package controllers

import (
	"errors"

	"github.com/astaxie/beego/logs"
	"github.com/garyburd/redigo/redis"

	"ai-eye/src/golang/lib/comm"
	"ai-eye/src/golang/lib/log"
	"ai-eye/src/golang/lib/rtmq"

	"ai-eye/src/golang/exec/msgsvr/controllers/conf"
)

/* MSGSVR上下文 */
type MsgSvrCntx struct {
	conf   *conf.MsgSvrConf /* 配置信息 */
	log    *logs.BeeLogger  /* 日志对象 */
	frwder *rtmq.Proxy      /* 代理对象 */
	redis  *redis.Pool      /* REDIS连接池 */
}

/******************************************************************************
 **函数名称: MsgSvrInit
 **功    能: 初始化对象
 **输入参数:
 **     conf: 配置信息
 **输出参数: NONE
 **返    回:
 **     ctx: 上下文
 **     err: 错误信息
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2016.10.30 22:32:23 #
 ******************************************************************************/
func MsgSvrInit(conf *conf.MsgSvrConf) (ctx *MsgSvrCntx, err error) {
	ctx = &MsgSvrCntx{}

	ctx.conf = conf

	/* > 初始化日志 */
	ctx.log = log.Init(conf.Log.Level, conf.Log.Path, "msgsvr.log")
	if nil == ctx.log {
		return nil, errors.New("Initialize log failed!")
	}

	/* > REDIS连接池 */
	ctx.redis = &redis.Pool{
		MaxIdle:   80,
		MaxActive: 12000,
		Dial: func() (redis.Conn, error) {
			c, err := redis.Dial("tcp", conf.Redis.Addr)
			if nil != err {
				panic(err.Error())
				return nil, err
			}
			if 0 != len(conf.Redis.Passwd) {
				if _, err := c.Do("AUTH", conf.Redis.Passwd); nil != err {
					c.Close()
					panic(err.Error())
					return nil, err
				}
			}
			return c, err
		},
	}
	if nil == ctx.redis {
		ctx.log.Error("Create redis pool failed! addr:%s passwd:%s",
			conf.Redis.Addr, conf.Redis.Passwd)
		return nil, errors.New("Create redis pool failed!")
	}

	/* > 初始化RTMQ-PROXY */
	ctx.frwder = rtmq.ProxyInit(&conf.Frwder, ctx.log)
	if nil == ctx.frwder {
		return nil, err
	}

	return ctx, nil
}

/******************************************************************************
 **函数名称: Register
 **功    能: 注册处理回调
 **输入参数: NONE
 **输出参数: NONE
 **返    回: VOID
 **实现描述: 注册回调函数
 **注意事项: 请在调用Launch()前完成此函数调用
 **作    者: # Qifeng.zou # 2016.10.30 22:32:23 #
 ******************************************************************************/
func (ctx *MsgSvrCntx) Register() {
	ctx.frwder.Register(comm.CMD_BROWSER_ENV, MsgSvrBrowserEnvHandler, ctx)
	ctx.frwder.Register(comm.CMD_EVENT_STATISTIC, MsgSvrEventStatisticHandler, ctx)
}

/******************************************************************************
 **函数名称: Launch
 **功    能: 启动OLSVR服务
 **输入参数: NONE
 **输出参数: NONE
 **返    回: VOID
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2016.10.30 22:32:23 #
 ******************************************************************************/
func (ctx *MsgSvrCntx) Launch() {
	go ctx.task()
	ctx.frwder.Launch()
}
