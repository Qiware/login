#include "log.h"
#include "redo.h"
#include "atomic.h"
#include "session.h"

/* 会话ID哈希回调 */
static uint64_t session_hash_cb(session_item_t *s)
{
    return s->sid;
}

/* 会话SID+连接CID比较回调 */
static int session_cmp_cb(session_item_t *s1, session_item_t *s2)
{
    int diff;

    diff = (int)(s1->sid - s2->sid);
    if (0 == diff) {
        return (int)(s1->cid - s2->cid);
    }

    return diff;
}

/* SID->CID哈希回调 */
static uint64_t session_dict_hash_cb(session_dict_item_t *item)
{
    return item->sid;
}

/* SID->CID比较回调 */
static int session_dict_cmp_cb(session_dict_item_t *item1, session_dict_item_t *item2)
{
    return (int)(item1->sid - item2->sid);
}

/******************************************************************************
 **函数名称: session_tab_init
 **功    能: 初始化上下文
 **输入参数:
 **     len: 槽的长度
 **     log: 日志对象
 **输出参数: NONE
 **返    回: TAB对象
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2016.09.21 10:38:44 #
 ******************************************************************************/
session_tab_t *session_tab_init(int len, log_cycle_t *log)
{
    session_tab_t *tab;

    /* > 创建全局对象 */
    tab = (session_tab_t *)calloc(1, sizeof(session_tab_t));
    if (NULL == tab) {
        return NULL;
    }

    tab->log = log;

    do {
        /* > 初始化SID->CID表 */
        tab->dict = hash_tab_creat(len,
                (hash_cb_t)session_dict_hash_cb,
                (cmp_cb_t)session_dict_cmp_cb, NULL);
        if (NULL == tab->dict) {
            break;
        }

        /* > 初始化SESSION表 */
        tab->sessions = hash_tab_creat(len,
                (hash_cb_t)session_hash_cb,
                (cmp_cb_t)session_cmp_cb, NULL);
        if (NULL == tab->sessions) {
            break;
        }

        return tab;
    } while(0);

    /* > 释放内存 */
    hash_tab_destroy(tab->dict, (mem_dealloc_cb_t)mem_dummy_dealloc, NULL);
    hash_tab_destroy(tab->sessions, (mem_dealloc_cb_t)mem_dummy_dealloc, NULL);

    FREE(tab);

    return NULL;
}

/******************************************************************************
 **函数名称: session_add
 **功    能: 添加会话
 **输入参数: 
 **     tab: TAB对象
 **     sid: 会话ID
 **     cid: 连接ID
 **     ctm: 创建时间
 **输出参数: NONE
 **返    回: 0:成功 !0:失败
 **实现描述:
 **注意事项: 
 **作    者: # Qifeng.zou # 2016.09.21 19:59:38 #
 ******************************************************************************/
int session_add(session_tab_t *tab, uint64_t sid, uint64_t cid, time_t ctm)
{
    session_item_t *session;

    /* > 新建会话对象 */
    session = (session_item_t *)calloc(1, sizeof(session_item_t));
    if (NULL == session) {
        return -1;
    }

    session->sid = sid;
    session->cid = cid;
    session->ctm = ctm;

    /* > 插入会话表 */
    if (hash_tab_insert(tab->sessions, (void *)session, WRLOCK)) {
        FREE(session);
        return -1;
    }

    return 0;
}

/******************************************************************************
 **函数名称: session_del
 **功    能: 删除会话
 **输入参数: 
 **     tab: TAB对象
 **     sid: 会话ID
 **     cid: 连接ID
 **输出参数: NONE
 **返    回: 0:成功 !0:失败
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2016.09.20 19:59:38 #
 ******************************************************************************/
int session_del(session_tab_t *tab, uint64_t sid, uint64_t cid)
{
    session_item_t *session, key;

    /* > 删除SID->CID映射 */
    session_dict_del(tab, sid, cid);

    /* > 删除SID+CID索引 */
    key.sid = sid;
    key.cid = cid;

    session = hash_tab_delete(tab->sessions, (void *)&key, WRLOCK);
    if (NULL == session) {
        log_error(tab->log, "Didn't find sid[%u]. ptr:%p", sid, session);
        return 0; /* Didn't find */
    }

    /* > 释放会话对象 */
    FREE(session);

    return 0;
}

