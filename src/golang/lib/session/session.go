package session

import (
	"sync"
)

const (
	SESSION_MAX_LEN = 999 // 聊天室分组列表长度
)

/* 遍历回调 */
type SessionTravSid2CidProcCb func(sid uint32, cid uint32, param interface{}) int
type SessionTravProcCb func(sid uint32, cid uint32, extra interface{}, param interface{}) int

/* 会话信息 */
type SessionItem struct {
	sid          uint32      // 会话SID
	cid          uint32      // 连接CID
	sync.RWMutex             // 读写锁
	param        interface{} // 扩展数据
}

/* SESSION ITEM主键 */
type SessionKey struct {
	sid uint32 // 会话ID
	cid uint32 // 连接ID
}

/* SESSION TAB信息 */
type SessionList struct {
	sync.RWMutex                             // 读写锁
	session      map[SessionKey]*SessionItem // 会话集合[sid&cid]*SessionItem
}

/* SID->CID字典信息 */
type SessionDict struct {
	sync.RWMutex                   // 读写锁
	sid2cid      map[uint32]uint32 // 会话集合[sid]cid
}

/* 全局对象 */
type SessionTab struct {
	dict     [SESSION_MAX_LEN]SessionDict // SID->CID映射
	sessions [SESSION_MAX_LEN]SessionList // SESSION信息
}

/******************************************************************************
 **函数名称: Init
 **功    能: 初始化
 **输入参数: NONE
 **输出参数: NONE
 **返    回: 全局对象
 **实现描述: 初始化ctx成员变量
 **注意事项:
 **作    者: # Qifeng.zou # 2017.02.20 23:46:50 #
 ******************************************************************************/
func Init() *SessionTab {
	ctx := &SessionTab{}

	/* 初始化SESSION信息 */
	for idx := 0; idx < SESSION_MAX_LEN; idx += 1 {
		ss := &ctx.sessions[idx]
		ss.session = make(map[SessionKey]*SessionItem)
	}

	/* 初始化SID->CID映射 */
	for idx := 0; idx < SESSION_MAX_LEN; idx += 1 {
		ss := &ctx.dict[idx]
		ss.sid2cid = make(map[uint32]uint32)
	}

	/* 启动定时任务 */
	go ctx.task_clean_sid2cid()

	return ctx
}

/******************************************************************************
 **函数名称: GetCidBySid
 **功    能: 通过SID获取CID
 **输入参数:
 **     sid: 会话ID
 **输出参数: NONE
 **返    回: 连接CID
 **实现描述: 从sid2cid映射中查询
 **注意事项:
 **作    者: # Qifeng.zou # 2017.05.07 07:24:06 #
 ******************************************************************************/
func (ctx *SessionTab) GetCidBySid(sid uint32) uint32 {
	ss := &ctx.dict[sid%SESSION_MAX_LEN]

	ss.RLock()
	defer ss.RUnlock()

	cid, ok := ss.sid2cid[sid]
	if !ok {
		return 0
	}

	return cid
}

/******************************************************************************
 **函数名称: SetCid
 **功    能: 设置SID->CID映射
 **输入参数:
 **     sid: 会话ID
 **     cid: 连接ID
 **输出参数: NONE
 **返    回: 0:成功 !0:失败
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2017.05.07 07:42:07 #
 ******************************************************************************/
func (ctx *SessionTab) SetCid(sid uint32, cid uint32) int {
	ss := &ctx.dict[sid%SESSION_MAX_LEN]

	ss.Lock()
	defer ss.Unlock()

	ss.sid2cid[sid] = cid

	return 0
}

/******************************************************************************
 **函数名称: Delete
 **功    能: 会话删除
 **输入参数:
 **     sid: 会话ID
 **     cid: 连接ID
 **输出参数: NONE
 **返    回: 0:成功 !0:失败
 **实现描述:
 **     1. 清理会话表中的数据
 **     2. 清理聊天室各层级数据
 **注意事项:
 **作    者: # Qifeng.zou # 2017.02.22 20:54:53 #
 ******************************************************************************/
