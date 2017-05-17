package controllers

import (
	"errors"
	"fmt"
	"strconv"
	"strings"
	"time"

	"github.com/golang/protobuf/proto"

	"ai-eye/src/golang/lib/comm"
	"ai-eye/src/golang/lib/crypt"
	"ai-eye/src/golang/lib/im"
	"ai-eye/src/golang/lib/mesg"
)

// 通用请求

////////////////////////////////////////////////////////////////////////////////
// 上线请求

type OnlineToken struct {
	ttl int64  /* TTL */
	sid uint64 /* 会话SID */
}

/******************************************************************************
 **函数名称: online_token_decode
 **功    能: 解码TOKEN
 **输入参数:
 **     token: TOKEN字串
 **输出参数: NONE
 **返    回: TOKEN字段
 **实现描述: 解析token, 并提取有效数据.
 **注意事项:
 **     TOKEN的格式"ttl:${ttl}:sid:${sid}:end"
 **     ttl: 该token的最大生命时间
 **     sid: 会话SID
 **作    者: # Qifeng.zou # 2016.11.20 09:28:06 #
 ******************************************************************************/
func (ctx *UsrSvrCntx) online_token_decode(token string) *OnlineToken {
	tk := &OnlineToken{}

	/* > TOKEN解码 */
	cry := crypt.CreateEncodeCtx(ctx.conf.Cipher)
	orig_token := crypt.Decode(cry, token)
	words := strings.Split(orig_token, ":")
	if 5 != len(words) {
		ctx.log.Error("Token format not right! token:%s orig:%s", token, orig_token)
		return nil
	}

	ctx.log.Debug("token:%s orig:%s", token, orig_token)

	/* > 验证TOKEN合法性 */
	ttl, _ := strconv.ParseInt(words[1], 10, 64)
	tk.ttl = int64(ttl)
	ctx.log.Debug("words[1]:%s ttl:%d", words[1], tk.ttl)

	sid, _ := strconv.ParseInt(words[3], 10, 64)
	tk.sid = uint64(sid)
	ctx.log.Debug("words[3]:%s sid:%d sid:%d", words[3], sid, tk.sid)

	return tk
}

/******************************************************************************
 **函数名称: online_req_check
 **功    能: 检验ONLINE请求合法性
 **输入参数:
 **     req: ONLINE请求
 **输出参数: NONE
 **返    回: 异常信息
 **实现描述: 计算TOKEN合法性
 **注意事项:
 **     1.TOKEN的格式"${ttl}:${sid}"
 **         ttl: 该token的最大生命时间
 **         sid: 会话SID
 **     2.头部数据(MesgHeader)中的SID此时表示的是客户端的连接CID.
 **作    者: # Qifeng.zou # 2016.11.02 10:20:57 #
 ******************************************************************************/
func (ctx *UsrSvrCntx) online_req_check(req *mesg.MesgOnline) error {
	token := ctx.online_token_decode(req.GetToken())
	if nil == token {
		ctx.log.Error("Decode token failed!")
		return errors.New("Decode token failed!")
	} else if token.ttl < time.Now().Unix() {
		ctx.log.Error("Token is timeout! sid:%d ttl:%d", token.sid, token.ttl)
		return errors.New("Token is timeout!")
	} else if uint64(token.sid) != req.GetSid() {
		ctx.log.Error("Token is invalid! sid:%d/%d ttl:%d",
			token.sid, req.GetSid(), token.ttl)
		return errors.New("Token is invalid!!")
	}

	return nil
}

/******************************************************************************
 **函数名称: online_parse
 **功    能: 解析上线请求
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
func (ctx *UsrSvrCntx) online_parse(data []byte) (
	head *comm.MesgHeader, req *mesg.MesgOnline, code uint32, err error) {
	/* > 字节序转换 */
	head = comm.MesgHeadNtoh(data)
	if !head.IsValid(1) {
		errmsg := "Header of online is invalid!"
		ctx.log.Error("Header is invalid! cmd:0x%04X nid:%d chksum:0x%08X",
			head.GetCmd(), head.GetNid(), head.GetChkSum())
		return nil, nil, comm.ERR_SVR_HEAD_INVALID, errors.New(errmsg)
	}

	ctx.log.Debug("Online request header! cmd:0x%04X length:%d chksum:0x%08X cid:%d nid:%d seq:%d head:%d",
		head.GetCmd(), head.GetLength(),
		head.GetChkSum(), head.GetSid(), head.GetNid(),
		head.GetSeq(), comm.MESG_HEAD_SIZE)

	/* > 解析PB协议 */
	req = &mesg.MesgOnline{}
	err = proto.Unmarshal(data[comm.MESG_HEAD_SIZE:], req)
	if nil != err {
		ctx.log.Error("Unmarshal body failed! errmsg:%s", err.Error())
		return head, nil, comm.ERR_SVR_BODY_INVALID, errors.New("Unmarshal body failed!")
	}

	/* > 校验协议合法性 */
	err = ctx.online_req_check(req)
	if nil != err {
		ctx.log.Error("Check online-request failed!")
		return head, req, comm.ERR_SVR_CHECK_FAIL, err
	}

	return head, req, 0, nil
}

