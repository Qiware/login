package routers

import (
	"github.com/astaxie/beego"

	"login/src/golang/exec/usrsvr/controllers"
)

/* > 设置路由回调 */
//  beego.Router("/api/list",&RestController{},"*:ListFood")
//  beego.Router("/api/create",&RestController{},"post:CreateFood")
//  beego.Router("/api/update",&RestController{},"put:UpdateFood")
//  beego.Router("/api/delete",&RestController{},"delete:DeleteFood")
func Router() {
	beego.Router("/system/iplist", &controllers.UsrSvrIplistCtrl{}, "get:Iplist")

	beego.Router("/system/query", &controllers.UsrSvrQueryCtrl{}, "get:Query")
	beego.Router("/system/config", &controllers.UsrSvrConfigCtrl{}, "get:Config")
}
