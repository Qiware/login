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

//#IM系统REDIS键值定义列表
const (
	//|**宏**|**键值**|**类型**|**描述**|**备注**|
	AE_KEY_SID_ZSET = "ae:sid:zset"    //*| ZSET | 会话SID集合 | 成员:SID 分值:TTL |
	AE_KEY_SID_INCR = "ae:sid:incr"    //*| STRING | 会话SID增量器 | 只增不减 注意:sid不能为0 |
	AE_KEY_SID_ATTR = "ae:sid:%d:attr" //*| HASH | 会话SID属性 | 包含UID/NID |

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
