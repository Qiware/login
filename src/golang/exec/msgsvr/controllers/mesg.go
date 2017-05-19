package controllers

import (
	"errors"
	"fmt"
	"time"

	"ai-eye/src/golang/lib/comm"
	"ai-eye/src/golang/lib/mesg"

	"github.com/golang/protobuf/proto"
)

////////////////////////////////////////////////////////////////////////////////
// 浏览器环境

/******************************************************************************
 **函数名称: browser_env_parse
 **功    能: 解析浏览器环境信息
 **输入参数:
 **     data: 接收的数据
 **输出参数: NONE
 **返    回:
 **     head: 通用协议头
 **     req: 协议体内容
 **     code: 错误码
 **     err: 错误描述
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2016.10.30 22:32:23 #
 ******************************************************************************/
func (ctx *MsgSvrCntx) browser_env_parse(data []byte) (
	head *comm.MesgHeader, req *mesg.MesgBrowserEnv, code uint32, err error) {
	/* > 字节序转换 */
	head = comm.MesgHeadNtoh(data)
	if !head.IsValid(1) {
		errmsg := "Browser-env head is invalid!"
		ctx.log.Error("Header is invalid! cmd:0x%04X nid:%d",
			head.GetCmd(), head.GetNid())
		return nil, nil, comm.ERR_SVR_HEAD_INVALID, errors.New(errmsg)
	}

	ctx.log.Debug("Browser-env header! cmd:0x%04X length:%d sid:%d cid:%d nid:%d seq:%d",
		head.GetCmd(), head.GetLength(),
		head.GetSid(), head.GetCid(), head.GetNid(), head.GetSeq())

	/* > 解析PB协议 */
	req = &mesg.MesgBrowserEnv{}

	err = proto.Unmarshal(data[comm.MESG_HEAD_SIZE:], req)
	if nil != err {
		ctx.log.Error("Unmarshal body failed! errmsg:%s", err.Error())
		return head, nil, comm.ERR_SVR_BODY_INVALID, errors.New("Unmarshal body failed!")
	}

	return head, req, 0, nil
}

/******************************************************************************
 **函数名称: browser_env_failed
 **功    能: 发送浏览器环境应答
 **输入参数:
 **     head: 协议头
 **     req: 浏览器环境信息
 **     code: 错误码
 **     errmsg: 错误描述
 **输出参数: NONE
 **返    回: VOID
 **实现描述:
 **应答协议:
 ** {
 **     optional uint32 code = 1;       // M|错误码|数字|
 **     optional string errmsg = 2;     // M|错误描述|字串|
 ** }
 **注意事项:
 **作    者: # Qifeng.zou # 2017.05.18 10:02:34 #
 ******************************************************************************/
func (ctx *MsgSvrCntx) browser_env_failed(head *comm.MesgHeader,
	req *mesg.MesgBrowserEnv, code uint32, errmsg string) int {
	if nil == head {
		return -1
	}

	/* > 设置协议体 */
	ack := &mesg.MesgBrowserEnvAck{
		Code:   proto.Uint32(code),
		Errmsg: proto.String(errmsg),
	}

	/* 生成PB数据 */
	body, err := proto.Marshal(ack)
	if nil != err {
		ctx.log.Error("Marshal protobuf failed! errmsg:%s", err.Error())
		return -1
	}

	length := len(body)

	/* > 拼接协议包 */
	p := &comm.MesgPacket{}
	p.Buff = make([]byte, comm.MESG_HEAD_SIZE+length)

	head.Cmd = comm.CMD_BROWSER_ENV_ACK
	head.Length = uint32(length)

	comm.MesgHeadHton(head, p)
	copy(p.Buff[comm.MESG_HEAD_SIZE:], body)

	/* > 发送协议包 */
	ctx.frwder.AsyncSend(comm.CMD_BROWSER_ENV_ACK, p.Buff, uint32(len(p.Buff)))

	ctx.log.Debug("Send browser-env ack succ!")

	return 0
}

/******************************************************************************
 **函数名称: browser_env_ack
 **功    能: 发送上线应答
 **输入参数:
 **输出参数: NONE
 **返    回: VOID
 **实现描述:
 ** {
 **     required uint64 sid = 1;        // M|会话ID|数字|内部使用
 **     optional uint32 code = 2;       // M|错误码|数字|
 **     optional string errmsg = 3;     // M|错误描述|字串|
 ** }
 **注意事项:
 **作    者: # Qifeng.zou # 2016.11.01 18:37:59 #
 ******************************************************************************/
