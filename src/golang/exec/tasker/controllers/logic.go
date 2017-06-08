package controllers

import (
	"fmt"
	"strconv"
	"strings"
	"time"

	"github.com/garyburd/redigo/redis"

	"login/src/golang/lib/comm"
	"login/src/golang/lib/crypt"
	"login/src/golang/lib/im"
)

/******************************************************************************
 **函数名称: timer_clean
 **功    能: 定时清理操作
 **输入参数: NONE
 **输出参数: NONE
 **返    回:
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2016.11.04 12:08:43 #
 ******************************************************************************/
func (ctx *TaskerCntx) timer_clean() {
	for {
		ctm := time.Now().Unix()

		ctx.clean_sid_zset(ctm)
		ctx.clean_token_zset(ctm)

		time.Sleep(30 * time.Second)
	}
	return
}

/******************************************************************************
 **函数名称: timer_update
 **功    能: 定时更新操作
 **输入参数: NONE
 **输出参数: NONE
 **返    回:
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2016.11.04 17:46:18 #
 ******************************************************************************/
func (ctx *TaskerCntx) timer_update() {
	for {
		ctx.update_prec_statis()

		time.Sleep(30 * time.Second)
	}
	return
}

////////////////////////////////////////////////////////////////////////////////

/******************************************************************************
 **函数名称: clean_sid_zset
 **功    能: 清理会话SID资源
 **输入参数:
 **输出参数: NONE
 **返    回:
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2016.11.04 12:08:43 #
 ******************************************************************************/
func (ctx *TaskerCntx) clean_sid_zset(ctm int64) {
	rds := ctx.redis.Get()
	defer rds.Close()

	off := 0
	for {
		sid_list, err := redis.Strings(rds.Do("ZRANGEBYSCORE",
			comm.AE_KEY_SID_ZSET, "-inf", ctm,
			"LIMIT", off, comm.AE_BAT_NUM))
		if nil != err {
			ctx.log.Error("Get sid list failed! errmsg:%s", err.Error())
			return
		}

		sid_num := len(sid_list)
		for idx := 0; idx < sid_num; idx += 1 {
			sid, _ := strconv.ParseInt(sid_list[idx], 10, 64)
			im.CleanSessionDataBySid(ctx.redis, uint32(sid))
		}

		if sid_num < comm.AE_BAT_NUM {
			break
		}
		off += comm.AE_BAT_NUM
	}
}

////////////////////////////////////////////////////////////////////////////////

/******************************************************************************
 **函数名称: online_token_decode
 **功    能: 解码TOKEN
 **输入参数:
 **     token: TOKEN字串
 **输出参数: NONE
 **返    回: 会话SID
 **实现描述: 解析token, 并提取有效数据.
 **注意事项:
 **     TOKEN的格式"sid:${sid}:ttl:${ttl}:end"
 **     sid: 会话SID
 **     ttl: 该token的最大生命时间
 **作    者: # Qifeng.zou # 2016.11.20 09:28:06 #
 ******************************************************************************/
func (ctx *TaskerCntx) online_token_decode(token string) uint32 {
	/* > TOKEN解码 */
	cry := crypt.CreateEncodeCtx(ctx.conf.Cipher)

	orig_token := crypt.Decode(cry, token)

	words := strings.Split(orig_token, ":")
	if 5 != len(words) {
		ctx.log.Error("Token format not right! token:%s orig:%s", token, orig_token)
		return 0
	}

	ctx.log.Debug("token:%s orig:%s", token, orig_token)

	/* > 验证TOKEN合法性 */
	sid, _ := strconv.ParseInt(words[1], 10, 32)
	ttl, _ := strconv.ParseInt(words[3], 10, 64)

	ctx.log.Debug("Parse token success! sid:%d ttl:%d", sid, ttl)

	return uint32(sid)
}

/******************************************************************************
 **函数名称: clean_token_zset
 **功    能: 清理会话TOKEN资源
 **输入参数:
 **输出参数: NONE
 **返    回:
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2017.05.08 10:43:59 #
 ******************************************************************************/
func (ctx *TaskerCntx) clean_token_zset(ctm int64) {
	rds := ctx.redis.Get()
	defer rds.Close()

	pl := ctx.redis.Get()
	defer func() {
		pl.Do("")
		pl.Close()
	}()

	off := 0
	for {
		token_list, err := redis.Strings(rds.Do("ZRANGEBYSCORE",
			comm.AE_KEY_TOKEN_ZSET, "-inf", ctm, "LIMIT", off, comm.AE_BAT_NUM))
		if nil != err {
			ctx.log.Error("Get token list failed! errmsg:%s", err.Error())
			return
		}

		token_num := len(token_list)
		for idx := 0; idx < token_num; idx += 1 {
			pl.Send("ZREM", comm.AE_KEY_TOKEN_ZSET, token_list[idx])
			pl.Send("HDEL", comm.AE_KEY_TOKEN_TO_SID, token_list[idx])

			/* 清理采集数据 */
			sid := ctx.online_token_decode(token_list[idx])

			key := fmt.Sprintf(comm.AE_KEY_SID_STATISTIC, sid)
			pl.Send("DEL", key)
		}

		if token_num < comm.AE_BAT_NUM {
			break
		}
		off += comm.AE_BAT_NUM
		pl.Do("")
	}
}

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

