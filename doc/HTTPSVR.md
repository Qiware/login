# HTTP接口列表

## 1. 登录注册<br>
### 1.1 获取IPLIST接口<br>
---
**功能描述**: 获取IPLIST接口<br>
**当前状态**: Ok<br>
**接口类型**: GET<br>
**接口路径**: /im/iplist?type=${type}&clientip=${clientip}<br>
**参数描述**:<br>
> type: LSN类型(0:Unknown 1:TCP 2:WS)(M)<br>
> uid: 用户ID(M)<br>
> sid: 会话SID(M)<br>
> clientip: 客户端IP(M)<br>

**返回结果**:<br>
>{<br>
>   "sid":${sid},           // 整型 | 会话SID(M)<br>
>   "type":${type},         // 整型 | LSN类型(0:UNKNOWN 1:TCP 2:WS)(M)<br>
>   "len":${len},           // 整型 | 列表长度(M)<br>
>   "iplist":[              // 数组 | IP列表<br>
>       "${ipaddr}:${port}",<br>
>       "${ipaddr}:${port}",<br>
>       "${ipaddr}:${port}"],<br>
>   "token":"${token}"      // 字串 | 鉴权token(M) # 格式:"sid:${sid}:ttl:${ttl}:end"<br>
>   "expire":${expire}      // 整型 | 有效时常(M) # 单位:秒<br>
>   "code":${code},         // 整型 | 错误码(M)<br>
>   "errmsg":"${errmsg}"    // 字串 | 错误描述(M)<br>
>}

## 2. 配置操作<br>
### 2.1 添加在线人数统计<br>
---
**功能描述**: 添加在线人数统计<br>
**当前状态**: Ok<br>
**接口类型**: GET<br>
**接口路径**: /im/config?action=add&option=user-statis&prec=${prec}&num=${num}<br>
**参数描述**:<br>
> action: 操作行为, 此时为add.(M)<br>
> option: 操作选项, 此时为user-statis.(M)<br>
> prec: 时间精度(M).可以有:300s, 600s, 1800s, 3600s(1h), 86400(1d), etc<br>
> num: 该精度的记录最大数(M).<br>

**返回结果**:<br>
>{<br>
>   "code":${code},     // 整型 | 错误码(M)<br>
>   "errmsg":"${errmsg}"// 字串 | 错误描述(M)<br>
>}

### 2.2 删除在线人数统计<br>
---
**功能描述**: 删除在线人数统计<br>
**当前状态**: Ok<br>
**接口类型**: GET<br>
**接口路径**: /im/config?action=del&option=user-statis&prec=${prec}<br>
**参数描述**:<br>
> action: 操作行为, 此时为del.(M)<br>
> option: 操作选项, 此时为user-statis.(M)<br>
> prec: 时间精度(M).可以有:300s, 600s, 1800s, 3600s(1h), 86400(1d), etc<br>

**返回结果**:<br>
>{<br>
>   "code":${code},     // 整型 | 错误码(M)<br>
>   "errmsg":"${errmsg}"// 字串 | 错误描述(M)<br>
>}

### 2.3 在线人数统计列表<br>
---
**功能描述**: 在线人数统计列表<br>
**当前状态**: Ok<br>
**接口类型**: GET<br>
**接口路径**: /im/config?action=list&option=user-statis<br>
**参数描述**:<br>
> action: 操作行为, 此时为list.(M)<br>
> option: 操作选项, 此时为user-statis.(M)<br>

**返回结果**:<br>
>{<br>
>   "len":${len},       // 整型 | 列表长度(M)<br>
>   "list":[            // 数组 | 精度列表(M)<br>
>       {"idx":${idx}, "prec":{prec}, "num":${num}}, // ${idx}:序号 ${prec}:精度值 ${num}:最大记录数<br>
>       {"idx":${idx}, "prec":{prec}, "num":${num}}],<br>
>   "code":${code},     // 整型 | 错误码(M)<br>
>   "errmsg":"${errmsg}"// 字串 | 错误描述(M)<br>
>}