func (ctx *MsgSvrCntx) browser_env_ack(head *comm.MesgHeader, req *mesg.MesgBrowserEnv) int {
	/* > 设置协议体 */
	ack := &mesg.MesgBrowserEnvAck{
		Code:   proto.Uint32(0),
		Errmsg: proto.String("Ok"),
	}

	/* 生成PB数据 */
	body, err := proto.Marshal(ack)
	if nil != err {
		ctx.log.Error("Marshal protobuf failed! errmsg:%s", err.Error())
		return -1
	}

	length := len(body)

	/* > 拼接协议包 */
	p := &comm.MesgPacket{}
	p.Buff = make([]byte, comm.MESG_HEAD_SIZE+length)

	head.Cmd = comm.CMD_BROWSER_ENV_ACK
	head.Length = uint32(length)

	comm.MesgHeadHton(head, p)
	copy(p.Buff[comm.MESG_HEAD_SIZE:], body)

	/* > 发送协议包 */
	ctx.frwder.AsyncSend(comm.CMD_BROWSER_ENV_ACK, p.Buff, uint32(len(p.Buff)))

	ctx.log.Debug("Send browser-env ack success!")

	return 0
}

/******************************************************************************
 **函数名称: browser_env_handler
 **功    能: 浏览器环境处理
 **输入参数:
 **     head: 协议头
 **     req: 浏览器环境信息
 **输出参数: NONE
 **返    回: 异常信息
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2017.05.18 09:51:50 #
 ******************************************************************************/
func (ctx *MsgSvrCntx) browser_env_handler(head *comm.MesgHeader, req *mesg.MesgBrowserEnv) (err error) {
	pl := ctx.redis.Get()
	defer func() {
		pl.Do("")
		pl.Close()
	}()

	ttl := time.Now().Unix() + comm.AE_SID_TTL

	/* 记录SID集合 */
	pl.Send("ZADD", comm.AE_KEY_SID_ZSET, ttl, head.GetSid())

	/* 记录浏览器环境 */
	key := fmt.Sprintf(comm.AE_KEY_SID_STATISTIC, head.GetSid())
	/* > 插件信息 */
	plugin := req.GetPlugin()
	if nil != plugin {
		if len(plugin.GetName()) > 0 {
			pl.Send("HSET", key, comm.COL_PLUGIN_HAS_NAME, 1)
		}

		if len(plugin.GetDesc()) > 0 {
			pl.Send("HSET", key, comm.COL_PLUGIN_HAS_DESC, 1)
		}
	}

	/* > 用户代理 */
	ua := req.GetUa()
	if nil != ua {
		if len(ua.GetUa()) > 0 {
			pl.Send("HSET", key, comm.COL_UA_EXISTS, 1)
		}
	}

	/* > 屏幕信息 */
	screen := req.GetScreen()
	if nil != screen {
		pl.Send("HMSET", key, comm.COL_SCREEN_WIDTH, screen.GetWidth(),
			comm.COL_SCREEN_HEIGH, screen.GetHeight(),
			comm.COL_SCREEN_AVAIL_WIDTH, screen.GetAvailWidth(),
			comm.COL_SCREEN_AVAIL_HEIGH, screen.GetAvailHeight(),
			comm.COL_SCREEN_AVAIL_LEFT, screen.GetAvailLeft(),
			comm.COL_SCREEN_AVAIL_TOP, screen.GetAvailTop(),
			comm.COL_SCREEN_OUTER_WIDTH, screen.GetOuterWidth(),
			comm.COL_SCREEN_OUTER_HEIGH, screen.GetOuterHeight(),
			comm.COL_SCREEN_INNER_WIDTH, screen.GetInnerWidth(),
			comm.COL_SCREEN_INNER_HEIGH, screen.GetInnerHeight())
	}

	/* > 更新时间信息
	 *   CTM: 创建时间
	 *   UTM: 更新时间 */
	pl.Send("HMSET", key, "CTM", time.Now().Unix(), "UTM", time.Now().Unix())

	return err
}

