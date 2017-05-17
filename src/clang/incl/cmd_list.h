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
    , CMD_ONLINE                = 0x0001    /* 上线请求(服务端) */
    , CMD_ONLINE_ACK            = 0x0002    /* 上线请求应答(客户端) */

    , CMD_OFFLINE               = 0x0003    /* 下线请求(服务端) */
    , CMD_OFFLINE_ACK           = 0x0004    /* 下线请求应答(客户端) */

    , CMD_PING                  = 0x0005    /* 客户端心跳(服务端) */
    , CMD_PONG                  = 0x0006    /* 客户端心跳应答(客户端) */

    , CMD_KICK                  = 0x0007    /* 踢某连接下线 */
    , CMD_KICK_ACK              = 0x0008    /* 踢某连接下线应答 */

    /* 数据上报 */
    , CMD_BROWSER_ENV           = 0x0101    /* 环境信息 */
    , CMD_BROWSER_ENV_ACK       = 0x0102    /* 环境信息应答 */
    , CMD_EVENT_STATISTIC       = 0x0103    /* 事件统计 */
    , CMD_EVENT_STATISTIC_ACK   = 0x0104    /* 事件统计应答 */

    /* 系统内部消息 */
    , CMD_LSND_INFO             = 0x0601    /* 帧听层信息上报 */
    , CMD_LSND_INFO_ACK         = 0x0602    /* 帧听层信息上报应答 */

    , CMD_FRWD_INFO             = 0x0603    /* 转发层信息上报 */
    , CMD_FRWD_INFO_ACK         = 0x0604    /* 转发层信息上报应答 */
} mesg_type_e;

#endif /*__CMD_LIST_H__*/
