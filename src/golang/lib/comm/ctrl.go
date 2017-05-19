package comm

/* 控件列表 */
const (
	CTL_IBX_USR = 0 // 输入框: 用户名
	CTL_IBX_PWD = 1 // 输入框: 密码
	CTL_IBX_IMG = 2 // 输入框: 图形验证码
	CTL_BTN_IMG = 3 // 按钮: 图形验证码刷新
	CTL_IBX_TEL = 4 // 输入框: 手机号码
	CTL_IBX_SMS = 5 // 输入框: 手机验证码
	CTL_BTN_SMS = 6 // 按钮: 手机验证码获取
	CTL_BTN_LGN = 7 // 按钮: 登录
)

/* 事件列表 */
const (
	EV_CHANGE     = 0  // 改变事件
	EV_CLICK      = 1  // 单击事件
	EV_DBLCLICK   = 2  // 双击事件
	EV_FOCUS      = 3  // 获取焦点
	EV_KEYDOWN    = 4  // 按键DOWN
	EV_KEYPRESS   = 5  // 按键
	EV_KEYUP      = 6  // 按键UP
	EV_MOUSEDOWN  = 7  // 鼠标DOWN
	EV_MOUSEMOVE  = 8  // 移动鼠标
	EV_MOUSEOUT   = 9  // 鼠标OUT
	EV_MOUSEOVER  = 10 // 鼠标OVER
	EV_MOUSEUP    = 11 // 鼠标UP
	EV_TOUCHSTART = 12 // 触屏开始
	EV_TOUCHMOVE  = 13 // 触屏移动
	EV_TOUCHEND   = 14 // 触屏结束
)