/******************************************************************************
 **函数名称: update_prec_statis
 **功    能: 更新各精度用户数
 **输入参数:
 **输出参数: NONE
 **返    回:
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2016.11.04 17:49:10 #
 ******************************************************************************/
func (ctx *TaskerCntx) update_prec_statis() {
	rds := ctx.redis.Get()
	defer rds.Close()

	pl := ctx.redis.Get()
	defer func() {
		pl.Do("")
		pl.Close()
	}()

	defer ctx.clean_prec_statis()

	/* > 获取当前并发数 */
	sid_num, err := redis.Int64(rds.Do("ZCARD", comm.AE_KEY_SID_ZSET))
	if nil != err {
		ctx.log.Error("Get sid num failed! errmsg:%s", err.Error())
		return
	}

	/* > 遍历统计精度列表 */
	prec_rnum_list, err := redis.Strings(rds.Do("ZRANGEBYSCORE",
		comm.AE_KEY_PREC_NUM_ZSET, 0, "+inf", "WITHSCORES"))
	if nil != err {
		ctx.log.Error("Get prec list failed! errmsg:%s", err.Error())
		return
	}

	ctm := uint64(time.Now().Unix())

	prec_num := len(prec_rnum_list)
	for idx := 0; idx < prec_num; idx += 2 {
		prec, _ := strconv.ParseInt(prec_rnum_list[idx], 10, 64)
		rnum, _ := strconv.ParseInt(prec_rnum_list[idx+1], 10, 64)
		if 0 == prec || 0 == rnum {
			continue
		}

		seg := (ctm / uint64(prec)) * uint64(prec)

		/* > 更新最大峰值 */
		key := fmt.Sprintf(comm.AE_KEY_PREC_USR_MAX_NUM, prec)
		has, err := redis.Bool(rds.Do("HEXISTS", key, seg))
		if nil != err {
			ctx.log.Error("Exec hexists failed! errmsg:%s", err.Error())
			break
		} else if false == has {
			pl.Send("HSET", key, seg, sid_num)
		}

		max, err := redis.Int64(rds.Do("HGET", key, seg))
		if nil != err {
			ctx.log.Error("Get max num failed! errmsg:%s", err.Error())
			continue
		} else if max <= sid_num {
			pl.Send("HSET", key, seg, sid_num)
		}

		/* > 更新最低峰值 */
		key = fmt.Sprintf(comm.AE_KEY_PREC_USR_MIN_NUM, prec)
		has, err = redis.Bool(rds.Do("HEXISTS", key, seg))
		if nil != err {
			ctx.log.Error("Exec hexists failed! errmsg:%s", err.Error())
			break
		} else if false == has {
			pl.Send("HSET", key, seg, sid_num)
		}

		min, err := redis.Int64(rds.Do("HGET", key, seg))
		if nil != err {
			ctx.log.Error("Get min num failed! errmsg:%s", err.Error())
			continue
		} else if min > sid_num {
			pl.Send("HSET", key, seg, sid_num)
		}
	}
}

/******************************************************************************
 **函数名称: clean_prec_statis
 **功    能: 删除各精度用户数
 **输入参数:
 **输出参数: NONE
 **返    回:
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2016.11.04 17:49:10 #
 ******************************************************************************/
func (ctx *TaskerCntx) clean_prec_statis() {
	rds := ctx.redis.Get()
	defer rds.Close()

	pl := ctx.redis.Get()
	defer func() {
		pl.Do("")
		pl.Close()
	}()

	ctm := time.Now().Unix()

	/* > 遍历统计精度列表 */
	prec_rnum_list, err := redis.Strings(rds.Do("ZRANGEBYSCORE",
		comm.AE_KEY_PREC_NUM_ZSET, 0, "+inf", "WITHSCORES"))
	if nil != err {
		ctx.log.Error("Get prec list failed! errmsg:%s", err.Error())
		return
	}

	prec_num := len(prec_rnum_list)
	for idx := 0; idx < prec_num; idx += 2 {
		prec, _ := strconv.ParseInt(prec_rnum_list[idx], 10, 64)
		rnum, _ := strconv.ParseInt(prec_rnum_list[idx+1], 10, 64)
		if 0 == prec || 0 == rnum {
			continue
		}

		seg := (ctm / prec) * prec

		/* > 清理最大峰值 */
		key := fmt.Sprintf(comm.AE_KEY_PREC_USR_MAX_NUM, prec)
		time_list, err := redis.Strings(rds.Do("HKEYS", key))
		if nil == err {
			time_num := len(time_list)
			for idx := 0; idx < time_num; idx += 1 {
				tm, _ := strconv.ParseInt(time_list[idx], 10, 64)
				intval_num := (seg - tm) / prec
				if intval_num > rnum {
					pl.Send("HDEL", key, tm)
				}
			}
		}

		/* > 清理最低峰值 */
		key = fmt.Sprintf(comm.AE_KEY_PREC_USR_MIN_NUM, prec)
		time_list, err = redis.Strings(rds.Do("HKEYS", key))
		if nil == err {
			time_num := len(time_list)
			for idx := 0; idx < time_num; idx += 1 {
				tm, _ := strconv.ParseInt(time_list[idx], 10, 64)
				intval_num := (seg - tm) / prec
				if intval_num > rnum {
					pl.Send("HDEL", key, tm)
				}
			}
		}
	}
}