### 2.4 查询在线人数统计<br>
---
**功能描述**: 查询在线人数统计<br>
**当前状态**: Ok<br>
**接口类型**: GET<br>
**接口路径**: /im/config?action=get&option=user-statis&prec=${prec}&num=${num}<br>
**参数描述**:<br>
> action: 操作行为, 此时为get.(M)<br>
> option: 操作选项, 此时为user-statis.(M)<br>
> prec: 时间精度(M). 如:300s, 600s, 1800s, 3600s(1h), 86400(1d), 1m, 1y<br>
> num: 记录条数, 从请求时间往前取${num}条记录.(M)<br>

**返回结果**:<br>
>{<br>
>   "prec":"${prec}",       // 整型 | 时间精度(M)<br>
>   "num":${num},           // 整型 | 列表长度(M)<br>
>   "list":[                // 数组 | 走势列表(M)<br>
>      {"idx":${idx}, "time":${time}, "time-str":"${time-str}", "num":${num}}, // ${time-str}:时间戳 ${num}:在线人数<br>
>      {"idx":${idx}, "time":${time}, "time-str":"${time-str}", "num":${num}},<br>
>      {"idx":${idx}, "time":${time}, "time-str":"${time-str}", "num":${num}}],<br>
>   "code":${code},         // 整型 | 错误码(M)<br>
>   "errmsg":"${errmsg}"    // 字串 | 错误描述(M)<br>
>}

## 3. 状态查询<br>
### 3.1 某用户SID列表<br>
---
**功能描述**: 查询某用户SID列表<br>
**当前状态**: Ok<br>
**接口类型**: GET<br>
**接口路径**: /im/query?option=sid-list&uid=${uid}<br>
**参数描述**:<br>
> option: 操作选项, 此时为sid-list.(M)<br>
> uid: 用户UID.(M)<br>

**返回结果**:<br>
>{<br>
>   "uid":"${uid}",         // 整型 | 用户ID(M)<br>
>   "len":${len},           // 整型 | 列表长度(M)<br>
>   "list":[                // 数组 | 当前正登陆设备列表(M)<br>
>      {"idx":${idx}, "sid":${sid}},     // ${sid}:会话ID<br>
>      {"idx":${idx}, "sid":${sid}}],<br>
>   "code":${code},         // 整型 | 错误码(M)<br>
>   "errmsg":"${errmsg}"    // 字串 | 错误描述(M)<br>
>}

## 4. 系统维护接口<br>
### 4.1 查询侦听层状态<br>
---
**功能描述**: 查询侦听层状态<br>
**当前状态**: 待测试<br>
**接口类型**: GET<br>
**接口路径**: /im/config?action=list&option=listend<br>
**参数描述**:<br>
> action: 操作行为, 此时为list.(M)<br>
> option: 操作选项, 此时为listend.(M)<br>

**返回结果**:<br>
>{<br>
>   "len":${len},           // 整型 | 列表长度(M)<br>
>   "list":[                // 数组 | 分组列表(M)<br>
>      {"idx":${idx}, "nid":${nid}, "type":${type}, "ipaddr":"{ipaddr}", "status":${status}, "total":"${total}"},<br>
>      {"idx":${idx}, "nid":${nid}, "type":${type}, "ipaddr":"{ipaddr}", "status":${status}, "total":"${total}"},<br>
>      {"idx":${idx}, "nid":${nid}, "type":${type}, "ipaddr":"{ipaddr}", "status":${status}, "total":"${total}"},<br>
>      {"idx":${idx}, "nid":${nid}, "type":${type}, "ipaddr":"{ipaddr}", "status":${status}, "total":"${total}"}],<br>
>   "code":${code},         // 整型 | 错误码(M)<br>
>   "errmsg":"${errmsg}"    // 字串 | 错误描述(M)<br>
>}

### 4.2 添加侦听层结点<br>
---
**功能描述**: 移除侦听层结点<br>
**当前状态**: 未完成<br>
**接口类型**: GET<br>
**接口路径**: /im/config?action=add&option=listend&nid=${nid}&ipaddr=${ipaddr}&port=${port}<br>
**参数描述**:<br>
> action: 操作行为, 此时为add.(M)<br>
> option: 操作选项, 此时为listend.(M)<br>
> nid: 结点ID(M)<br>
> ipaddr: 将被添加的侦听层结点IP地址.(M)<br>
> port: 将被添加的侦听层结点端口.(M)<br>

