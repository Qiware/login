#if !defined(__SESSION_H__)
#define __SESSION_H__

#include "log.h"
#include "comm.h"
#include "list.h"
#include "rb_tree.h"
#include "avl_tree.h"
#include "hash_tab.h"

/* 聊天室会话信息 */
typedef struct
{
    uint64_t sid;               /* 会话SID(SID+CID主键) */
    uint64_t cid;               /* 连接CID(SID+CID主键) */
    time_t ctm;                 /* 创建时间 */
} session_item_t;

/* SID->CID字典 */
typedef struct {
    uint64_t sid;               /* 会话SID */
    uint64_t cid;               /* 连接CID */
} session_dict_item_t;

/* 全局信息 */
typedef struct
{
    log_cycle_t *log;           /* 日志对象 */

    hash_tab_t *dict;           /* SID->CID信息 */
    hash_tab_t *sessions;       /* SESSION信息(注: (SID+CID)为主键存储数据session_item_t) */
} session_tab_t;

session_tab_t *session_tab_init(int len, log_cycle_t *log); // OK

int session_add(session_tab_t *tab, uint64_t sid, uint64_t cid, time_t ctm);
int session_del(session_tab_t *tab, uint64_t sid, uint64_t cid); // OK

uint64_t session_dict_get(session_tab_t *tab, uint64_t sid); // OK
int session_dict_add(session_tab_t *tab, uint64_t sid, uint64_t cid); // OK
int session_dict_del(session_tab_t *tab, uint64_t sid, uint64_t cid); // OK

#endif /*__SESSION_H__*/