func (ctx *SessionTab) Delete(sid uint32, cid uint32) int {
	/* > 清理映射数据 */
	ctx.sid2cid_del(sid, cid)

	/* > 清理会话数据 */
	ssn := ctx.session_del(sid, cid)
	if nil == ssn {
		return 0 // 无数据
	}

	return 0
}

/******************************************************************************
 **函数名称: SetParam
 **功    能: 设置会话参数
 **输入参数:
 **     sid: 会话SID
 **     param: 扩展数据
 **输出参数: NONE
 **返    回: 0:成功 !0:失败
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2017.02.22 20:32:20 #
 ******************************************************************************/
func (ctx *SessionTab) SetParam(sid uint32, cid uint32, param interface{}) int {
	ss := &ctx.sessions[sid%SESSION_MAX_LEN]

	ss.Lock()
	defer ss.Unlock()

	/* > 判断会话是否存在 */
	key := &SessionKey{sid: sid, cid: cid}

	ssn, ok := ss.session[*key]
	if ok {
		return -1 // 已存在
	}

	/* > 添加会话信息 */
	ssn = &SessionItem{
		sid:   sid,   // 会话ID
		cid:   cid,   // 连接ID
		param: param, // 扩展数据
	}

	ss.session[*key] = ssn

	return 0
}

/******************************************************************************
 **函数名称: GetParam
 **功    能: 获取会话参数
 **输入参数:
 **     sid: 会话SID
 **     cid: 连接CID
 **输出参数: NONE
 **返    回: 扩展数据
 **实现描述:
 **注意事项: 各层级读写锁的操作, 降低锁粒度, 防止死锁.
 **作    者: # Qifeng.zou # 2017.03.07 17:02:35 #
 ******************************************************************************/
func (ctx *SessionTab) GetParam(sid uint32, cid uint32) (param interface{}) {
	ss := &ctx.sessions[sid%SESSION_MAX_LEN]

	ss.RLock()
	defer ss.RUnlock()

	key := &SessionKey{sid: sid, cid: cid}

	ssn, ok := ss.session[*key]
	if !ok {
		return nil
	}

	return ssn.param // 已存在
}

/******************************************************************************
 **函数名称: Total
 **功    能: 获取会话总数
 **输入参数: NONE
 **输出参数: NONE
 **返    回: 会话总数
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2017.03.21 18:37:55 #
 ******************************************************************************/
func (ctx *SessionTab) Total() uint32 {
	var total uint32

	for idx := 0; idx < SESSION_MAX_LEN; idx += 1 {
		item := &ctx.sessions[idx%SESSION_MAX_LEN]

		item.RLock()
		total += uint32(len(item.session))
		item.RUnlock()
	}
	return total
}

/******************************************************************************
 **函数名称: Trav
 **功    能: 遍历所有会话
 **输入参数:
 **     proc: 处理回调
 **     param: 附加参数
 **输出参数: NONE
 **返    回: VOID
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2017.05.10 20:33:38 #
 ******************************************************************************/
func (ctx *SessionTab) Trav(proc SessionTravProcCb, param interface{}) {
	for idx := 0; idx < SESSION_MAX_LEN; idx += 1 {
		sl := &ctx.sessions[idx]

		sl.trav_list(proc, param)
	}
}

/******************************************************************************
 **函数名称: TravSid2Cid
 **功    能: 遍历SID->CID映射
 **输入参数:
 **     proc: 处理回调
 **     param: 附加参数
 **输出参数: NONE
 **返    回: VOID
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2017.05.11 10:06:00 #
 ******************************************************************************/
func (ctx *SessionTab) TravSid2Cid(proc SessionTravSid2CidProcCb, param interface{}) {
	for idx := 0; idx < SESSION_MAX_LEN; idx += 1 {
		sc := &ctx.dict[idx]

		sc.trav_list(proc, param)
	}
}
