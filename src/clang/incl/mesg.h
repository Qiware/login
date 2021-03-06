/******************************************************************************
 ** Copyright(C) 2014-2024 Qiware technology Co., Ltd
 **
 ** 文件名: mesg.h
 ** 版本号: 1.0
 ** 描  述: 消息类型的定义
 ** 作  者: # Qifeng.zou # Fri 08 May 2015 10:43:30 PM CST #
 ******************************************************************************/
#if !defined(__MESG_H__)
#define __MESG_H__

#include "comm.h"

/* 通用协议头 */
typedef struct
{
    uint32_t type;                      /* 消息类型 */
    uint32_t length;                    /* 报体长度 */

    uint32_t sid;                       /* 会话ID */
    uint32_t cid;                       /* 连接ID */
    uint32_t nid;                       /* 结点ID */

    uint64_t seq;                       /* 消息序列号(注: 全局唯一流水号) */
    char body[0];                       /* 消息体 */
}__attribute__ ((__packed__))mesg_header_t;

/* 字节序转换 */
#define MESG_HEAD_HTON(h, n) do { /* 主机->网络 */\
    (n)->type = htonl((h)->type); \
    (n)->length = htonl((h)->length); \
    (n)->sid = htonl((h)->sid); \
    (n)->cid = htonl((h)->cid); \
    (n)->nid = htonl((h)->nid); \
    (n)->seq = htonl((h)->seq); \
} while(0)

#define MESG_HEAD_NTOH(n, h) do { /* 网络->主机*/\
    (h)->type = ntohl((n)->type); \
    (h)->length = ntohl((n)->length); \
    (h)->sid = ntohl((n)->sid); \
    (h)->cid = ntohl((n)->cid); \
    (h)->nid = ntohl((n)->nid); \
    (h)->seq = ntohl((n)->seq); \
} while(0)

#define MESG_HEAD_SET(head, _type, _sid, _cid, _nid, _seq, _len) do { /* 设置协议头 */\
    (head)->type = (_type); \
    (head)->length = (_len); \
    (head)->sid = (_sid); \
    (head)->cid = (_cid); \
    (head)->nid = (_nid); \
    (head)->seq = (_seq); \
} while(0)

#define MESG_TOTAL_LEN(body_len) (sizeof(mesg_header_t) + body_len)

#define MESG_HEAD_PRINT(log, head) \
    log_debug((log), "type:0x%04X len:%d sid:%u cid:%u nid:%u seq:%u", \
            (head)->type, (head)->length, \
            (head)->sid, (head)->cid, (head)->nid, (head)->seq);

#endif /*__MESG_H__*/