/******************************************************************************
 **函数名称: session_dict_get
 **功    能: 通过SID获取CID
 **输入参数: 
 **     tab: TAB对象
 **     sid: 会话ID
 **输出参数: NONE
 **返    回: 连接CID
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2017.05.07 10:24:42 #
 ******************************************************************************/
uint64_t session_dict_get(session_tab_t *tab, uint64_t sid)
{
    uint64_t cid;
    session_dict_item_t *item, key;

    /* > 删除SID索引 */
    key.sid = sid;

    item = hash_tab_query(tab->dict, (void *)&key, RDLOCK);
    if (NULL == item) {
        log_error(tab->log, "Didn't find cid by sid. sid:%u.", sid);
        return 0; /* Didn't find */
    }

    cid = item->cid;

    hash_tab_unlock(tab->dict, (void *)&key, RDLOCK);

    return cid;
}

/******************************************************************************
 **函数名称: session_dict_add
 **功    能: 设置SID->CID映射
 **输入参数: 
 **     tab: TAB对象
 **     sid: 会话ID
 **     cid: 连接ID
 **输出参数: NONE
 **返    回: 0:成功 !0:失败
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2017.05.07 10:48:27 #
 ******************************************************************************/
int session_dict_add(session_tab_t *tab, uint64_t sid, uint64_t cid)
{
    int ret;
    session_dict_item_t *item, key;

AGAIN:
    /* > 查询SID->CID项 */
    key.sid = sid;

    item = hash_tab_query(tab->dict, (void *)&key, WRLOCK);
    if (NULL != item) {
        if (item->cid == cid) {
            hash_tab_unlock(tab->dict, (void *)&key, WRLOCK);
            return 0; // 已存在
        }
        hash_tab_delete(tab->dict, (void *)&key, NONLOCK); // 已加锁

        /* > 新建SID->CID项 */
        item = (session_dict_item_t *)calloc(1, sizeof(session_dict_item_t));
        if (NULL == item) {
            log_error(tab->log, "Alloc memory failed! errmsg:[%d] %s!", errno, strerror(errno));
            return -1;
        }

        item->sid = sid;
        item->cid = cid;

        ret = hash_tab_insert(tab->dict, (void *)item, NONLOCK); // 已加锁
        if (0 != ret) {
            hash_tab_unlock(tab->dict, (void *)&key, WRLOCK);
            free(item);
            log_error(tab->log, "Insert sid to cid map failed. sid:%lu cid:%lu.", sid, cid);
            return -1;
        }
        hash_tab_unlock(tab->dict, (void *)&key, WRLOCK);
    } else {
        /* > 新建SID->CID项 */
        item = (session_dict_item_t *)calloc(1, sizeof(session_dict_item_t));
        if (NULL == item) {
            log_error(tab->log, "Alloc memory failed! errmsg:[%d] %s!", errno, strerror(errno));
            return -1;
        }

        item->sid = sid;
        item->cid = cid;

        ret = hash_tab_insert(tab->dict, (void *)item, WRLOCK); // 加写锁
        if (0 != ret) {
            free(item);
            log_error(tab->log, "Insert sid to cid map failed. sid:%lu cid:%lu.", sid, cid);
            goto AGAIN;
        }
    }

    return 0;
}

/******************************************************************************
 **函数名称: session_dict_del
 **功    能: 删除SID->CID映射
 **输入参数: 
 **     tab: TAB对象
 **     sid: 会话ID
 **     cid: 连接ID
 **输出参数: NONE
 **返    回: 0:成功 !0:失败
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2017.05.08 08:37:58 #
 ******************************************************************************/
int session_dict_del(session_tab_t *tab, uint64_t sid, uint64_t cid)
{
    session_dict_item_t *item, key;

    /* > 删除SID索引 */
    key.sid = sid;

    item = hash_tab_query(tab->dict, (void *)&key, WRLOCK);
    if (NULL != item) {
        if (item->cid == cid) { // 相等时才执行删除操作
            hash_tab_delete(tab->dict, (void *)&key, NONLOCK);
            hash_tab_unlock(tab->dict, (void *)&key, WRLOCK);
            free(item);
        } else {
            hash_tab_unlock(tab->dict, (void *)&key, WRLOCK);
        }
    }

    return 0;
}