**返回结果**:<br>
>{<br>
>  "code":${code},      // 整型 | 错误码(M)<br>
>  "errmsg":"${errmsg}" // 字串 | 错误描述(M)<br>
>}<br>

### 4.3 移除侦听层结点<br>
---
**功能描述**: 移除侦听层结点<br>
**当前状态**: 未完成<br>
**接口类型**: GET<br>
**接口路径**: /im/config?action=del&option=listend&nid=${nid}&ipaddr=${ipaddr}&port=${port}<br>
**参数描述**:<br>
> action: 操作行为, 此时为del.(M)<br>
> option: 操作选项, 此时为listend.(M)<br>
> nid: 结点ID(M)<br>
> ipaddr: 将被移除的侦听层结点IP地址.(M)<br>
> port: 将被移除的侦听层结点端口.(M)<br>

**返回结果**:<br>
>{<br>
>  "code":${code},      // 整型 | 错误码(M)<br>
>  "errmsg":"${errmsg}" // 字串 | 错误描述(M)<br>
>}<br>

### 4.4 查询转发层状态<br>
---
**功能描述**: 查询转发层状态<br>
**当前状态**: 待测试<br>
**接口类型**: GET<br>
**接口路径**: /im/config?action=list&option=frwder<br>
**参数描述**:<br>
> action: 操作行为, 此时为list.(M)<br>
> option: 操作选项, 此时为frwder.(M)<br>

**返回结果**:<br>
>{<br>
>   "len":${len},           // 整型 | 列表长度(M)<br>
>   "list":[                // 数组 | 分组列表(M)<br>
>      {"idx":${idx}, "nid":${nid}, "ipaddr":"{ipaddr}", "port":${port}, "status":"${status}"},<br>
>      {"idx":${idx}, "nid":${nid}, "ipaddr":"{ipaddr}", "port":${port}, "status":"${status}"},<br>
>      {"idx":${idx}, "nid":${nid}, "ipaddr":"{ipaddr}", "port":${port}, "status":"${status}"},<br>
>      {"idx":${idx}, "nid":${nid}, "ipaddr":"{ipaddr}", "port":${port}, "status":"${status}"}],<br>
>   "code":${code},         // 整型 | 错误码(M)<br>
>   "errmsg":"${errmsg}"    // 字串 | 错误描述(M)<br>
>}
**补充说明**:<br>
> idx: 整型 | 序列号<br>
> nid: 整型 | 结点ID<br>
> ipaddr: 字串 | IP地址<br>
> port: 整型 | 端口号<br>
> status: 整型 | 状态<br>

### 4.5 添加转发层结点<br>
---
**功能描述**: 添加转发层结点<br>
**当前状态**: 未完成<br>
**接口类型**: GET<br>
**接口路径**: /im/config?action=add&option=frwder&nid=${nid}&ipaddr=${ipaddr}&port=${port}<br>
**参数描述**:<br>
> action: 操作行为, 此时为add.(M)<br>
> option: 操作选项, 此时为frwder.(M)<br>
> nid: 结点ID(M)<br>
> ipaddr: 将被添加的转发层结点IP地址.(M)<br>
> port: 将被添加的转发层结点端口.(M)<br>

**返回结果**:<br>
>{<br>
>  "code":${code},      // 整型 | 错误码(M)<br>
>  "errmsg":"${errmsg}" // 字串 | 错误描述(M)<br>
>}<br>

### 4.6 移除转发层结点<br>
---
**功能描述**: 移除转发层结点<br>
**当前状态**: 未完成<br>
**接口类型**: GET<br>
**接口路径**: /im/config?action=del&option=frwder&nid=${nid}&ipaddr=${ipaddr}&port=${port}<br>
**参数描述**:<br>
> action: 操作行为, 此时为del.(M)<br>
> option: 操作选项, 此时为frwder.(M)<br>
> nid: 结点ID(M)<br>
> ipaddr: 将被移除的转发层结点IP地址.(M)<br>
> port: 将被移除的转发层结点端口.(M)<br>

**返回结果**:<br>
>{<br>
>  "code":${code},      // 整型 | 错误码(M)<br>
>  "errmsg":"${errmsg}" // 字串 | 错误描述(M)<br>
>}<br>
