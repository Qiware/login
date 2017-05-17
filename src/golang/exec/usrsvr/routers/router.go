package routers

import (
	"github.com/astaxie/beego"

	"ai-eye/src/golang/exec/usrsvr/controllers"
)

/* > 设置路由回调 */
//  beego.Router("/api/list",&RestController{},"*:ListFood")
//  beego.Router("/api/create",&RestController{},"post:CreateFood")
//  beego.Router("/api/update",&RestController{},"put:UpdateFood")
//  beego.Router("/api/delete",&RestController{},"delete:DeleteFood")
func Router() {
	beego.Router("/im/iplist", &controllers.UsrSvrIplistCtrl{}, "get:Iplist")

	beego.Router("/im/query", &controllers.UsrSvrQueryCtrl{}, "get:Query")
	beego.Router("/im/config", &controllers.UsrSvrConfigCtrl{}, "get:Config")
}
