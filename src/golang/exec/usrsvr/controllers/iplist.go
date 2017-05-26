package controllers

import (
	"errors"
	"fmt"
	"math/rand"
	"time"

	"ai-eye/src/golang/lib/comm"
	"ai-eye/src/golang/lib/crypt"
	"ai-eye/src/golang/lib/im"
)

type UsrSvrIplistCtrl struct {
	BaseController
}

func (this *UsrSvrIplistCtrl) Iplist() {
	ctx := GetUsrSvrCtx()

	this.iplist_query(ctx)
}

////////////////////////////////////////////////////////////////////////////////

/* 注册参数 */
type IpListParam struct {
	typ      int    // 网络类型(0:Unknown 1:TCP 2:WS)
	clientip string // 客户端IP
}

/* IP列表应答 */
type IpListRsp struct {
	Sid    uint32   `json:"sid"`    // 会话ID
	Type   int      `json:"type"`   // 网络类型(0:Unknown 1:TCP 2:WS)
	Token  string   `json:"token"`  // 鉴权TOKEN
	Expire int      `json:"expire"` // 过期时长
	Len    int      `json:"len"`    // 列表长度
	List   []string `json:"list"`   // IP列表
	Code   int      `json:"code"`   // 错误码
	ErrMsg string   `json:"errmsg"` // 错误描述
}

func (this *UsrSvrIplistCtrl) iplist_query(ctx *UsrSvrCntx) {
	/* > 提取注册参数 */
	param, err := this.iplist_param_parse(ctx)
	if nil != err {
		ctx.log.Error("Parse param failed! clientip:%s", param.clientip)
		this.Error(comm.ERR_SVR_PARSE_PARAM, err.Error())
		return
	}

	/* > 申请会话SID */
	sid, err := im.AllocSid(ctx.redis)
	if nil != err {
		ctx.log.Error("Alloc sid failed! clientip:%s", param.clientip)
		this.Error(comm.ERR_SVR_PARSE_PARAM, err.Error())
		return
	}

	ctx.log.Debug("Param list. type:%d sid:%d clientip:%s", param.typ, sid, param.clientip)

	/* > 获取IP列表 */
	this.iplist_handler(ctx, sid, param)

	return
}

/******************************************************************************
 **函数名称: iplist_param_parse
 **功    能: 解析参数
 **输入参数:
 **     ctx: 上下文
 **输出参数: NONE
 **返    回:
 **     param: 注册参数
 **     err: 错误描述
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2016.11.25 23:17:52 #
 ******************************************************************************/
func (this *UsrSvrIplistCtrl) iplist_param_parse(ctx *UsrSvrCntx) (*IpListParam, error) {
	param := &IpListParam{}

	/* > 提取注册参数 */
	param.typ, _ = this.GetInt("type")
	if 0 == param.typ {
		ctx.log.Error("Type is invalid.")
		return param, errors.New("Type is invalid!")
	}

	param.clientip = this.GetString("clientip")
	if "" == param.clientip {
		ctx.log.Error("Client ip is invalid.")
		return param, errors.New("Client ip is invalid!")
	}

	ctx.log.Debug("Get ip list param. type:%d clientip:%s",
		param.typ, param.clientip)

	return param, nil
}

/******************************************************************************
 **函数名称: iplist_handler
 **功    能: 获取IP列表
 **输入参数:
 **     ctx: 上下文
 **     param: URL参数
 **输出参数:
 **返    回: NONE
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2016.11.24 17:00:07 #
 ******************************************************************************/
func (this *UsrSvrIplistCtrl) iplist_handler(ctx *UsrSvrCntx, sid uint32, param *IpListParam) {
	iplist := this.iplist_get(ctx, param.typ, param.clientip)
	if nil == iplist {
		ctx.log.Error("Get ip list failed!")
		this.Error(comm.ERR_SYS_SYSTEM, "Get ip list failed!")
		return
	}

	this.success(sid, param, iplist)

	return
}

/******************************************************************************
 **函数名称: success
 **功    能: 应答处理成功
 **输入参数:
 **     param: 注册参数
 **     iplist: IP列表
 **输出参数:
 **返    回: NONE
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2016.11.25 23:13:02 #
 ******************************************************************************/
