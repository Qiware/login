package comm

const (
	AE_FMT_IP_PORT_STR = "%s:%d" //| IP+PORT
)

/* 侦听层结点属性 */
const (
	AE_LSND_ATTR_ADDR       = "ATTR"        //| IP地址
	AE_LSND_ATTR_PORT       = "PORT"        //| 侦听PORT
	AE_LSND_ATTR_TYPE       = "TYPE"        //| 侦听层类型(0:未知 1:TCP 2:WS)
	AE_LSND_ATTR_STATUS     = "STATUS"      //| 侦听层状态
	AE_LSND_ATTR_CONNECTION = "CONNECTIONS" //| 在线连接数
)

/* 路由层结点属性 */
const (
	AE_FRWD_ATTR_ADDR     = "ATTR"     //| IP地址
	AE_FRWD_ATTR_BC_PORT  = "BC-PORT"  //| 后置PORT
	AE_FRWD_ATTR_FWD_PORT = "FWD-PORT" //| 前置PORT
)

/* 采集数据的维度(HASH表元素编号) */
const (
	// 浏览器环境
	COL_PLUGIN_HAS_NAME = 0
	COL_PLUGIN_HAS_DESC = 1
	COL_UA_EXISTS       = 2
	// 屏幕信息
	COL_SCREEN_WIDTH       = 3
	COL_SCREEN_HEIGH       = 4
	COL_SCREEN_AVAIL_WIDTH = 5
	COL_SCREEN_AVAIL_HEIGH = 6
	COL_SCREEN_AVAIL_LEFT  = 7
	COL_SCREEN_AVAIL_TOP   = 8
	COL_SCREEN_OUTER_WIDTH = 9
	COL_SCREEN_OUTER_HEIGH = 10
	COL_SCREEN_INNER_WIDTH = 11
	COL_SCREEN_INNER_HEIGH = 12
	// 事件信息
	// A - 用户名输入框
	COL_EVENT_IBX_USR_CHANGE     = 13
	COL_EVENT_IBX_USR_CLICK      = 14
	COL_EVENT_IBX_USR_DBLCLICK   = 15
	COL_EVENT_IBX_USR_FOCUS      = 16
	COL_EVENT_IBX_USR_KEYDOWN    = 17
	COL_EVENT_IBX_USR_KEYPRESS   = 18
	COL_EVENT_IBX_USR_KEYUP      = 19
	COL_EVENT_IBX_USR_MOUSEDOWN  = 20
	COL_EVENT_IBX_USR_MOUSEMOVE  = 21
	COL_EVENT_IBX_USR_MOUSEOUT   = 22
	COL_EVENT_IBX_USR_MOUSEOVER  = 23
	COL_EVENT_IBX_USR_MOUSEUP    = 24
	COL_EVENT_IBX_USR_TOUCHSTART = 25
	COL_EVENT_IBX_USR_TOUCHMOVE  = 26
	COL_EVENT_IBX_USR_TOUCHEND   = 27
	// B - 密码输入框
	COL_EVENT_IBX_PWD_CHANGE     = 28
	COL_EVENT_IBX_PWD_CLICK      = 29
	COL_EVENT_IBX_PWD_DBLCLICK   = 30
	COL_EVENT_IBX_PWD_FOCUS      = 31
	COL_EVENT_IBX_PWD_KEYDOWN    = 32
	COL_EVENT_IBX_PWD_KEYPRESS   = 33
	COL_EVENT_IBX_PWD_KEYUP      = 34
	COL_EVENT_IBX_PWD_MOUSEDOWN  = 35
	COL_EVENT_IBX_PWD_MOUSEMOVE  = 36
	COL_EVENT_IBX_PWD_MOUSEOUT   = 37
	COL_EVENT_IBX_PWD_MOUSEOVER  = 38
	COL_EVENT_IBX_PWD_MOUSEUP    = 39
	COL_EVENT_IBX_PWD_TOUCHSTART = 40
	COL_EVENT_IBX_PWD_TOUCHMOVE  = 41
	COL_EVENT_IBX_PWD_TOUCHEND   = 42
	// C - 验证码输入框
	COL_EVENT_IBX_IMG_CHANGE     = 43
	COL_EVENT_IBX_IMG_CLICK      = 44
	COL_EVENT_IBX_IMG_DBLCLICK   = 45
	COL_EVENT_IBX_IMG_FOCUS      = 46
	COL_EVENT_IBX_IMG_KEYDOWN    = 47
	COL_EVENT_IBX_IMG_KEYPRESS   = 48
	COL_EVENT_IBX_IMG_KEYUP      = 49
	COL_EVENT_IBX_IMG_MOUSEDOWN  = 50
	COL_EVENT_IBX_IMG_MOUSEMOVE  = 51
	COL_EVENT_IBX_IMG_MOUSEOUT   = 52
	COL_EVENT_IBX_IMG_MOUSEOVER  = 53
	COL_EVENT_IBX_IMG_MOUSEUP    = 54
	COL_EVENT_IBX_IMG_TOUCHSTART = 55
	COL_EVENT_IBX_IMG_TOUCHMOVE  = 56
	COL_EVENT_IBX_IMG_TOUCHEND   = 57
	// D - 验证码刷新按钮
	COL_EVENT_BTN_IMG_CLICK      = 58
	COL_EVENT_BTN_IMG_DBLCLICK   = 59
	COL_EVENT_BTN_IMG_FOCUS      = 60
	COL_EVENT_BTN_IMG_KEYDOWN    = 61
	COL_EVENT_BTN_IMG_KEYPRESS   = 62
	COL_EVENT_BTN_IMG_KEYUP      = 63
	COL_EVENT_BTN_IMG_MOUSEDOWN  = 64
	COL_EVENT_BTN_IMG_MOUSEMOVE  = 65
	COL_EVENT_BTN_IMG_MOUSEOUT   = 66
	COL_EVENT_BTN_IMG_MOUSEOVER  = 67
	COL_EVENT_BTN_IMG_MOUSEUP    = 68
	COL_EVENT_BTN_IMG_TOUCHSTART = 69
	COL_EVENT_BTN_IMG_TOUCHMOVE  = 70
	COL_EVENT_BTN_IMG_TOUCHEND   = 71
	// E - 手机号输入框
	COL_EVENT_IBX_TEL_CHANGE     = 72
	COL_EVENT_IBX_TEL_CLICK      = 73
	COL_EVENT_IBX_TEL_DBLCLICK   = 74
	COL_EVENT_IBX_TEL_FOCUS      = 75
	COL_EVENT_IBX_TEL_KEYDOWN    = 76
	COL_EVENT_IBX_TEL_KEYPRESS   = 77
	COL_EVENT_IBX_TEL_KEYUP      = 78
	COL_EVENT_IBX_TEL_MOUSEDOWN  = 79
	COL_EVENT_IBX_TEL_MOUSEMOVE  = 80
	COL_EVENT_IBX_TEL_MOUSEOUT   = 81
	COL_EVENT_IBX_TEL_MOUSEOVER  = 82
	COL_EVENT_IBX_TEL_MOUSEUP    = 83
	COL_EVENT_IBX_TEL_TOUCHSTART = 84
	COL_EVENT_IBX_TEL_TOUCHMOVE  = 85
	COL_EVENT_IBX_TEL_TOUCHEND   = 86
	// H - 手机验证码输入框(FOR TEL)
	COL_EVENT_IBX_SMS_CHANGE     = 87
	COL_EVENT_IBX_SMS_CLICK      = 88
	COL_EVENT_IBX_SMS_DBLCLICK   = 89
	COL_EVENT_IBX_SMS_FOCUS      = 90
	COL_EVENT_IBX_SMS_KEYDOWN    = 91
	COL_EVENT_IBX_SMS_KEYPRESS   = 92
	COL_EVENT_IBX_SMS_KEYUP      = 93
	COL_EVENT_IBX_SMS_MOUSEDOWN  = 94
	COL_EVENT_IBX_SMS_MOUSEMOVE  = 95
	COL_EVENT_IBX_SMS_MOUSEOUT   = 96
	COL_EVENT_IBX_SMS_MOUSEOVER  = 97
	COL_EVENT_IBX_SMS_MOUSEUP    = 98
	COL_EVENT_IBX_SMS_TOUCHSTART = 99
	COL_EVENT_IBX_SMS_TOUCHMOVE  = 100
	COL_EVENT_IBX_SMS_TOUCHEND   = 101
	// I - 手机验证码获取按钮(FOR TEL)
	COL_EVENT_BTN_SMS_CLICK      = 102
	COL_EVENT_BTN_SMS_DBLCLICK   = 103
	COL_EVENT_BTN_SMS_FOCUS      = 104
	COL_EVENT_BTN_SMS_KEYDOWN    = 105
	COL_EVENT_BTN_SMS_KEYPRESS   = 106
	COL_EVENT_BTN_SMS_KEYUP      = 107
	COL_EVENT_BTN_SMS_MOUSEDOWN  = 108
	COL_EVENT_BTN_SMS_MOUSEMOVE  = 109
	COL_EVENT_BTN_SMS_MOUSEOUT   = 110
	COL_EVENT_BTN_SMS_MOUSEOVER  = 111
	COL_EVENT_BTN_SMS_MOUSEUP    = 112
	COL_EVENT_BTN_SMS_TOUCHSTART = 113
	COL_EVENT_BTN_SMS_TOUCHMOVE  = 114
	COL_EVENT_BTN_SMS_TOUCHEND   = 115
	// J - 登录按钮
	COL_EVENT_BTN_LGN_CLICK      = 116
	COL_EVENT_BTN_LGN_DBLCLICK   = 117
	COL_EVENT_BTN_LGN_FOCUS      = 118
	COL_EVENT_BTN_LGN_KEYDOWN    = 119
	COL_EVENT_BTN_LGN_KEYPRESS   = 120
	COL_EVENT_BTN_LGN_KEYUP      = 121
	COL_EVENT_BTN_LGN_MOUSEDOWN  = 122
	COL_EVENT_BTN_LGN_MOUSEMOVE  = 123
	COL_EVENT_BTN_LGN_MOUSEOUT   = 124
	COL_EVENT_BTN_LGN_MOUSEOVER  = 125
	COL_EVENT_BTN_LGN_MOUSEUP    = 126
	COL_EVENT_BTN_LGN_TOUCHSTART = 127
	COL_EVENT_BTN_LGN_TOUCHMOVE  = 128
	COL_EVENT_BTN_LGN_TOUCHEND   = 129
	// 时间信息
	COL_TIME_DIFF_SEC = 130
)

