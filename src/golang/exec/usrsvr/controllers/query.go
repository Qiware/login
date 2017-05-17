package controllers

import (
	"fmt"

	"ai-eye/src/golang/lib/comm"
)

type UsrSvrQueryCtrl struct {
	BaseController
}

func (this *UsrSvrQueryCtrl) Query() {
	//ctx := GetUsrSvrCtx()

	option := this.GetString("option")
	switch option {
	default:
	}

	this.Error(comm.ERR_SVR_INVALID_PARAM, fmt.Sprintf("Unsupport this option:%s", option))
	return
}
