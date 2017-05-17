package session

import (
	"time"
)

////////////////////////////////////////////////////////////////////////////////
// 会话操作

/******************************************************************************
 **函数名称: session_del
 **功    能: 移除会话管理表
 **输入参数:
 **     sid: 会话SID
 **     cid: 连接CID
 **输出参数: NONE
 **返    回: 会话数据
 **实现描述: 从session[]表中删除sid的会话数据
 **注意事项:
 **作    者: # Qifeng.zou # 2017.03.02 10:13:34 #
 ******************************************************************************/
func (ctx *SessionTab) session_del(sid uint64, cid uint64) *SessionItem {
	ss := &ctx.sessions[sid%SESSION_MAX_LEN]

	ss.Lock()
	defer ss.Unlock()

	/* > 判断会话是否存在 */
	key := &SessionKey{sid: sid, cid: cid}

	ssn, ok := ss.session[*key]
	if !ok {
		return nil // 无数据
	}
	delete(ss.session, *key)

	return ssn
}

/******************************************************************************
 **函数名称: sid2cid_del
 **功    能: 移除映射信息
 **输入参数:
 **     sid: 会话SID
 **     cid: 连接CID
 **输出参数: NONE
 **返    回: 0:成功 !0:失败
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2017.05.11 10:03:30 #
 ******************************************************************************/
func (ctx *SessionTab) sid2cid_del(sid uint64, cid uint64) int {
	sc := &ctx.sid2cids[sid%SESSION_MAX_LEN]

	sc.Lock()
	defer sc.Unlock()

	_cid, ok := sc.sid2cid[sid]
	if !ok {
		return 0 // 无数据
	} else if _cid == cid {
		delete(sc.sid2cid, sid)
	}

	return 0
}

////////////////////////////////////////////////////////////////////////////////
// 会话操作

/******************************************************************************
 **函数名称: trav_list
 **功    能: 遍历会话列表
 **输入参数:
 **     proc: 处理回调
 **     param: 附加参数
 **输出参数: NONE
 **返    回: VOID
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2017.05.10 21:05:08 #
 ******************************************************************************/
func (sl *SessionList) trav_list(proc SessionTravProcCb, param interface{}) {
	sl.RLock()
	defer sl.RUnlock()

	for k, v := range sl.session {
		proc(k.sid, k.cid, v.param, param)
	}
}

////////////////////////////////////////////////////////////////////////////////
// 映射操作

/******************************************************************************
 **函数名称: trav_list
 **功    能: 遍历映射列表
 **输入参数:
 **     proc: 处理回调
 **     param: 附加参数
 **输出参数: NONE
 **返    回: VOID
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2017.05.11 10:07:32 #
 ******************************************************************************/
func (sc *SessionSid2CidList) trav_list(proc SessionTravSid2CidProcCb, param interface{}) {
	sc.RLock()
	defer sc.RUnlock()

	for sid, cid := range sc.sid2cid {
		proc(sid, cid, param)
	}
}

/******************************************************************************
 **函数名称: query_dirty
 **功    能: 查找脏数据(不一致的数据)
 **输入参数:
 **     ls: 脏数据列表
 **输出参数: NONE
 **返    回: VOID
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2017.05.11 10:32:16 #
 ******************************************************************************/
func (sc *SessionSid2CidList) query_dirty(ctx *SessionTab, ls map[uint64]uint64) {
	sc.RLock()
	defer sc.RUnlock()

	for sid, cid := range sc.sid2cid {
		extra := ctx.SessionGetParam(sid, cid)
		if nil != extra {
			continue
		}
		ls[sid] = cid
	}
}

/******************************************************************************
 **函数名称: task_clean_sid2cid
 **功    能: 清理SID->CID映射数据(防止映射始终存在导致内存泄露)
 **输入参数: NONE
 **输出参数: NONE
 **返    回: VOID
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2017.05.11 08:53:21 #
 ******************************************************************************/
func (ctx *SessionTab) task_clean_sid2cid() {
	for {
		list := make(map[uint64]uint64)

		for idx := 0; idx < SESSION_MAX_LEN; idx += 1 {
			sc := &ctx.sid2cids[idx]

			sc.query_dirty(ctx, list)
		}

		for _, sid := range list {
			ctx.sid2cid_del(sid, list[sid])
		}

		time.Sleep(15 * time.Second)
	}
}