/******************************************************************************
 **函数名称: online_failed
 **功    能: 发送上线应答
 **输入参数:
 **     head: 协议头
 **     req: 上线请求
 **     code: 错误码
 **     errmsg: 错误描述
 **输出参数: NONE
 **返    回: VOID
 **实现描述:
 **应答协议:
 ** {
 **     required uint64 sid = 1;        // M|连接ID|数字|内部使用
 **     required string app = 2;        // M|APP名|字串|
 **     required string version = 3;    // M|APP版本|字串|
 **     optional uint32 code = 4;       // M|错误码|数字|
 **     optional string errmsg = 5;     // M|错误描述|字串|
 ** }
 **注意事项:
 **作    者: # Qifeng.zou # 2016.11.01 18:37:59 #
 ******************************************************************************/
func (ctx *UsrSvrCntx) online_failed(head *comm.MesgHeader,
	req *mesg.MesgOnline, code uint32, errmsg string) int {
	if nil == head {
		return -1
	}

	/* > 设置协议体 */
	ack := &mesg.MesgOnlineAck{
		Code:   proto.Uint32(code),
		Errmsg: proto.String(errmsg),
	}

	if nil != req {
		ack.Sid = proto.Uint64(req.GetSid())
		ack.App = proto.String(req.GetApp())
		ack.Version = proto.String(req.GetVersion())
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

	head.Cmd = comm.CMD_ONLINE_ACK
	head.Length = uint32(length)

	comm.MesgHeadHton(head, p)
	copy(p.Buff[comm.MESG_HEAD_SIZE:], body)

	/* > 发送协议包 */
	ctx.frwder.AsyncSend(comm.CMD_ONLINE_ACK, p.Buff, uint32(len(p.Buff)))

	ctx.log.Debug("Send online ack succ!")

	return 0
}

/******************************************************************************
 **函数名称: online_ack
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
func (ctx *UsrSvrCntx) online_ack(head *comm.MesgHeader, req *mesg.MesgOnline) int {
	/* > 设置协议体 */
	ack := &mesg.MesgOnlineAck{
		Sid:    proto.Uint64(req.GetSid()),
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

	head.Cmd = comm.CMD_ONLINE_ACK
	head.Length = uint32(length)

	comm.MesgHeadHton(head, p)
	copy(p.Buff[comm.MESG_HEAD_SIZE:], body)

	/* > 发送协议包 */
	ctx.frwder.AsyncSend(comm.CMD_ONLINE_ACK, p.Buff, uint32(len(p.Buff)))

	ctx.log.Debug("Send online ack success!")

	return 0
}

/******************************************************************************
 **函数名称: online_handler
 **功    能: 上线处理
 **输入参数:
 **     req: 上线请求
 **输出参数: NONE
 **返    回: 异常信息
 **实现描述:
 **     1. 校验是否SID上线信息是否存在冲突. 如果存在冲突, 则将之前的连接踢下线.
 **     2. 更新数据库信息
 **注意事项:
 **     1. 在上线请求中, head中的sid此时为侦听层cid
 **     2. 在上线请求中, req中的sid此时为会话sid
 **作    者: # Qifeng.zou # 2016.11.01 21:12:36 #
 ******************************************************************************/
func (ctx *UsrSvrCntx) online_handler(head *comm.MesgHeader, req *mesg.MesgOnline) (err error) {
	var key string

	rds := ctx.redis.Get()
	defer rds.Close()

	pl := ctx.redis.Get()
	defer func() {
		pl.Do("")
		pl.Close()
	}()

	ttl := time.Now().Unix() + comm.CHAT_SID_TTL

	/* 获取会话属性 */
	attr, err := im.GetSidAttr(ctx.redis, req.GetSid())
	if nil != err {
		ctx.send_kick(req.GetSid(), head.GetCid(), head.GetNid(), comm.ERR_SYS_SYSTEM, err.Error())
		return err
	} else if 0 != attr.GetNid() && (attr.GetNid() != head.GetNid() || attr.GetCid() != head.GetCid()) {
		// 注意：当nid为0时表示会话SID之前并未登录.
		ctx.log.Error("Session's nid is conflict! sid:%d nid:[%d/%d] cid:%d",
			req.GetSid(), attr.GetNid(), head.GetNid(), head.GetCid())
		/* 清理会话数据 */
		im.CleanSessionData(ctx.redis, head.GetSid(), attr.GetCid(), attr.GetNid())
		/* 将老连接踢下线 */
		ctx.send_kick(req.GetSid(), attr.GetCid(), attr.GetNid(), comm.ERR_SVR_DATA_COLLISION, "Session's nid is collision!")
	}

	/* 记录SID集合 */
	pl.Send("ZADD", comm.IM_KEY_SID_ZSET, ttl, req.GetSid())

	/* 记录SID->CID & NID */
	key = fmt.Sprintf(comm.IM_KEY_SID_ATTR, req.GetSid())
	pl.Send("HMSET", key, "CID", head.GetCid(), "NID", head.GetNid())

	return err
}

/******************************************************************************
 **函数名称: UsrSvrOnlineHandler
 **功    能: 上线请求
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
 **     {
 **        required uint64 sid = 1;         // M|会话ID|数字|
 **        required string token = 2;       // M|鉴权TOKEN|字串|
 **        required string app = 3;         // M|APP名|字串|
 **        required string version = 4;     // M|APP版本|字串|
 **     }
 **注意事项:
 **     1. 首先需要调用MesgHeadNtoh()对头部数据进行直接序转换.
 **     2. 在上线请求中, head中的sid此时为侦听层cid
 **     3. 在上线请求中, req中的sid此时为会话sid
 **作    者: # Qifeng.zou # 2016.10.30 22:32:23 #
 ******************************************************************************/
func UsrSvrOnlineHandler(cmd uint32, nid uint32, data []byte, length uint32, param interface{}) int {
	ctx, ok := param.(*UsrSvrCntx)
	if !ok {
		return -1
	}

	ctx.log.Debug("Recv online request! cmd:0x%04X nid:%d length:%d", cmd, nid, length)

	/* > 解析上线请求 */
	head, req, code, err := ctx.online_parse(data)
	if nil != err {
		ctx.log.Error("Parse online request failed! errmsg:%s", err.Error())
		ctx.online_failed(head, req, code, err.Error())
		return -1
	}

	/* > 初始化上线环境 */
	err = ctx.online_handler(head, req)
	if nil != err {
		ctx.log.Error("Online handler failed!")
		ctx.online_failed(head, req, comm.ERR_SYS_SYSTEM, err.Error())
		return -1
	}

	/* > 发送上线应答 */
	ctx.online_ack(head, req)

	return 0
}

////////////////////////////////////////////////////////////////////////////////
// 下线请求

/******************************************************************************
 **函数名称: offline_parse
 **功    能: 解析Offline请求
 **输入参数:
 **     data: 接收的数据
 **输出参数: NONE
 **返    回:
 **     head: 通用协议头
 **     req: 协议体内容
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2016.11.02 22:17:38 #
 ******************************************************************************/
func (ctx *UsrSvrCntx) offline_parse(data []byte) (head *comm.MesgHeader) {
	/* > 字节序转换 */
	head = comm.MesgHeadNtoh(data)
	if !head.IsValid(1) {
		ctx.log.Error("Header is invalid! cmd:0x%04X nid:%d chksum:0x%08X",
			head.GetCmd(), head.GetNid(), head.GetChkSum())
		return nil
	}

	return head
}

/******************************************************************************
 **函数名称: offline_handler
 **功    能: Offline处理
 **输入参数:
 **     head: 协议头
 **输出参数: NONE
 **返    回: 异常信息
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2017.01.11 23:23:50 #
 ******************************************************************************/
func (ctx *UsrSvrCntx) offline_handler(head *comm.MesgHeader) error {
	return im.CleanSessionData(ctx.redis, head.GetSid(), head.GetCid(), head.GetNid())
}

/******************************************************************************
 **函数名称: UsrSvrOfflineHandler
 **功    能: 下线请求
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
 **作    者: # Qifeng.zou # 2016.10.30 22:32:23 #
 ******************************************************************************/
func UsrSvrOfflineHandler(cmd uint32, nid uint32, data []byte, length uint32, param interface{}) int {
	ctx, ok := param.(*UsrSvrCntx)
	if !ok {
		return -1
	}

	ctx.log.Debug("Recv offline request!")

	/* 1. > 解析下线请求 */
	head := ctx.offline_parse(data)
	if nil == head {
		ctx.log.Error("Parse offline request failed!")
		return -1
	}

	ctx.log.Debug("Offline data! sid:%d cid:%d nid:%d", head.GetSid(), head.GetCid(), head.GetNid())

	/* 2. > 清理会话数据 */
	err := ctx.offline_handler(head)
	if nil != err {
		ctx.log.Error("Offline handler failed!")
		return -1
	}

	return 0
}

////////////////////////////////////////////////////////////////////////////////
// PING请求

/******************************************************************************
 **函数名称: ping_parse
 **功    能: 解析PING请求
 **输入参数:
 **     data: 接收的数据
 **输出参数: NONE
 **返    回: 协议头
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2016.11.03 21:18:29 #
 ******************************************************************************/
func (ctx *UsrSvrCntx) ping_parse(data []byte) (head *comm.MesgHeader) {
	/* > 字节序转换 */
	head = comm.MesgHeadNtoh(data)
	if !head.IsValid(1) {
		ctx.log.Error("Header is invalid! cmd:0x%04X nid:%d chksum:0x%08X",
			head.GetCmd(), head.GetNid(), head.GetChkSum())
		return nil
	}

	return head
}

/******************************************************************************
 **函数名称: ping_handler
 **功    能: PING处理
 **输入参数:
 **     head: 协议头
 **输出参数: NONE
 **返    回: VOID
 **实现描述: 更新会话相关的TTL. 如果发现数据异常, 则需要清除该会话的数据, 并将该
 **          会话踢下线.
 **注意事项:
 **作    者: # Qifeng.zou # 2016.11.03 21:53:38 #
 ******************************************************************************/
func (ctx *UsrSvrCntx) ping_handler(head *comm.MesgHeader) {
	code, err := im.UpdateSessionData(ctx.redis, head.GetSid(), head.GetCid(), head.GetNid())
	if nil != err {
		im.CleanSessionData(ctx.redis, head.GetSid(), head.GetCid(), head.GetNid()) // 清理会话数据
		ctx.send_kick(head.GetSid(), head.GetCid(), head.GetNid(), code, err.Error())
	}
}

/******************************************************************************
 **函数名称: UsrSvrPingHandler
 **功    能: 客户端PING
 **输入参数:
 **     cmd: 消息类型
 **     nid: 结点ID
 **     data: 收到数据
 **     length: 数据长度
 **     param: 附加参数
 **输出参数: NONE
 **返    回: 0:成功 !0:失败
 **实现描述:
 **注意事项: 由侦听层给各终端回复PONG请求
 **作    者: # Qifeng.zou # 2016.11.03 21:40:30 #
 ******************************************************************************/
func UsrSvrPingHandler(cmd uint32, nid uint32, data []byte, length uint32, param interface{}) int {
	ctx, ok := param.(*UsrSvrCntx)
	if !ok {
		return -1
	}

	ctx.log.Debug("Recv ping request!")

	/* > 解析PING请求 */
	head := ctx.ping_parse(data)
	if nil == head {
		ctx.log.Error("Parse ping request failed!")
		return -1
	}

	/* > PING请求处理 */
	ctx.ping_handler(head)

	return 0
}

/******************************************************************************
 **函数名称: send_kick
 **功    能: 发送踢人操作
 **输入参数:
 **     sid: 会话ID
 **     cid: 连接ID
 **     nid: 结点ID
 **     code: 错误码
 **     errmsg: 错误描述
 **输出参数: NONE
 **返    回: VOID
 **实现描述:
 **应答协议:
 ** {
 **     required int code = 1;          // M|错误码|数字|
 **     required string errmsg = 2;     // M|错误描述|数字|
 ** }
 **注意事项:
 **作    者: # Qifeng.zou # 2016.12.16 20:49:02 #
 ******************************************************************************/
func (ctx *UsrSvrCntx) send_kick(sid uint64, cid uint64, nid uint32, code uint32, errmsg string) int {
	var head comm.MesgHeader

	ctx.log.Debug("Send kick command! sid:%d nid:%d", sid, nid)

	/* > 设置协议体 */
	req := &mesg.MesgKick{
		Code:   proto.Uint32(code),
		Errmsg: proto.String(errmsg),
	}

	/* 生成PB数据 */
	body, err := proto.Marshal(req)
	if nil != err {
		ctx.log.Error("Marshal protobuf failed! errmsg:%s", err.Error())
		return -1
	}

	length := len(body)

	/* > 拼接协议包 */
	p := &comm.MesgPacket{}
	p.Buff = make([]byte, comm.MESG_HEAD_SIZE+length)

	head.Cmd = comm.CMD_KICK
	head.Sid = sid
	head.Cid = cid
	head.Nid = nid
	head.Length = uint32(length)
	head.ChkSum = comm.MSG_CHKSUM_VAL

	comm.MesgHeadHton(&head, p)
	copy(p.Buff[comm.MESG_HEAD_SIZE:], body)

	/* > 发送协议包 */
	ctx.frwder.AsyncSend(comm.CMD_KICK, p.Buff, uint32(len(p.Buff)))

	return 0
}