//#IM系统REDIS键值定义列表
const (
	//|**宏**|**键值**|**类型**|**描述**|**备注**|
	AE_KEY_SID_ZSET     = "ae:sid:zset"     //*| ZSET | 会话SID集合 | 成员:SID 分值:TTL |
	AE_KEY_SID_INCR     = "ae:sid:incr"     //*| STRING | 会话SID增量器 | 只增不减 注意:sid不能为0 |
	AE_KEY_SID_ATTR     = "ae:sid:%d:attr"  //*| HASH | 会话SID属性 | 包含UID/NID |
	AE_KEY_TOKEN_ZSET   = "ae:token:zset"   //*| ZSET | 会话TOKEN集合 | 成员:TOKEN 分值:TTL |
	AE_KEY_TOKEN_TO_SID = "ae:token:to:sid" //*| HASH | 存储TOKEN->SID映射 | 无 |

	//|**宏**|**键值**|**类型**|**描述**|**备注**|
	// 统计数据
	AE_KEY_SID_STATISTIC = "ae:sid:%d:statistic" //| HASH | 会话采集数据 |

	//|**宏**|**键值**|**类型**|**描述**|**备注**|
	AE_KEY_LSND_TYPE_ZSET      = "ae:lsnd:type:zset"                           //| ZSET | 帧听层"类型"集合 | 成员:"网络类型" 分值:TTL |
	AE_KEY_LSND_NATION_ZSET    = "ae:lsnd:type:%d:nation:zset"                 //| ZSET | 某"类型"的帧听层"地区/国家"集合 | 成员:"国家/地区" 分值:TTL |
	AE_KEY_LSND_OP_ZSET        = "ae:lsnd:type:%d:nation:%s:op:zset"           //| ZSET | 帧听层"地区/国家"对应的运营商集合 | 成员:运营商名称 分值:TTL |
	AE_KEY_LSND_IP_ZSET        = "ae:lsnd:type:%d:nation:%s:op:%d:zset"        //| ZSET | 帧听层"地区/国家"-运营商对应的IP集合 | 成员:IP 分值:TTL |
	AE_KEY_LSND_OP_TO_NID_ZSET = "ae:lsnd:type:%d:nation:%s:op:%d:to:nid:zset" //| ZSET | 运营商帧听层NID集合 | 成员:NID 分值:TTL |
	AE_KEY_LSND_NID_ZSET       = "ae:lsnd:nid:zset"                            //| ZSET | 帧听层NID集合 | 成员:NID 分值:TTL |
	AE_KEY_LSND_ATTR           = "ae:lsnd:nid:%d:attr"                         //| HASH | 帧听层NID->地址 | 键:NID/值:外网IP+端口 |
	AE_KEY_LSND_ADDR_TO_NID    = "ae:lsnd:addr:to:nid"                         //| HASH | 转发层地址->NID | 键:内网IP+端口/值:NID |
	AE_KEY_FRWD_NID_ZSET       = "ae:frwd:nid:zset"                            //| ZSET | 转发层NID集合 | 成员:NID 分值:TTL |
	AE_KEY_FRWD_ATTR           = "ae:frwd:nid:%d:attr"                         //| HASH | 转发层NID->"地址/前置端口/后置端口"等信息
	AE_KEY_PREC_NUM_ZSET       = "ae::prec:num:zset"                           //| ZSET | 人数统计精度 | 成员:prec 分值:记录条数 |
	AE_KEY_PREC_USR_MAX_NUM    = "ae:usr:statis:prec:%d:max:num"               //| HASH | 某统计精度最大人数 | 键:时间/值:最大人数 |
	AE_KEY_PREC_USR_MIN_NUM    = "ae:usr:statis:prec:%d:min:num"               //| HASH | 某统计精度最少人数 | 键:时间/值:最少人数 |
)