func (this *UsrSvrIplistCtrl) success(sid uint32, param *IpListParam, iplist []string) {
	var resp IpListRsp

	resp.Sid = sid
	resp.Type = param.typ
	resp.Token = this.iplist_token(sid)
	resp.Expire = comm.TIME_DAY
	resp.Len = len(iplist)
	resp.List = iplist
	resp.Code = 0
	resp.ErrMsg = "OK"

	this.Data["json"] = &resp
	this.ServeJSON()
}

/******************************************************************************
 **函数名称: iplist_token
 **功    能: 生成TOKEN字串
 **输入参数:
 **输出参数: NONE
 **返    回:
 **     token: 加密TOKEN
 **     expire: 过期时间
 **实现描述:
 **注意事项:
 **     TOKEN的格式"sid:${sid}:ttl:${ttl}:end"
 **     sid: 会话SID
 **     ttl: 该token的最大生命时间
 **作    者: # Qifeng.zou # 2016.11.25 23:54:27 #
 ******************************************************************************/
func (this *UsrSvrIplistCtrl) iplist_token(sid uint32) string {
	ctx := GetUsrSvrCtx()
	ttl := time.Now().Unix() + comm.TIME_YEAR

	/* > 原始TOKEN */
	token := fmt.Sprintf("sid:%d:ttl:%d:end", sid, ttl)

	/* > 加密TOKEN */
	cry := crypt.CreateEncodeCtx(ctx.conf.Cipher)

	return crypt.Encode(cry, token)
}

/******************************************************************************
 **函数名称: iplist_get
 **功    能: 获取IP列表
 **输入参数:
 **     ctx: 上下文
 **     typ: 网络类型(0:Unknown 1:TCP 2:WS)
 **     clientip: 客户端IP
 **输出参数: NONE
 **返    回: IP列表
 **实现描述: 首先根据网络类型, 再根据运营商类型筛选.
 **注意事项: 加读锁
 **作    者: # Qifeng.zou # 2016.11.27 07:42:54 #
 ******************************************************************************/
func (this *UsrSvrIplistCtrl) iplist_get(ctx *UsrSvrCntx, typ int, clientip string) []string {
	ctx.listend.RLock()
	defer ctx.listend.RUnlock()

	listend, ok := ctx.listend.types[typ]
	if !ok || 0 == typ {
		return nil
	}

	item := ctx.ipdict.Query(clientip)
	if nil == item {
		listend.RLock()
		defer listend.RUnlock()
		return listend.get_default(ctx)
	}

	listend.RLock()
	defer listend.RUnlock()

	/* > 获取国家/地区下辖的运营商列表 */
	operators, ok := listend.list[item.GetNation()]
	if nil == operators || !ok {
		return listend.get_default(ctx)
	}

	/* > 获取运营商下辖的侦听层列表 */
	list, ok := operators[item.GetOpid()]
	if nil == list || !ok {
		return listend.get_default(ctx)
	}

	items := make([]string, 0)
	items = append(items, list[rand.Intn(len(list))])

	return items
}

/******************************************************************************
 **函数名称: get_default
 **功    能: 获取默认IP列表
 **输入参数:
 **     ctx: 上下文
 **     typ: 网络类型(0:Unknown 1:TCP 2:WS)
 **输出参数: NONE
 **返    回: IP列表
 **实现描述:
 **注意事项: 外部已经加读锁
 **作    者: # Qifeng.zou # 2016.11.27 19:33:49 #
 ******************************************************************************/
func (listend *UsrSvrLsndList) get_default(ctx *UsrSvrCntx) []string {
	var ok bool
	var typ, n uint32

	/* > 获取"默认"国家/地区下辖的运营商ID列表 */
	operators, ok := listend.list["CN"]
	if nil == operators || 0 == len(operators) || !ok {
		ctx.log.Error("Get default iplist by nation failed!")
		return nil
	}

	idx := rand.Intn(len(operators)) % len(operators)

	n = 0
	for k, v := range operators {
		if n == uint32(idx) {
			typ = k
			break
		}
		ctx.log.Debug("k:%d v:%s", k, v)
	}

	/* > 获取"默认"运营商下辖的侦听层列表 */
	list, ok := operators[typ]
	if nil == list || 0 == len(list) || !ok {
		ctx.log.Error("Get default iplist by operator failed!")
		return nil
	}

	items := make([]string, 0)
	items = append(items, list[rand.Intn(len(list))])

	return items
}

////////////////////////////////////////////////////////////////////////////////
