package comm

import (
	"encoding/binary"
)

type HttpResp struct {
	Code   int    `json:"code"`   // 错误码
	ErrMsg string `json:"errmsg"` // 错误描述
}

const (
	CMD_UNKNOWN = 0 /* 未知消息 */

	/* 通用消息 */
	CMD_ONLINE      = 0x0101 /* 上线请求(服务端) */
	CMD_ONLINE_ACK  = 0x0102 /* 上线请求应答(客户端) */
	CMD_OFFLINE     = 0x0103 /* 下线请求(服务端) */
	CMD_OFFLINE_ACK = 0x0104 /* 下线请求应答(客户端) */
	CMD_PING        = 0x0105 /* 客户端心跳(服务端) */
	CMD_PONG        = 0x0106 /* 客户端心跳应答(客户端) */
	CMD_KICK        = 0x0107 /* 踢人请求 */
	CMD_KICK_ACK    = 0x0108 /* 踢人应答 */

	/* 上报消息 */
	CMD_BROWSER_ENV         = 0x0201 /* 浏览器环境 */
	CMD_BROWSER_ENV_ACK     = 0x0202 /* 浏览器环境应答 */
	CMD_EVENT_STATISTIC     = 0x0203 /* 添加好友 */
	CMD_EVENT_STATISTIC_ACK = 0x0204 /* 添加好友应答 */

	/* 系统内部消息 */
	CMD_LSND_INFO     = 0x0301 /* 帧听层信息上报 */
	CMD_LSND_INFO_ACK = 0x0302 /* 帧听层信息上报应答 */
	CMD_FRWD_INFO     = 0x0303 /* 转发层信息上报 */
	CMD_FRWD_INFO_ACK = 0x0304 /* 转发层信息上报应答 */
)

const (
	MSG_CHKSUM_VAL = 0x1ED23CB4 /* 校验码 */
)

var (
	MESG_HEAD_SIZE = binary.Size(MesgHeader{})
)

/* 通用协议头 */
type MesgHeader struct {
	Cmd    uint32 /* 消息类型 */
	Length uint32 /* 报体长度 */
	ChkSum uint32 /* 校验值 */
	Sid    uint64 /* 会话ID */
	Cid    uint64 /* 连接ID */
	Nid    uint32 /* 结点ID */
	Seq    uint64 /* 流水号(注: 全局唯一流水号) */
}

func (head *MesgHeader) SetCmd(cmd uint32) {
	head.Cmd = cmd
}

func (head *MesgHeader) GetCmd() uint32 {
	return head.Cmd
}

func (head *MesgHeader) GetLength() uint32 {
	return head.Length
}

func (head *MesgHeader) GetChkSum() uint32 {
	return head.ChkSum
}

func (head *MesgHeader) SetSid(sid uint64) {
	head.Sid = sid
}

func (head *MesgHeader) GetSid() uint64 {
	return head.Sid
}

func (head *MesgHeader) SetCid(cid uint64) {
	head.Cid = cid
}

func (head *MesgHeader) GetCid() uint64 {
	return head.Cid
}

func (head *MesgHeader) SetNid(nid uint32) {
	head.Nid = nid
}

func (head *MesgHeader) GetNid() uint32 {
	return head.Nid
}

func (head *MesgHeader) GetSeq() uint64 {
	return head.Seq
}

type MesgPacket struct {
	Buff []byte /* 接收数据 */
}

/* "主机->网络"字节序 */
func MesgHeadHton(head *MesgHeader, p *MesgPacket) {
	binary.BigEndian.PutUint32(p.Buff[0:4], head.Cmd)     /* CMD */
	binary.BigEndian.PutUint32(p.Buff[4:8], head.Length)  /* LENGTH */
	binary.BigEndian.PutUint32(p.Buff[8:12], head.ChkSum) /* CHKSUM */
	binary.BigEndian.PutUint64(p.Buff[12:20], head.Sid)   /* SID */
	binary.BigEndian.PutUint64(p.Buff[20:28], head.Cid)   /* CID */
	binary.BigEndian.PutUint32(p.Buff[28:32], head.Nid)   /* NID */
	binary.BigEndian.PutUint64(p.Buff[32:40], head.Seq)   /* SEQ */
}

/* "网络->主机"字节序 */
func MesgHeadNtoh(data []byte) *MesgHeader {
	head := &MesgHeader{}

	head.Cmd = binary.BigEndian.Uint32(data[0:4])
	head.Length = binary.BigEndian.Uint32(data[4:8])
	head.ChkSum = binary.BigEndian.Uint32(data[8:12])
	head.Sid = binary.BigEndian.Uint64(data[12:20])
	head.Cid = binary.BigEndian.Uint64(data[20:28])
	head.Nid = binary.BigEndian.Uint32(data[28:32])
	head.Seq = binary.BigEndian.Uint64(data[32:40])

	return head
}

/* 校验头部数据的合法性 */
func (head *MesgHeader) IsValid(flag uint32) bool {
	if 0 == head.Nid || MSG_CHKSUM_VAL != head.ChkSum {
		return false
	} else if 0 != flag && 0 == head.Sid {
		return false
	}
	return true
}
