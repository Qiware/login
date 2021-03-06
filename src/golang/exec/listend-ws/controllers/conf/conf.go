package conf

import (
	"os"
	"path/filepath"

	"login/src/golang/lib/log"
	"login/src/golang/lib/lws"
	"login/src/golang/lib/rtmq"
)

/* 侦听层配置 */
type LsndConf struct {
	Id        uint32                  // 结点ID
	Gid       uint32                  // 分组ID
	WorkPath  string                  // 工作路径(自动获取)
	AppPath   string                  // 程序路径(自动获取)
	ConfPath  string                  // 配置路径(自动获取)
	Log       log.Conf                // 日志配置
	Operator  LsndConfOperatorXmlData // 运营商信息
	WebSocket lws.Conf                // WEBSOCKET配置
	Frwder    rtmq.ProxyConf          // RTMQ配置
}

/******************************************************************************
 **函数名称: Load
 **功    能: 加载配置信息
 **输入参数:
 **     path: 配置路径
 **输出参数: NONE
 **返    回:
 **     conf: 配置信息
 **     err: 错误描述
 **实现描述:
 **注意事项:
 **作    者: # Qifeng.zou # 2016.10.30 22:35:28 #
 ******************************************************************************/
func Load(path string) (conf *LsndConf, err error) {
	conf = &LsndConf{}
	conf.WorkPath, _ = os.Getwd()
	conf.WorkPath, _ = filepath.Abs(conf.WorkPath)
	conf.AppPath, _ = filepath.Abs(filepath.Dir(os.Args[0]))
	conf.ConfPath = path

	err = conf.parse()
	if nil != err {
		return nil, err
	}
	return conf, err
}

/* 获取结点ID */
func (conf *LsndConf) GetNid() uint32 {
	return conf.Id
}

/* 获取分组ID */
func (conf *LsndConf) GetGid() uint32 {
	return conf.Gid
}

/* 获取运营商ID */
func (conf *LsndConf) GetOpid() uint32 {
	return conf.Operator.Id
}

/* 获取国家 */
func (conf *LsndConf) GetNation() string {
	return conf.Operator.Nation
}

/* 获取IP地址 */
func (conf *LsndConf) GetIp() string {
	return conf.WebSocket.Ip
}

/* 获取绑定端口 */
func (conf *LsndConf) GetPort() uint32 {
	return conf.WebSocket.Port
}
