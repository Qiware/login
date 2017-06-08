package controllers

import (
	"errors"
	"sync"

	"github.com/astaxie/beego/logs"
	"github.com/garyburd/redigo/redis"

	"login/src/golang/lib/cache"
	"login/src/golang/lib/comm"
	"login/src/golang/lib/log"
	"login/src/golang/lib/rtmq"

	"login/src/golang/exec/usrsvr/controllers/conf"
)

/* 侦听层列表 */
type UsrSvrLsndList struct {
	sync.RWMutex                                  /* 读写锁 */
	list         map[string](map[uint32][]string) /* 侦听层列表:map[TCP/WS](map[国家/地区](map([运营商ID][]IP列表))) */
}

type UsrSvrLsndNetWork struct {
	sync.RWMutex                         /* 读写锁 */
	types        map[int]*UsrSvrLsndList /* 侦听层类型:map[网络类型]UsrSvrLsndList */
}

/* 侦听层列表 */
type UsrSvrThriftClient struct {
}

/* 用户中心上下文 */
type UsrSvrCntx struct {
	conf    *conf.UsrSvrConf  /* 配置信息 */
	log     *logs.BeeLogger   /* 日志对象 */
	ipdict  *comm.IpDict      /* IP字典 */
	frwder  *rtmq.Proxy       /* 代理对象 */
	redis   *redis.Pool       /* REDIS连接池 */
	listend UsrSvrLsndNetWork /* 侦听层类型 */
}

var g_usrsvr_cntx *UsrSvrCntx /* 全局对象 */

/* 获取全局对象 */
func GetUsrSvrCtx() *UsrSvrCntx {
	return g_usrsvr_cntx
}

/* 设置全局对象 */
func SetUsrSvrCtx(ctx *UsrSvrCntx) {
	g_usrsvr_cntx = ctx
}

/******************************************************************************
 **函数名称: UsrSvrInit
 **功    能: 初始化对象
 **输入参数:
 **     conf: 配置信息
 **输出参数: NONE
 **返    回:
 **     ctx: 上下文
 **     err: 错误信息
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2016.10.30 22:32:23 #
 ******************************************************************************/
func UsrSvrInit(conf *conf.UsrSvrConf) (ctx *UsrSvrCntx, err error) {
	ctx = &UsrSvrCntx{}

	ctx.conf = conf

	/* > 初始化日志 */
	ctx.log = log.Init(conf.Log.Level, conf.Log.Path, "usrsvr.log")
	if nil == ctx.log {
		return nil, errors.New("Initialize log failed!")
	}

	/* > 加载IP字典 */
	ctx.ipdict, err = comm.LoadIpDict("../conf/ipdict.txt")
	if nil != err {
		return nil, err
	}

	///* > 创建侦听层列表 */
	ctx.listend.types = make(map[int]*UsrSvrLsndList)

	/* > REDIS连接池 */
	ctx.redis = cache.CreateRedisPool(conf.Redis.Addr, conf.Redis.Passwd, 2048)
	if nil == ctx.redis {
		ctx.log.Error("Create redis pool failed! addr:%s", conf.Redis.Addr)
		return nil, errors.New("Create redis pool failed!")
	}

	/* > 初始化RTMQ-PROXY */
	ctx.frwder = rtmq.ProxyInit(&conf.Frwder, ctx.log)
	if nil == ctx.frwder {
		return nil, err
	}

	SetUsrSvrCtx(ctx)

	return ctx, nil
}

/******************************************************************************
 **函数名称: Register
 **功    能: 注册处理回调
 **输入参数: NONE
 **输出参数: NONE
 **返    回: VOID
 **实现描述: 注册回调函数
 **注意事项: 请在调用Launch()前完成此函数调用
 **作    者: # Qifeng.zou # 2016.10.30 22:32:23 #
 ******************************************************************************/
func (ctx *UsrSvrCntx) Register() {
	/* > 通用消息 */
	ctx.frwder.Register(comm.CMD_ONLINE, UsrSvrOnlineHandler, ctx)
	ctx.frwder.Register(comm.CMD_OFFLINE, UsrSvrOfflineHandler, ctx)
	ctx.frwder.Register(comm.CMD_PING, UsrSvrPingHandler, ctx)
}

/******************************************************************************
 **函数名称: Launch
 **功    能: 启动USRSVR服务
 **输入参数: NONE
 **输出参数: NONE
 **返    回: VOID
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2016.10.30 22:32:23 #
 ******************************************************************************/
func (ctx *UsrSvrCntx) Launch() {
	ctx.frwder.Launch()

	go ctx.start_task()
}