/******************************************************************************
 **函数名称: MsgSvrBrowserEnvHandler
 **功    能: 浏览器环境上报信息处理
 **输入参数:
 **     cmd: 消息类型
 **     nid: 结点ID
 **     data: 收到数据
 **     length: 数据长度
 **     param: 附加参数
 **输出参数: NONE
 **返    回: VOID
 **实现描述:
 **请求协议:
 **注意事项:
 **作    者: # Qifeng.zou # 2017.05.18 09:41:31 #
 ******************************************************************************/
func MsgSvrBrowserEnvHandler(cmd uint32, nid uint32, data []byte, length uint32, param interface{}) int {
	ctx, ok := param.(*MsgSvrCntx)
	if !ok {
		return -1
	}

	ctx.log.Debug("Recv browser-env data! cmd:0x%04X nid:%d length:%d", cmd, nid, length)

	/* > 解析上线请求 */
	head, req, code, err := ctx.browser_env_parse(data)
	if nil != err {
		ctx.log.Error("Parse browser-env failed! errmsg:%s", err.Error())
		ctx.browser_env_failed(head, req, code, err.Error())
		return -1
	}

	/* > 初始化上线环境 */
	err = ctx.browser_env_handler(head, req)
	if nil != err {
		ctx.log.Error("Browser-env handler failed!")
		ctx.browser_env_failed(head, req, comm.ERR_SYS_SYSTEM, err.Error())
		return -1
	}

	/* > 发送上线应答 */
	ctx.browser_env_ack(head, req)

	return 0
}

////////////////////////////////////////////////////////////////////////////////
// 事件统计

/******************************************************************************
 **函数名称: event_statistic_parse
 **功    能: 事件统计信息
 **输入参数:
 **     data: 接收的数据
 **输出参数: NONE
 **返    回:
 **     head: 通用协议头
 **     req: 协议体内容
 **     code: 错误码
 **     err: 错误描述
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2016.10.30 22:32:23 #
 ******************************************************************************/
func (ctx *MsgSvrCntx) event_statistic_parse(data []byte) (
	head *comm.MesgHeader, req *mesg.MesgEventStatistic, code uint32, err error) {
	/* > 字节序转换 */
	head = comm.MesgHeadNtoh(data)
	if !head.IsValid(1) {
		errmsg := "Event-statistic head is invalid!"
		ctx.log.Error("Header is invalid! cmd:0x%04X nid:%d",
			head.GetCmd(), head.GetNid())
		return nil, nil, comm.ERR_SVR_HEAD_INVALID, errors.New(errmsg)
	}

	ctx.log.Debug("Event-statistic header! cmd:0x%04X length:%d sid:%d cid:%d nid:%d seq:%d",
		head.GetCmd(), head.GetLength(),
		head.GetSid(), head.GetCid(), head.GetNid(), head.GetSeq())

	/* > 解析PB协议 */
	req = &mesg.MesgEventStatistic{}

	err = proto.Unmarshal(data[comm.MESG_HEAD_SIZE:], req)
	if nil != err {
		ctx.log.Error("Unmarshal body failed! errmsg:%s", err.Error())
		return head, nil, comm.ERR_SVR_BODY_INVALID, errors.New("Unmarshal body failed!")
	}

	return head, req, 0, nil
}

/******************************************************************************
 **函数名称: event_statistic_failed
 **功    能: 事件统计失败
 **输入参数:
 **     head: 协议头
 **     req: 事件统计
 **     code: 错误码
 **     errmsg: 错误描述
 **输出参数: NONE
 **返    回: VOID
 **实现描述:
 **应答协议:
 ** {
 **     optional uint32 code = 1;       // M|错误码|数字|
 **     optional string errmsg = 2;     // M|错误描述|字串|
 ** }
 **注意事项:
 **作    者: # Qifeng.zou # 2017.05.18 10:02:34 #
 ******************************************************************************/
