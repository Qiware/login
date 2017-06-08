package controllers

import (
	"github.com/golang/protobuf/proto"

	"login/src/golang/lib/comm"
	"login/src/golang/lib/mesg"
)

/******************************************************************************
 **函数名称: UpMesgRegister
 **功    能: 下行消息回调注册
 **输入参数: NONE
 **输出参数: NONE
 **返    回: VOID
 **实现描述: 为"下行"消息注册处理函数
 **注意事项: "下行"消息指的是从转发层发送过来的消息
 **作    者: # Qifeng.zou # 2017.03.06 17:54:26 #
 ******************************************************************************/
func (ctx *LsndCntx) UpMesgRegister() {
	/* > 未知消息 */
	ctx.frwder.Register(comm.CMD_UNKNOWN, LsndUpMesgCommHandler, ctx)

	/* > 通用消息 */
	ctx.frwder.Register(comm.CMD_ONLINE_ACK, LsndUpMesgOnlineAckHandler, ctx)
	ctx.frwder.Register(comm.CMD_KICK, LsndUpMesgKickHandler, ctx)

	/* > 内部运维消息 */
	ctx.frwder.Register(comm.CMD_LSND_INFO_ACK, LsndUpMesgLsndInfoAckHandler, ctx)
}

////////////////////////////////////////////////////////////////////////////////

/******************************************************************************
 **函数名称: LsndUpMesgCommHandler
 **功    能: 通用消息处理
 **输入参数:
 **     cmd: 消息类型
 **     nid: 结点ID
 **     data: 收到数据
 **     length: 数据长度
 **     param: 附加参数
 **输出参数: NONE
 **返    回: 0:成功 !0:失败
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2017.03.06 17:54:26 #
 ******************************************************************************/
func LsndUpMesgCommHandler(cmd uint32, nid uint32, data []byte, length uint32, param interface{}) int {
	ctx, ok := param.(*LsndCntx)
	if !ok {
		return -1
	}

	ctx.log.Debug("Recv command [0x%04X]!", cmd)

	/* > 验证合法性 */
	head := comm.MesgHeadNtoh(data)
	if !head.IsValid(1) {
		ctx.log.Error("Mesg head is invalid!")
		return -1
	}

	/* > 获取会话数据 */
	cid := head.GetCid()
	if 0 == cid {
		cid = ctx.session.GetCidBySid(head.GetSid())
		if 0 == cid {
			ctx.log.Error("Get cid by sid failed! sid:%d", head.GetSid())
			return -1
		}
	}

	extra := ctx.session.GetParam(head.GetSid(), cid)
	if nil == extra {
		ctx.log.Error("Didn't find conn data! sid:%d cid:%d", head.GetSid(), cid)
		return -1
	}

	conn, ok := extra.(*LsndConnExtra)
	if !ok {
		ctx.log.Error("Convert conn extra failed! sid:%d", head.GetSid())
		return -1
	}

	ctx.log.Debug("Session extra data. sid:%d cid:%d status:%d",
		conn.GetSid(), conn.GetCid(), conn.GetStatus())

	ctx.lws.AsyncSend(conn.GetCid(), data)

	return 0
}

////////////////////////////////////////////////////////////////////////////////

/******************************************************************************
 **函数名称: lsnd_error_online_ack_handler
 **功    能: ONLINE-ACK的异常处理
 **输入参数:
 **     cid: 连接ID
 **     head: 通用头(主机字节序)
 **     data: 下发数据
 **输出参数: NONE
 **返    回: 0:成功 !0:失败
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2017.03.13 01:06:41 #
 ******************************************************************************/
func (ctx *LsndCntx) lsnd_error_online_ack_handler(cid uint32, head *comm.MesgHeader, data []byte) int {
	/* > 下发ONLINE-ACK消息 */
	p := &comm.MesgPacket{Buff: data}

	comm.MesgHeadHton(head, p) /* 字节序转换(主机 - > 网络) */

	ctx.lws.AsyncSend(cid, data)

	/* > 加入被踢列表 */
	ctx.kick_add(cid)

	return -1
}

/******************************************************************************
 **函数名称: LsndUpMesgOnlineAckHandler
 **功    能: ONLINE-ACK消息的处理
 **输入参数:
 **     cmd: 消息类型
 **     nid: 结点ID
 **     data: 收到数据
 **     length: 数据长度
 **     param: 附加参数
 **输出参数: NONE
 **返    回: 0:成功 !0:失败
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2017.03.07 23:49:03 #
 ******************************************************************************/
