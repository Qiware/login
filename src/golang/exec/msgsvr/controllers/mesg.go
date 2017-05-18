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