func (ctx *MsgSvrCntx) event_statistic_failed(head *comm.MesgHeader,
	req *mesg.MesgEventStatistic, code uint32, errmsg string) int {
	if nil == head {
		return -1
	}

	/* > 设置协议体 */
	ack := &mesg.MesgEventStatisticAck{
		Code:   proto.Uint32(code),
		Errmsg: proto.String(errmsg),
	}

	/* 生成PB数据 */
	body, err := proto.Marshal(ack)
	if nil != err {
		ctx.log.Error("Marshal protobuf failed! errmsg:%s", err.Error())
		return -1
	}

	length := len(body)

	/* > 拼接协议包 */
	p := &comm.MesgPacket{}
	p.Buff = make([]byte, comm.MESG_HEAD_SIZE+length)

	head.Cmd = comm.CMD_EVENT_STATISTIC_ACK
	head.Length = uint32(length)

	comm.MesgHeadHton(head, p)
	copy(p.Buff[comm.MESG_HEAD_SIZE:], body)

	/* > 发送协议包 */
	ctx.frwder.AsyncSend(comm.CMD_EVENT_STATISTIC_ACK, p.Buff, uint32(len(p.Buff)))

	ctx.log.Debug("Send event-statistic ack succ!")

	return 0
}

/******************************************************************************
 **函数名称: event_statistic_ack
 **功    能: 事件统计应答
 **输入参数:
 **输出参数: NONE
 **返    回: VOID
 **实现描述:
 ** {
 **     optional uint32 code = 2;       // M|错误码|数字|
 **     optional string errmsg = 3;     // M|错误描述|字串|
 ** }
 **注意事项:
 **作    者: # Qifeng.zou # 2017.05.18 16:32:35 #
 ******************************************************************************/
func (ctx *MsgSvrCntx) event_statistic_ack(head *comm.MesgHeader, req *mesg.MesgBrowserEnv) int {
	/* > 设置协议体 */
	ack := &mesg.MesgEventStatisticAck{
		Code:   proto.Uint32(0),
		Errmsg: proto.String("Ok"),
	}

	/* 生成PB数据 */
	body, err := proto.Marshal(ack)
	if nil != err {
		ctx.log.Error("Marshal protobuf failed! errmsg:%s", err.Error())
		return -1
	}

	length := len(body)

	/* > 拼接协议包 */
	p := &comm.MesgPacket{}
	p.Buff = make([]byte, comm.MESG_HEAD_SIZE+length)

	head.Cmd = comm.CMD_EVENT_STATISTIC_ACK
	head.Length = uint32(length)

	comm.MesgHeadHton(head, p)
	copy(p.Buff[comm.MESG_HEAD_SIZE:], body)

	/* > 发送协议包 */
	ctx.frwder.AsyncSend(comm.CMD_EVENT_STATISTIC_ACK, p.Buff, uint32(len(p.Buff)))

	ctx.log.Debug("Send event-statistic ack success!")

	return 0
}

/******************************************************************************
 **函数名称: event_statistic_handler
 **功    能: 事件统计处理
 **输入参数:
 **     head: 协议头
 **     req: 事件统计信息
 **输出参数: NONE
 **返    回: 异常信息
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2017.05.18 16:33:41 #
 ******************************************************************************/
