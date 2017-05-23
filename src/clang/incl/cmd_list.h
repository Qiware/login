/******************************************************************************
 ** Copyright(C) 2014-2024 Qiware technology Co., Ltd
 **
 ** 文件名: cmd_list.h
 ** 版本号: 1.0
 ** 描  述: 消息类型的定义
 ** 作  者: # Qifeng.zou # Fri 08 May 2015 10:43:30 PM CST #
 ******************************************************************************/
#if !defined(__CMD_LIST_H__)
#define __CMD_LIST_H__

/* 消息类型 */
typedef enum
{
    CMD_UNKNOWN                             /* 未知消息 */

    /* 通用消息 */
    , CMD_ONLINE                = 0x0101    /* 上线请求(服务端) */
    , CMD_ONLINE_ACK            = 0x0102    /* 上线请求应答(客户端) */

    , CMD_OFFLINE               = 0x0103    /* 下线请求(服务端) */
    , CMD_OFFLINE_ACK           = 0x0104    /* 下线请求应答(客户端) */

    , CMD_PING                  = 0x0105    /* 客户端心跳(服务端) */
    , CMD_PONG                  = 0x0106    /* 客户端心跳应答(客户端) */

    , CMD_KICK                  = 0x0107    /* 踢某连接下线 */
    , CMD_KICK_ACK              = 0x0108    /* 踢某连接下线应答 */

    /* 数据上报 */
    , CMD_BROWSER_ENV           = 0x0201    /* 环境信息 */
    , CMD_BROWSER_ENV_ACK       = 0x0202    /* 环境信息应答 */
    , CMD_EVENT_STATISTIC       = 0x0203    /* 事件统计 */
    , CMD_EVENT_STATISTIC_ACK   = 0x0204    /* 事件统计应答 */

    /* 系统内部消息 */
    , CMD_LSND_INFO             = 0x0301    /* 帧听层信息上报 */
    , CMD_LSND_INFO_ACK         = 0x0302    /* 帧听层信息上报应答 */

    , CMD_FRWD_INFO             = 0x0303    /* 转发层信息上报 */
    , CMD_FRWD_INFO_ACK         = 0x0304    /* 转发层信息上报应答 */
} mesg_type_e;

#endif /*__CMD_LIST_H__*/
