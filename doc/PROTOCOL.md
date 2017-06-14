# 协议头

---
|**序号**|**字段名**|**字段类型**|**字段长度(字节)**|**字段含义**|**备注**|
|:------:|:---------|:-----------|:-------------:|:-------|:-------|
| 01 | type | uint32_t | 4 |消息类型|命令ID|
| 02 | length | uint32_t | 4 |报体长度|不包含报头|
| 03 | sid | uint32_t | 8 |会话ID|每个连接的会话ID都不一样|
| 04 | cid | uint32_t | 8 |连接ID| |
| 05 | nid | uint32_t | 4 |结点ID| |
| 07 | seq | uint32_t | 8 |流水号| |

# 通用消息

---
命令ID: 0x0101:<br>
命令描述: 上线请求(ONLINE)<br>
协议格式:<br>
`message mesg_online_req
{
    required uint64 sid = 1;        // M|会话ID|数字|
    required string token = 2;      // M|鉴权TOKEN|字串|
    required string app = 3;        // M|APP名|字串|
    required string version = 4;    // M|APP版本|字串|
}`

---
命令ID: 0x0102<br>
命令描述: 上线请求应答(ONLINE-ACK)<br>
协议格式:<br>
`message mesg_online_ack<br>
{<br>
    required uint32 sid = 1;        // M|会话ID|数字|
    required string app = 2;        // M|APP名|字串|
    required string version = 3;    // M|APP版本|字串|
    required uint32 code = 4;       // M|错误码|数字|
    required string errmsg = 5;     // M|错误描述|字串|
}`

---
命令ID: 0x0103<br>
命令描述: 下线请求(OFFLINE)<br>
协议格式: NONE

---
命令ID: 0x0104<br>
命令描述: 下线请求应答(OFFLINE-ACK)<br>
协议格式: NONE<br>

---
命令ID: 0x0105<br>
命令描述: 客户端心跳(PING)<br>
协议格式: NONE

---
命令ID: 0x0106<br>
命令描述: 客户端心跳应答(PONG)<br>
协议格式: NONE

---
命令ID: 0x0107
命令描述: 踢连接下线(KICK)
协议格式: NONE
`message mesg_kick
{
    required uint32 code = 1;       // M|错误码|数字|
    required string errmsg = 2;     // M|错误描述|字串|
}`


命令ID: 0x0108
命令描述: 踢连接下线应答(KICK-ACK)
协议格式: NONE


# 上报消息

---
插件信息(PLUGIN)
`message browser_plugin_info
{
    optional string name = 1; // 插件名称
    optional string desc = 2; // 插件描述
}`

用户代理信息
`message browser_useragent_info {
    optional string ua = 1; // 用户代理
}`

屏幕信息
`message browser_screen_info
{
    optional uint32 width = 1; // screen.width
    optional uint32 height = 2; // screen.height
    optional uint32 avail_width = 3; // screen.availWidth
    optional uint32 avail_height = 4; // screen.availHeight
    optional uint32 avail_left = 5; // screen.availLeft
    optional uint32 avail_top = 6; // screen.availTop
    optional uint32 outer_width = 7; // screen.outerWidth
    optional uint32 outer_height = 8; // screen.outerHeight
    optional uint32 inner_width = 9; // screen.innerWidth
    optional uint32 inner_height = 10; // screen.innerHeight
}`

---
命令ID: 0x0201
命令描述: 上报浏览器环境信息(BROWSER-ENV)
协议格式:
`message mesg_browser_env
{
    optional browser_plugin_info plugin = 1; // 插件信息
    optional browser_useragent_info ua = 2; // 用户代理
    optional browser_screen_info screen = 3; // 屏幕信息
}`

---
命令ID: 0x0202
命令描述: 上报浏览器环境信息应答(BROWSER-ENV-ACK)
协议格式:
`message mesg_browser_env_ack
{
    required uint32 code = 1;       // M|错误码|数字|
    required string errmsg = 2;     // M|错误描述|字串|
}`

---
控件定义
`enum ctrl_type
{
    CTL_IBX_USR = 0; // 用户名输入框
    CTL_IBX_PWD = 1; // 密码输入框
    CTL_IBX_IMG = 2; // 图形验证码输入框
    CTL_BTN_IMG = 3; // 图形验证码刷新按钮
    CTL_IBX_TEL = 4; // 手机号码输入框
    CTL_IBX_SMS = 5; // 手机验证码输入框
    CTL_BTN_SMS = 6; // 手机验证码获取按钮
    CTL_BTN_LGN = 7; // 登录按钮
}`

事件定义
`enum event_type
{
    EV_CHANGE = 0; // change事件
    EV_CLICK = 1; // 单击事件
    EV_DBLCLICK = 2; // 双击事件
    EV_FOCUS = 3; // 获取焦点
    EV_KEYDOWN = 4; // 按键（下）
    EV_KEYPRESS = 5; // 按键
    EV_KEYUP = 6; // 按键（上)
    EV_MOUSEDOWN = 7; // 鼠标（下）
    EV_MOUSEMOVE = 8; // 鼠标移动
    EV_MOUSEOUT = 9; // 鼠标移出
    EV_MOUSEOVER = 10; // 鼠标在某控件上
    EV_MOUSEUP = 11; // 鼠标（上）
    EV_TOUCHSTART = 12; // 触屏开始
    EV_TOUCHMOVE = 13; // 触屏移动
    EV_TOUCHEND = 14; // 触屏结束
    EV_TOUCHCANCEL = 15; // 触屏取消
}`

---
命令ID: 0x0203
命令描述: 上报事件统计信息(EVENT-STATISTIC)
协议格式:
`message mesg_event_statistic
{
    required ctrl_type ctrl = 1; // 控件类型
    required event_type event = 2; // 事件类型
    required uint32 count = 3; // 事件触发次数
}`

---
命令ID: 0x0204
命令描述: 上报事件统计信息应答(EVENT-STATISTIC-ACK)
协议格式:
`message mesg_event_statistic_ack
{
    required uint32 code = 1;       // M|错误码|数字|
    required string errmsg = 2;     // M|错误描述|字串|
}`

# 系统内部命令

---
命令ID: 0x0601<br>
命令描述: 帧听层信息上报(LSN-INFO)<br>
协议格式: <br>
>message mesg_lsn_info<br>
>{<br>
>   required uint32 type = 1;       // M|类型(0:Unknown 1:TCP 2:WS)|数字|<br>
>   required uint32 nid = 2;        // M|结点ID|数字|<br>
>   required string nation = 3;     // M|所属国家|字串|<br>
>   required string name = 4;       // M|运营商名称|字串|<br>
>   required string ip = 5;         // M|IP地址|字串|<br>
>   required uint32 port = 6;       // M|端口|数字|<br>
>   required uint32 connections = 7;   // M|在线连接数|数字|<br>
>}

---
命令ID: 0x0602<br>
命令描述: 帧听层上报应答(LSN-INFO-ACK)<br>
协议格式: NONE<br>

---
命令ID: 0x0603<br>
命令描述: 转发层上报 (FRWD-INFO)<br>
协议格式: <br>
>message mesg_frwd_info<br>
>{<br>
>   required uint32 nid = 1;        // M|结点ID|数字|<br>
>   required string ip = 2;         // M|IP地址|字串|<br>
>   required uint32 forward_port = 3;    // M|前端口号|数字|<br>
>   required uint32 backend_port = 4;    // M|后端口号|数字|<br>
>}

---
命令ID: 0x0604<br>
命令描述: 转发层上报应答(FRWD-INFO-ACK)<br>
协议格式: NONE<br>