func (ctx *MsgSvrCntx) event_statistic_handler(
	head *comm.MesgHeader, req *mesg.MesgEventStatistic) (err error) {
	pl := ctx.redis.Get()
	defer func() {
		pl.Do("")
		pl.Close()
	}()

	ttl := time.Now().Unix() + comm.AE_SID_TTL

	/* 记录SID集合 */
	pl.Send("ZADD", comm.AE_KEY_SID_ZSET, ttl, head.GetSid())

	/* > 插件信息 */
	key := fmt.Sprintf(comm.AE_KEY_SID_STATISTIC, head.GetSid())

	switch req.GetCtrl() {
	case comm.CTL_IBX_USR: // 输入框: 用户名
		switch req.GetEvent() {
		case comm.EV_CHANGE:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_USR_CHANGE, req.GetCount())
		case comm.EV_CLICK:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_USR_CLICK, req.GetCount())
		case comm.EV_DBLCLICK:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_USR_DBLCLICK, req.GetCount())
		case comm.EV_FOCUS:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_USR_FOCUS, req.GetCount())
		case comm.EV_KEYDOWN:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_USR_KEYDOWN, req.GetCount())
		case comm.EV_KEYPRESS:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_USR_KEYPRESS, req.GetCount())
		case comm.EV_KEYUP:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_USR_KEYUP, req.GetCount())
		case comm.EV_MOUSEDOWN:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_USR_MOUSEDOWN, req.GetCount())
		case comm.EV_MOUSEMOVE:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_USR_MOUSEMOVE, req.GetCount())
		case comm.EV_MOUSEOUT:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_USR_MOUSEOUT, req.GetCount())
		case comm.EV_MOUSEOVER:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_USR_MOUSEOVER, req.GetCount())
		case comm.EV_MOUSEUP:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_USR_MOUSEUP, req.GetCount())
		case comm.EV_TOUCHSTART:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_USR_TOUCHSTART, req.GetCount())
		case comm.EV_TOUCHMOVE:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_USR_TOUCHMOVE, req.GetCount())
		case comm.EV_TOUCHEND:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_USR_TOUCHEND, req.GetCount())
		case comm.EV_TOUCHCANCEL:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_USR_TOUCHCANCEL, req.GetCount())
		}
	case comm.CTL_IBX_PWD: // 输入框: 密码
		switch req.GetEvent() {
		case comm.EV_CHANGE:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_PWD_CHANGE, req.GetCount())
		case comm.EV_CLICK:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_PWD_CLICK, req.GetCount())
		case comm.EV_DBLCLICK:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_PWD_DBLCLICK, req.GetCount())
		case comm.EV_FOCUS:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_PWD_FOCUS, req.GetCount())
		case comm.EV_KEYDOWN:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_PWD_KEYDOWN, req.GetCount())
		case comm.EV_KEYPRESS:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_PWD_KEYPRESS, req.GetCount())
		case comm.EV_KEYUP:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_PWD_KEYUP, req.GetCount())
		case comm.EV_MOUSEDOWN:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_PWD_MOUSEDOWN, req.GetCount())
		case comm.EV_MOUSEMOVE:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_PWD_MOUSEMOVE, req.GetCount())
		case comm.EV_MOUSEOUT:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_PWD_MOUSEOUT, req.GetCount())
		case comm.EV_MOUSEOVER:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_PWD_MOUSEOVER, req.GetCount())
		case comm.EV_MOUSEUP:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_PWD_MOUSEUP, req.GetCount())
		case comm.EV_TOUCHSTART:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_PWD_TOUCHSTART, req.GetCount())
		case comm.EV_TOUCHMOVE:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_PWD_TOUCHMOVE, req.GetCount())
		case comm.EV_TOUCHEND:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_PWD_TOUCHEND, req.GetCount())
		case comm.EV_TOUCHCANCEL:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_PWD_TOUCHCANCEL, req.GetCount())
		}
	case comm.CTL_IBX_IMG: // 输入框: 图片验证码
		switch req.GetEvent() {
		case comm.EV_CHANGE:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_IMG_CHANGE, req.GetCount())
		case comm.EV_CLICK:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_IMG_CLICK, req.GetCount())
		case comm.EV_DBLCLICK:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_IMG_DBLCLICK, req.GetCount())
		case comm.EV_FOCUS:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_IMG_FOCUS, req.GetCount())
		case comm.EV_KEYDOWN:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_IMG_KEYDOWN, req.GetCount())
		case comm.EV_KEYPRESS:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_IMG_KEYPRESS, req.GetCount())
		case comm.EV_KEYUP:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_IMG_KEYUP, req.GetCount())
		case comm.EV_MOUSEDOWN:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_IMG_MOUSEDOWN, req.GetCount())
		case comm.EV_MOUSEMOVE:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_IMG_MOUSEMOVE, req.GetCount())
		case comm.EV_MOUSEOUT:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_IMG_MOUSEOUT, req.GetCount())
		case comm.EV_MOUSEOVER:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_IMG_MOUSEOVER, req.GetCount())
		case comm.EV_MOUSEUP:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_IMG_MOUSEUP, req.GetCount())
		case comm.EV_TOUCHSTART:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_IMG_TOUCHSTART, req.GetCount())
		case comm.EV_TOUCHMOVE:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_IMG_TOUCHMOVE, req.GetCount())
		case comm.EV_TOUCHEND:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_IMG_TOUCHEND, req.GetCount())
		case comm.EV_TOUCHCANCEL:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_IMG_TOUCHCANCEL, req.GetCount())
		}
	case comm.CTL_BTN_IMG: // 按钮: 图片验证码
		switch req.GetEvent() {
		case comm.EV_CLICK:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_IMG_CLICK, req.GetCount())
		case comm.EV_DBLCLICK:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_IMG_DBLCLICK, req.GetCount())
		case comm.EV_FOCUS:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_IMG_FOCUS, req.GetCount())
		case comm.EV_KEYDOWN:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_IMG_KEYDOWN, req.GetCount())
		case comm.EV_KEYPRESS:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_IMG_KEYPRESS, req.GetCount())
		case comm.EV_KEYUP:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_IMG_KEYUP, req.GetCount())
		case comm.EV_MOUSEDOWN:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_IMG_MOUSEDOWN, req.GetCount())
		case comm.EV_MOUSEMOVE:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_IMG_MOUSEMOVE, req.GetCount())
		case comm.EV_MOUSEOUT:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_IMG_MOUSEOUT, req.GetCount())
		case comm.EV_MOUSEOVER:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_IMG_MOUSEOVER, req.GetCount())
		case comm.EV_MOUSEUP:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_IMG_MOUSEUP, req.GetCount())
		case comm.EV_TOUCHSTART:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_IMG_TOUCHSTART, req.GetCount())
		case comm.EV_TOUCHMOVE:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_IMG_TOUCHMOVE, req.GetCount())
		case comm.EV_TOUCHEND:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_IMG_TOUCHEND, req.GetCount())
		case comm.EV_TOUCHCANCEL:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_IMG_TOUCHCANCEL, req.GetCount())
		}
	case comm.CTL_IBX_TEL: // 输入框: 手机号
		switch req.GetEvent() {
		case comm.EV_CHANGE:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_TEL_CHANGE, req.GetCount())
		case comm.EV_CLICK:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_TEL_CLICK, req.GetCount())
		case comm.EV_DBLCLICK:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_TEL_DBLCLICK, req.GetCount())
		case comm.EV_FOCUS:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_TEL_FOCUS, req.GetCount())
		case comm.EV_KEYDOWN:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_TEL_KEYDOWN, req.GetCount())
		case comm.EV_KEYPRESS:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_TEL_KEYPRESS, req.GetCount())
		case comm.EV_KEYUP:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_TEL_KEYUP, req.GetCount())
		case comm.EV_MOUSEDOWN:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_TEL_MOUSEDOWN, req.GetCount())
		case comm.EV_MOUSEMOVE:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_TEL_MOUSEMOVE, req.GetCount())
		case comm.EV_MOUSEOUT:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_TEL_MOUSEOUT, req.GetCount())
		case comm.EV_MOUSEOVER:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_TEL_MOUSEOVER, req.GetCount())
		case comm.EV_MOUSEUP:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_TEL_MOUSEUP, req.GetCount())
		case comm.EV_TOUCHSTART:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_TEL_TOUCHSTART, req.GetCount())
		case comm.EV_TOUCHMOVE:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_TEL_TOUCHMOVE, req.GetCount())
		case comm.EV_TOUCHEND:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_TEL_TOUCHEND, req.GetCount())
		case comm.EV_TOUCHCANCEL:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_TEL_TOUCHCANCEL, req.GetCount())
		}
	case comm.CTL_IBX_SMS: // 输入框: 短信验证码
		switch req.GetEvent() {
		case comm.EV_CHANGE:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_SMS_CHANGE, req.GetCount())
		case comm.EV_CLICK:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_SMS_CLICK, req.GetCount())
		case comm.EV_DBLCLICK:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_SMS_DBLCLICK, req.GetCount())
		case comm.EV_FOCUS:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_SMS_FOCUS, req.GetCount())
		case comm.EV_KEYDOWN:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_SMS_KEYDOWN, req.GetCount())
		case comm.EV_KEYPRESS:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_SMS_KEYPRESS, req.GetCount())
		case comm.EV_KEYUP:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_SMS_KEYUP, req.GetCount())
		case comm.EV_MOUSEDOWN:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_SMS_MOUSEDOWN, req.GetCount())
		case comm.EV_MOUSEMOVE:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_SMS_MOUSEMOVE, req.GetCount())
		case comm.EV_MOUSEOUT:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_SMS_MOUSEOUT, req.GetCount())
		case comm.EV_MOUSEOVER:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_SMS_MOUSEOVER, req.GetCount())
		case comm.EV_MOUSEUP:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_SMS_MOUSEUP, req.GetCount())
		case comm.EV_TOUCHSTART:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_SMS_TOUCHSTART, req.GetCount())
		case comm.EV_TOUCHMOVE:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_SMS_TOUCHMOVE, req.GetCount())
		case comm.EV_TOUCHEND:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_SMS_TOUCHEND, req.GetCount())
		case comm.EV_TOUCHCANCEL:
			pl.Send("HINCRBY", key, comm.COL_EVENT_IBX_SMS_TOUCHCANCEL, req.GetCount())
		}
	case comm.CTL_BTN_SMS: // 按钮: 短信验证码
		switch req.GetEvent() {
		case comm.EV_CLICK:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_SMS_CLICK, req.GetCount())
		case comm.EV_DBLCLICK:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_SMS_DBLCLICK, req.GetCount())
		case comm.EV_FOCUS:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_SMS_FOCUS, req.GetCount())
		case comm.EV_KEYDOWN:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_SMS_KEYDOWN, req.GetCount())
		case comm.EV_KEYPRESS:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_SMS_KEYPRESS, req.GetCount())
		case comm.EV_KEYUP:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_SMS_KEYUP, req.GetCount())
		case comm.EV_MOUSEDOWN:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_SMS_MOUSEDOWN, req.GetCount())
		case comm.EV_MOUSEMOVE:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_SMS_MOUSEMOVE, req.GetCount())
		case comm.EV_MOUSEOUT:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_SMS_MOUSEOUT, req.GetCount())
		case comm.EV_MOUSEOVER:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_SMS_MOUSEOVER, req.GetCount())
		case comm.EV_MOUSEUP:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_SMS_MOUSEUP, req.GetCount())
		case comm.EV_TOUCHSTART:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_SMS_TOUCHSTART, req.GetCount())
		case comm.EV_TOUCHMOVE:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_SMS_TOUCHMOVE, req.GetCount())
		case comm.EV_TOUCHEND:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_SMS_TOUCHEND, req.GetCount())
		case comm.EV_TOUCHCANCEL:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_SMS_TOUCHCANCEL, req.GetCount())
		}
	case comm.CTL_BTN_LGN: // 按钮: 登录
		switch req.GetEvent() {
		case comm.EV_CLICK:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_LGN_CLICK, req.GetCount())
		case comm.EV_DBLCLICK:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_LGN_DBLCLICK, req.GetCount())
		case comm.EV_FOCUS:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_LGN_FOCUS, req.GetCount())
		case comm.EV_KEYDOWN:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_LGN_KEYDOWN, req.GetCount())
		case comm.EV_KEYPRESS:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_LGN_KEYPRESS, req.GetCount())
		case comm.EV_KEYUP:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_LGN_KEYUP, req.GetCount())
		case comm.EV_MOUSEDOWN:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_LGN_MOUSEDOWN, req.GetCount())
		case comm.EV_MOUSEMOVE:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_LGN_MOUSEMOVE, req.GetCount())
		case comm.EV_MOUSEOUT:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_LGN_MOUSEOUT, req.GetCount())
		case comm.EV_MOUSEOVER:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_LGN_MOUSEOVER, req.GetCount())
		case comm.EV_MOUSEUP:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_LGN_MOUSEUP, req.GetCount())
		case comm.EV_TOUCHSTART:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_LGN_TOUCHSTART, req.GetCount())
		case comm.EV_TOUCHMOVE:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_LGN_TOUCHMOVE, req.GetCount())
		case comm.EV_TOUCHEND:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_LGN_TOUCHEND, req.GetCount())
		case comm.EV_TOUCHCANCEL:
			pl.Send("HINCRBY", key, comm.COL_EVENT_BTN_LGN_TOUCHCANCEL, req.GetCount())
		}
	}
	pl.Send("HINCRBY", key, "UTM", time.Now().Unix()) // 更新时间
	return err
}

/******************************************************************************
 **函数名称: MsgSvrEventStatisticHandler
 **功    能: 事件统计上报信息处理
 **输入参数:
 **     cmd: 消息类型
 **     nid: 结点ID
 **     data: 收到数据
 **     length: 数据长度
 **     param: 附加参数
 **输出参数: NONE
 **返    回: VOID
 **实现描述:
 **请求协议:
 **注意事项:
 **作    者: # Qifeng.zou # 2017.05.18 09:41:31 #
 ******************************************************************************/
func MsgSvrEventStatisticHandler(cmd uint32, nid uint32, data []byte, length uint32, param interface{}) int {
	ctx, ok := param.(*MsgSvrCntx)
	if !ok {
		return -1
	}

	ctx.log.Debug("Recv event-statistic data! cmd:0x%04X nid:%d length:%d", cmd, nid, length)

	return 0
}