func LsndUpMesgOnlineAckHandler(cmd uint32, nid uint32, data []byte, length uint32, param interface{}) int {
	ctx, ok := param.(*LsndCntx)
	if !ok {
		return -1
	}

	ctx.log.Debug("Recv online ack!")

	/* > 字节序转换(网络 -> 主机) */
	head := comm.MesgHeadNtoh(data)
	if !head.IsValid(1) {
		ctx.log.Error("Online-ack header is invalid!")
		return -1
	}

	cid := head.GetCid()

	/* > 消息ONLINE-ACK的处理 */
	ack := &mesg.MesgOnlineAck{}

	err := proto.Unmarshal(data[comm.MESG_HEAD_SIZE:], ack) /* 解析报体 */
	if nil != err {
		ctx.log.Error("Unmarshal online-ack failed! errmsg:%s", err.Error())
		return ctx.lsnd_error_online_ack_handler(cid, head, data)
	} else if 0 != ack.GetCode() {
		ctx.log.Error("Online failed! cid:%d sid:%d code:%d errmsg:%s",
			head.GetCid(), ack.GetSid(), ack.GetCode(), ack.GetErrmsg())
		return ctx.lsnd_error_online_ack_handler(cid, head, data)
	}

	/* > 获取&更新会话状态 */
	extra := ctx.session.GetParam(ack.GetSid(), cid)
	if nil == extra {
		ctx.log.Error("Didn't find conn data! cid:%d sid:%d", head.GetCid(), ack.GetSid())
		return ctx.lsnd_error_online_ack_handler(cid, head, data)
	}

	conn, ok := extra.(*LsndConnExtra)
	if !ok {
		ctx.log.Error("Convert conn extra failed! cid:%d sid:%d", head.GetCid(), ack.GetSid())
		return ctx.lsnd_error_online_ack_handler(cid, head, data)
	}

	conn.SetStatus(CONN_STATUS_LOGIN) /* 已登录 */

	/* 更新SID->CID映射 */
	_cid := ctx.session.GetCidBySid(ack.GetSid())
	if (0 != _cid) && (cid != _cid) {
		ctx.kick_add(_cid)
	}
	ctx.session.SetCid(ack.GetSid(), cid)

	/* > 下发ONLINE-ACK消息 */
	p := &comm.MesgPacket{Buff: data}

	comm.MesgHeadHton(head, p) /* 字节序转换(主机 - > 网络) */

	ctx.lws.AsyncSend(cid, data)

	ctx.log.Debug("Send online ack success! cid:%d sid:%d", conn.GetCid(), ack.GetSid())

	return 0
}

////////////////////////////////////////////////////////////////////////////////

/******************************************************************************
 **函数名称: LsndUpMesgKickHandler
 **功    能: KICK消息的处理
 **输入参数:
 **     cmd: 消息类型
 **     nid: 结点ID
 **     data: 收到数据
 **     length: 数据长度
 **     param: 附加参数
 **输出参数: NONE
 **返    回: 0:成功 !0:失败
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2017.04.29 19:39:30 #
 ******************************************************************************/
func LsndUpMesgKickHandler(cmd uint32, nid uint32, data []byte, length uint32, param interface{}) int {
	ctx, ok := param.(*LsndCntx)
	if !ok {
		return -1
	}

	ctx.log.Debug("Recv kick command!")

	/* > 字节序转换(网络 -> 主机) */
	head := comm.MesgHeadNtoh(data)
	if !head.IsValid(0) {
		ctx.log.Error("Kick head is invalid! sid:%d cid:%d seq:%d nid:%d",
			head.GetSid(), head.GetCid(), head.GetSeq(), head.GetNid())
		return -1
	}

	/* > 消息KICK的处理 */
	kick := &mesg.MesgKick{}

	err := proto.Unmarshal(data[comm.MESG_HEAD_SIZE:], kick) /* 解析报体 */
	if nil != err {
		ctx.log.Error("Unmarshal kick failed! errmsg:%s", err.Error())
		return -1
	}

	ctx.log.Debug("Kick command! code:%d errmsg:%s", kick.GetCode(), kick.GetErrmsg())

	/* > 下发KICK消息 */
	cid := ctx.session.GetCidBySid(head.GetSid())
	if 0 == cid {
		ctx.log.Error("Get cid by sid failed! sid:%d", head.GetSid())
		return -1
	}

	extra := ctx.session.GetParam(head.GetSid(), cid)
	if nil == extra {
		ctx.log.Error("Didn't find conn data! sid:%d", head.GetSid())
		return -1
	}

	conn, ok := extra.(*LsndConnExtra)
	if !ok {
		ctx.log.Error("Convert conn extra failed! sid:%d", head.GetSid())
		return -1
	}

	ctx.lws.AsyncSend(conn.GetCid(), data)

	/* > 执行KICK指令 */
	ctx.kick_add(conn.GetCid())

	return 0
}

////////////////////////////////////////////////////////////////////////////////
// 运维消息

/******************************************************************************
 **函数名称: LsndUpMesgLsndInfoAckHandler
 **功    能: LSND-INFO-ACK消息的处理
 **输入参数:
 **     cmd: 消息类型
 **     nid: 结点ID
 **     data: 收到数据
 **     length: 数据长度
 **     param: 附加参数
 **输出参数: NONE
 **返    回: 0:成功 !0:失败
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2017.03.21 18:05:18 #
 ******************************************************************************/
func LsndUpMesgLsndInfoAckHandler(cmd uint32, nid uint32, data []byte, length uint32, param interface{}) int {
	ctx, ok := param.(*LsndCntx)
	if !ok {
		return -1
	}

	ctx.log.Debug("Recv lsnd info ack!")

	return 0
}
