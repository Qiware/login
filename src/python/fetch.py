# -*- coding: utf-8 -*-
import os
import re
import cgi
import sys
import time
import json
import redis
import numpy
import thread
import logging
import urllib2
import urlparse
import SocketServer
import SimpleHTTPServer
import io,shutil,urllib

import xlrd
import xlwt
import xlutils
from xlutils.copy import copy

from sklearn import tree

reload(sys)
sys.setdefaultencoding('utf8')

type = sys.getfilesystemencoding()

COL_RESERVED = 1
## 浏览器环境
COL_PLUGIN_HAS_NAME = 0
COL_PLUGIN_HAS_DESC = 1
COL_UA_EXISTS       = 2
## 屏幕信息
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
## 事件信息
## A - 用户名输入框
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
## B - 密码输入框
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
## C - 验证码输入框
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
## D - 验证码刷新按钮
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
## E - 手机号输入框
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
## H - 手机验证码输入框(FOR TEL)
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
## I - 手机验证码获取按钮(FOR TEL)
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
## J - 登录按钮
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
## 时间信息
COL_TIME_DIFF_SEC = 130

DescMap = {
    # 浏览器环境
    COL_PLUGIN_HAS_NAME : '存在插件名:',
    COL_PLUGIN_HAS_DESC : '存在插件描述:',
    COL_UA_EXISTS : '存在代理:',
    # 屏幕信息
    COL_SCREEN_WIDTH : '屏幕宽度:',
    COL_SCREEN_HEIGH : '屏幕高度:',
    COL_SCREEN_AVAIL_WIDTH : '屏幕AVAIL宽度:',
    COL_SCREEN_AVAIL_HEIGH : '屏幕AVAIL高度:',
    COL_SCREEN_AVAIL_LEFT : '屏幕AVAIL左边距:',
    COL_SCREEN_AVAIL_TOP : '屏幕AVAIL顶边距:',
    COL_SCREEN_OUTER_WIDTH : '屏幕OUTER宽度:',
    COL_SCREEN_OUTER_HEIGH : '屏幕OUTER高度:',
    COL_SCREEN_INNER_WIDTH : '屏幕INNER宽度:',
    COL_SCREEN_INNER_HEIGH : '屏幕INNER高度:',
    # 事件信息
    ## A - 用户名输入框
    COL_EVENT_IBX_USR_CHANGE : '用户名CHANGE:',
    COL_EVENT_IBX_USR_CLICK : '用户名CLICK:',
    COL_EVENT_IBX_USR_DBLCLICK : '用户名DBLCLICK:',
    COL_EVENT_IBX_USR_FOCUS : '用户名FOCUS:',
    COL_EVENT_IBX_USR_KEYDOWN : '用户名KEYDOWN:',
    COL_EVENT_IBX_USR_KEYPRESS : '用户名KEYPRESS:',
    COL_EVENT_IBX_USR_KEYUP : '用户名KEYUP:',
    COL_EVENT_IBX_USR_MOUSEDOWN : '用户名MOUSEDOWN:',
    COL_EVENT_IBX_USR_MOUSEMOVE : '用户名MOUSEMOVE:',
    COL_EVENT_IBX_USR_MOUSEOUT : '用户名MOUSEOUT:',
    COL_EVENT_IBX_USR_MOUSEOVER : '用户名MOUSEOVER:',
    COL_EVENT_IBX_USR_MOUSEUP : '用户名MOUSEUP:',
    COL_EVENT_IBX_USR_TOUCHSTART : '用户名TOUCHSTART:',
    COL_EVENT_IBX_USR_TOUCHMOVE : '用户名TOUCHMOVE:',
    COL_EVENT_IBX_USR_TOUCHEND : '用户名TOUCHEND:',
    ## B - 密码输入框
    COL_EVENT_IBX_PWD_CHANGE : '密码CHANGE:',
    COL_EVENT_IBX_PWD_CLICK : '密码CLICK:',
    COL_EVENT_IBX_PWD_DBLCLICK : '密码DBLCLICK:',
    COL_EVENT_IBX_PWD_FOCUS : '密码FOCUS:',
    COL_EVENT_IBX_PWD_KEYDOWN : '密码KEYDOWN:',
    COL_EVENT_IBX_PWD_KEYPRESS : '密码KEYPRESS:',
    COL_EVENT_IBX_PWD_KEYUP : '密码KEYUP:',
    COL_EVENT_IBX_PWD_MOUSEDOWN : '密码MOUSEDOWN:',
    COL_EVENT_IBX_PWD_MOUSEMOVE : '密码MOUSEMOVE:',
    COL_EVENT_IBX_PWD_MOUSEOUT : '密码MOUSEOUT:',
    COL_EVENT_IBX_PWD_MOUSEOVER : '密码MOUSEOVER:',
    COL_EVENT_IBX_PWD_MOUSEUP : '密码MOUSEUP:',
    COL_EVENT_IBX_PWD_TOUCHSTART : '密码TOUCHSTART:',
    COL_EVENT_IBX_PWD_TOUCHMOVE : '密码TOUCHMOVE:',
    COL_EVENT_IBX_PWD_TOUCHEND : '密码TOUCHEND:',
    ## C - 验证码输入框
    COL_EVENT_IBX_IMG_CHANGE : '图片验证码CHANGE:',
    COL_EVENT_IBX_IMG_CLICK : '图片验证码CLICK:',
    COL_EVENT_IBX_IMG_DBLCLICK : '图片验证码DBLCLICK:',
    COL_EVENT_IBX_IMG_FOCUS : '图片验证码FOCUS:',
    COL_EVENT_IBX_IMG_KEYDOWN : '图片验证码KEYDOWN:',
    COL_EVENT_IBX_IMG_KEYPRESS : '图片验证码KEYPRESS:',
    COL_EVENT_IBX_IMG_KEYUP : '图片验证码KEYUP:',
    COL_EVENT_IBX_IMG_MOUSEDOWN : '图片验证码MOUSEDOWN:',
    COL_EVENT_IBX_IMG_MOUSEMOVE : '图片验证码MOUSEMOVE:',
    COL_EVENT_IBX_IMG_MOUSEOUT : '图片验证码MOUSEOUT:',
    COL_EVENT_IBX_IMG_MOUSEOVER : '图片验证码MOUSEOVER:',
    COL_EVENT_IBX_IMG_MOUSEUP : '图片验证码MOUSEUP:',
    COL_EVENT_IBX_IMG_TOUCHSTART : '图片验证码TOUCHSTART:',
    COL_EVENT_IBX_IMG_TOUCHMOVE : '图片验证码TOUCHMOVE:',
    COL_EVENT_IBX_IMG_TOUCHEND : '图片验证码TOUCHEND:',
    ## D - 验证码刷新按钮
    COL_EVENT_BTN_IMG_CLICK : '图片验证码刷新CLICK:',
    COL_EVENT_BTN_IMG_DBLCLICK : '图片验证码刷新DBLCLICK:',
    COL_EVENT_BTN_IMG_FOCUS : '图片验证码刷新FOCUS:',
    COL_EVENT_BTN_IMG_KEYDOWN : '图片验证码刷新KEYDOWN:',
    COL_EVENT_BTN_IMG_KEYPRESS : '图片验证码刷新KEYPRESS:',
    COL_EVENT_BTN_IMG_KEYUP : '图片验证码刷新KEYUP:',
    COL_EVENT_BTN_IMG_MOUSEDOWN : '图片验证码刷新MOUSEDOWN:',
    COL_EVENT_BTN_IMG_MOUSEMOVE : '图片验证码刷新MOUSEMOVE:',
    COL_EVENT_BTN_IMG_MOUSEOUT : '图片验证码刷新MOUSEOUT:',
    COL_EVENT_BTN_IMG_MOUSEOVER : '图片验证码刷新MOUSEOVER:',
    COL_EVENT_BTN_IMG_MOUSEUP : '图片验证码刷新MOUSEUP:',
    COL_EVENT_BTN_IMG_TOUCHSTART : '图片验证码刷新TOUCHSTART:',
    COL_EVENT_BTN_IMG_TOUCHMOVE : '图片验证码刷新TOUCHMOVE:',
    COL_EVENT_BTN_IMG_TOUCHEND : '图片验证码刷新TOUCHEND:',
    ## E - 手机号输入框
    COL_EVENT_IBX_TEL_CHANGE : '手机号CHANGE:',
    COL_EVENT_IBX_TEL_CLICK : '手机号CLICK:',
    COL_EVENT_IBX_TEL_DBLCLICK : '手机号DBLCLICK:',
    COL_EVENT_IBX_TEL_FOCUS : '手机号FOCUS:',
    COL_EVENT_IBX_TEL_KEYDOWN : '手机号KEYDOWN:',
    COL_EVENT_IBX_TEL_KEYPRESS : '手机号KEYPRESS:',
    COL_EVENT_IBX_TEL_KEYUP : '手机号KEYUP:',
    COL_EVENT_IBX_TEL_MOUSEDOWN : '手机号MOUSEDOWN:',
    COL_EVENT_IBX_TEL_MOUSEMOVE : '手机号MOUSEMOVE:',
    COL_EVENT_IBX_TEL_MOUSEOUT : '手机号MOUSEOUT:',
    COL_EVENT_IBX_TEL_MOUSEOVER : '手机号MOUSEOVER:',
    COL_EVENT_IBX_TEL_MOUSEUP : '手机号MOUSEUP:',
    COL_EVENT_IBX_TEL_TOUCHSTART : '手机号TOUCHSTART:',
    COL_EVENT_IBX_TEL_TOUCHMOVE : '手机号TOUCHMOVE:',
    COL_EVENT_IBX_TEL_TOUCHEND : '手机号TOUCHEND:',
    ## F - 短信验证码输入框(FOR TEL)
    COL_EVENT_IBX_SMS_CHANGE : '短信CHANGE:',
    COL_EVENT_IBX_SMS_CLICK : '短信CLICK:',
    COL_EVENT_IBX_SMS_DBLCLICK : '短信DBLCLICK:',
    COL_EVENT_IBX_SMS_FOCUS : '短信FOCUS:',
    COL_EVENT_IBX_SMS_KEYDOWN : '短信KEYDOWN:',
    COL_EVENT_IBX_SMS_KEYPRESS : '短信KEYPRESS:',
    COL_EVENT_IBX_SMS_KEYUP : '短信KEYUP:',
    COL_EVENT_IBX_SMS_MOUSEDOWN : '短信MOUSEDOWN:',
    COL_EVENT_IBX_SMS_MOUSEMOVE : '短信MOUSEMOVE:',
    COL_EVENT_IBX_SMS_MOUSEOUT : '短信MOUSEOUT:',
    COL_EVENT_IBX_SMS_MOUSEOVER : '短信MOUSEOVER:',
    COL_EVENT_IBX_SMS_MOUSEUP : '短信MOUSEUP:',
    COL_EVENT_IBX_SMS_TOUCHSTART : '短信TOUCHSTART:',
    COL_EVENT_IBX_SMS_TOUCHMOVE : '短信TOUCHMOVE:',
    COL_EVENT_IBX_SMS_TOUCHEND : '短信TOUCHEND:',
    ## G - 短信验证码输入框(FOR TEL)
    COL_EVENT_BTN_SMS_CLICK : '短信按钮CLICK:',
    COL_EVENT_BTN_SMS_DBLCLICK : '短信按钮DBLCLICK:',
    COL_EVENT_BTN_SMS_FOCUS : '短信按钮FOCUS:',
    COL_EVENT_BTN_SMS_KEYDOWN : '短信按钮KEYDOWN:',
    COL_EVENT_BTN_SMS_KEYPRESS : '短信按钮KEYPRESS:',
    COL_EVENT_BTN_SMS_KEYUP : '短信按钮KEYUP:',
    COL_EVENT_BTN_SMS_MOUSEDOWN : '短信按钮MOUSEDOWN:',
    COL_EVENT_BTN_SMS_MOUSEMOVE : '短信按钮MOUSEMOVE:',
    COL_EVENT_BTN_SMS_MOUSEOUT : '短信按钮MOUSEOUT:',
    COL_EVENT_BTN_SMS_MOUSEOVER : '短信按钮MOUSEOVER:',
    COL_EVENT_BTN_SMS_MOUSEUP : '短信按钮MOUSEUP:',
    COL_EVENT_BTN_SMS_TOUCHSTART : '短信按钮TOUCHSTART:',
    COL_EVENT_BTN_SMS_TOUCHMOVE : '短信按钮TOUCHMOVE:',
    COL_EVENT_BTN_SMS_TOUCHEND : '短信按钮TOUCHEND:',
    ## H - 登录按钮
    COL_EVENT_BTN_LGN_CLICK : '登录CLICK:',
    COL_EVENT_BTN_LGN_DBLCLICK : '登录DBLCLICK:',
    COL_EVENT_BTN_LGN_FOCUS : '登录FOCUS:',
    COL_EVENT_BTN_LGN_KEYDOWN : '登录KEYDOWN:',
    COL_EVENT_BTN_LGN_KEYPRESS : '登录KEYPRESS:',
    COL_EVENT_BTN_LGN_KEYUP : '登录KEYUP:',
    COL_EVENT_BTN_LGN_MOUSEDOWN : '登录MOUSEDOWN:',
    COL_EVENT_BTN_LGN_MOUSEMOVE : '登录MOUSEMOVE:',
    COL_EVENT_BTN_LGN_MOUSEOUT : '登录MOUSEOUT:',
    COL_EVENT_BTN_LGN_MOUSEOVER : '登录MOUSEOVER:',
    COL_EVENT_BTN_LGN_MOUSEUP : '登录MOUSEUP:',
    COL_EVENT_BTN_LGN_TOUCHSTART : '登录TOUCHSTART:',
    COL_EVENT_BTN_LGN_TOUCHMOVE : '登录TOUCHMOVE:',
    COL_EVENT_BTN_LGN_TOUCHEND : '登录TOUCHEND:',
    # 时间信息
    COL_TIME_DIFF_SEC : '间隔时间:'
}

################################################################################
################################################################################
# 对EXECL行列值进行转化
def execl_val_to_str(table, row_idx, col_idx):
    v = table.row(row_idx)[col_idx].value
    if type(v) is int or type(v) is float:
        return str(int(v))
    return v.encode("utf-8")

# 设置EXEL属性
def set_style(name, height, bold=False):
        style = xlwt.XFStyle() # 初始化样式

        #font = xlwt.Font() # 为样式创建字体
        #font.name = name # 'Times New Roman'
        #font.bold = bold
        #font.color_index = 4
        #font.height = height

        borders= xlwt.Borders()
        borders.left= 6
        borders.right= 6
        borders.top= 6
        borders.bottom= 6

        #style.font = font
        style.borders = borders

        return style

################################################################################
################################################################################
class Classifier(object):
    # 对象初始化
    def __init__(self):
        self.clf = tree.DecisionTreeClassifier()
        self.X = []
        self.Y = []
        return
    # 加载训练数据
    def load(self, fname):
        # 从XLSX中提取有效数据
        bk = xlrd.open_workbook(fname)
        if bk is None:
            print("Open [%s] failed!" % fname)
            exit(0)
        table = bk.sheet_by_name(u'SAMPLE')
        if table is None:
            print("Smaple data failed! fname:%s" % fname)
            exit(0)

        wb = copy(bk)
        r = 0
        for row in xrange(table.nrows):
            print("row:%d process:%f%%" % (row, row*1.0/table.nrows * 100))
            X = []
            Y = []
            r += 1
            # 加载所有属性
            for idx in range(COL_PLUGIN_HAS_NAME, COL_TIME_DIFF_SEC+1):
                col = idx + 1
                #print("uid:%s %s" % (uid, table.row(row)[col].value.split(":")[1]))
                #print("row:%d col:%d %s|%s" % (r, col, table.row(row)[col].value.split(":")[0], table.row(row)[col].value.split(":")[1]))
                X.append(float(table.row(row)[col].value.split(":")[1]))
            # 加载标注数据
            for idx in range(0, 1):
                col = idx
                Y.append(int(table.row(row)[col].value))
            self.X.append(X)
            self.Y.append(Y)

    # 进行训练处理
    def train(self):
        self.clf = self.clf.fit(self.X, self.Y)

    # 进行预测处理
    def predict(self, attr):
        return self.clf.predict(attr)

    # 批量预测处理
    def parse(self, fname):
        wb = xlwt.Workbook()
        wsheet = wb.add_sheet(u'SAMPLE', cell_overwrite_ok=True)
        wstyle = set_style('Times New Roman',220,True)

        # 从XLSX中提取有效数据
        bk = xlrd.open_workbook(fname)
        if bk is None:
            print("Open [%s] failed!" % fname)
            exit(0)
        table = bk.sheet_by_name(u'SAMPLE')
        if table is None:
            print("Smaple data failed! fname:%s" % fname)
            exit(0)

        # 加载所有行
        for row in xrange(table.nrows):
            X = []
            # 加载所有属性
            for idx in range(COL_PLUGIN_HAS_NAME, COL_TIME_DIFF_SEC+1):
                col = idx + 1
                X.append(float(table.row(row)[col].value.split(":")[1]))
                wsheet.write(row, col, table.row(row)[col].value, wstyle)
            Y = self.predict(X)
            wb.get_sheet(0).write(row, 0, unicode(int(Y)))

        # 调整所有列宽度
        for idx in range(COL_PLUGIN_HAS_NAME, COL_TIME_DIFF_SEC+1):
            col = wsheet.col(idx+1)
            col.width = 30 * 200;
        wb.save("./output.xlsx")

################################################################################
################################################################################

def ClassfierTrain():
    cls = Classifier()

    # 训练模型
    cls.load("./train/train-p-1.xlsx")
    cls.load("./train/train-p-2.xlsx")
    cls.load("./train/train-p-3.xlsx")

    cls.load("./train/train-r-1.xlsx")
    cls.load("./train/train-r-2.xlsx")

    cls.train()

    return cls

gClassfier = ClassfierTrain()
redis_pool = redis.ConnectionPool(host="10.110.98.220", port=19003, db=0)

################################################################################
################################################################################
# 获取会话SID
def GetSid(token):
    global redis_pool
    rds = redis.Redis(connection_pool=redis_pool)

    sid = rds.hget('ae:token:to:sid', token)
    if sid is None:
        return 0
    return int(sid)
# 获取统计数据
style = set_style('Times New Roman',220,True)
def GetStatistic(sheet, row, sid):
    global style
    global redis_pool
    rds = redis.Redis(connection_pool=redis_pool);

    statistic = rds.hgetall("ae:sid:%d:statistic" % (sid))
    if statistic is None:
        print("Get statistic failed! sid:%d" % sid)
        return None

    X = []
    # 浏览器环境
    ## 是否存在插件名
    col = 0
    if statistic.has_key(str(COL_PLUGIN_HAS_NAME)):
        X.append(1)
        item = unicode(DescMap[col] + '1')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    ## 是否存在描述信息
    col += 1
    if statistic.has_key(str(COL_PLUGIN_HAS_DESC)):
        X.append(1)
        item = unicode(DescMap[col] + '1')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    ## 是否存在用户代理
    col += 1
    if statistic.has_key(str(COL_UA_EXISTS)):
        X.append(1)
        item = unicode(DescMap[col] + '1')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档

    # 屏幕信息
    ## 屏幕宽度
    col += 1
    if statistic.has_key(str(COL_SCREEN_WIDTH)):
        X.append(int(statistic[str(COL_SCREEN_WIDTH)]))
        item = unicode(DescMap[col] + statistic[str(COL_SCREEN_WIDTH)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    ## 屏幕高度
    col += 1
    if statistic.has_key(str(COL_SCREEN_HEIGH)):
        X.append(int(statistic[str(COL_SCREEN_HEIGH)]))
        item = unicode(DescMap[col] + statistic[str(COL_SCREEN_HEIGH)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    ## 屏幕AVAIL宽度
    col += 1
    if statistic.has_key(str(COL_SCREEN_AVAIL_WIDTH)):
        X.append(int(statistic[str(COL_SCREEN_AVAIL_WIDTH)]))
        item = unicode(DescMap[col] + statistic[str(COL_SCREEN_AVAIL_WIDTH)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    ## 屏幕AVAIL高度
    col += 1
    if statistic.has_key(str(COL_SCREEN_AVAIL_HEIGH)):
        X.append(int(statistic[str(COL_SCREEN_AVAIL_HEIGH)]))
        item = unicode(DescMap[col] + statistic[str(COL_SCREEN_AVAIL_HEIGH)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    ## 屏幕AVAIL左边距
    col += 1
    if statistic.has_key(str(COL_SCREEN_AVAIL_LEFT)):
        X.append(int(statistic[str(COL_SCREEN_AVAIL_LEFT)]))
        item = unicode(DescMap[col] + statistic[str(COL_SCREEN_AVAIL_LEFT)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    ## 屏幕AVAIL顶部
    col += 1
    if statistic.has_key(str(COL_SCREEN_AVAIL_TOP)):
        X.append(int(statistic[str(COL_SCREEN_AVAIL_TOP)]))
        item = unicode(DescMap[col] + statistic[str(COL_SCREEN_AVAIL_TOP)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    ## 屏幕OUTER宽度
    col += 1
    if statistic.has_key(str(COL_SCREEN_OUTER_WIDTH)):
        X.append(int(statistic[str(COL_SCREEN_OUTER_WIDTH)]))
        item = unicode(DescMap[col] + statistic[str(COL_SCREEN_OUTER_WIDTH)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    ## 屏幕OUTER高度
    col += 1
    if statistic.has_key(str(COL_SCREEN_OUTER_HEIGH)):
        X.append(int(statistic[str(COL_SCREEN_OUTER_HEIGH)]))
        item = unicode(DescMap[col] + statistic[str(COL_SCREEN_OUTER_HEIGH)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    ## 屏幕INNER宽度
    col += 1
    if statistic.has_key(str(COL_SCREEN_INNER_WIDTH)):
        X.append(int(statistic[str(COL_SCREEN_INNER_WIDTH)]))
        item = unicode(DescMap[col] + statistic[str(COL_SCREEN_INNER_WIDTH)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    ## 屏幕INNER高度
    col += 1
    if statistic.has_key(str(COL_SCREEN_INNER_HEIGH)):
        X.append(int(statistic[str(COL_SCREEN_INNER_HEIGH)]))
        item = unicode(DescMap[col] + statistic[str(COL_SCREEN_INNER_HEIGH)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档

    # 事件信息
    # A - 用户名输入框
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_USR_CHANGE)):
        X.append(int(statistic[str(COL_EVENT_IBX_USR_CHANGE)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_USR_CHANGE)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_USR_CLICK)):
        X.append(int(statistic[str(COL_EVENT_IBX_USR_CLICK)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_USR_CLICK)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_USR_DBLCLICK)):
        X.append(int(statistic[str(COL_EVENT_IBX_USR_DBLCLICK)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_USR_DBLCLICK)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_USR_FOCUS)):
        X.append(int(statistic[str(COL_EVENT_IBX_USR_FOCUS)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_USR_FOCUS)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_USR_KEYDOWN)):
        X.append(int(statistic[str(COL_EVENT_IBX_USR_KEYDOWN)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_USR_KEYDOWN)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_USR_KEYPRESS)):
        X.append(int(statistic[str(COL_EVENT_IBX_USR_KEYPRESS)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_USR_KEYPRESS)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_USR_KEYUP)):
        X.append(int(statistic[str(COL_EVENT_IBX_USR_KEYUP)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_USR_KEYUP)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_USR_MOUSEDOWN)):
        X.append(int(statistic[str(COL_EVENT_IBX_USR_MOUSEDOWN)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_USR_MOUSEDOWN)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_USR_MOUSEMOVE)):
        X.append(int(statistic[str(COL_EVENT_IBX_USR_MOUSEMOVE)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_USR_MOUSEMOVE)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_USR_MOUSEOUT)):
        X.append(int(statistic[str(COL_EVENT_IBX_USR_MOUSEOUT)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_USR_MOUSEOUT)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_USR_MOUSEOVER)):
        X.append(int(statistic[str(COL_EVENT_IBX_USR_MOUSEOVER)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_USR_MOUSEOVER)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_USR_MOUSEUP)):
        X.append(int(statistic[str(COL_EVENT_IBX_USR_MOUSEUP)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_USR_MOUSEUP)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_USR_TOUCHSTART)):
        X.append(int(statistic[str(COL_EVENT_IBX_USR_TOUCHSTART)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_USR_TOUCHSTART)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_USR_TOUCHMOVE)):
        X.append(int(statistic[str(COL_EVENT_IBX_USR_TOUCHMOVE)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_USR_TOUCHMOVE)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_USR_TOUCHEND)):
        X.append(int(statistic[str(COL_EVENT_IBX_USR_TOUCHEND)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_USR_TOUCHEND)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档

    # B - 密码输入框
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_PWD_CHANGE)):
        X.append(int(statistic[str(COL_EVENT_IBX_PWD_CHANGE)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_PWD_CHANGE)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_PWD_CLICK)):
        X.append(int(statistic[str(COL_EVENT_IBX_PWD_CLICK)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_PWD_CLICK)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_PWD_DBLCLICK)):
        X.append(int(statistic[str(COL_EVENT_IBX_PWD_DBLCLICK)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_PWD_DBLCLICK)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    if statistic.has_key(str(COL_EVENT_IBX_PWD_FOCUS)):
        X.append(int(statistic[str(COL_EVENT_IBX_PWD_FOCUS)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_PWD_FOCUS)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_PWD_KEYDOWN)):
        X.append(int(statistic[str(COL_EVENT_IBX_PWD_KEYDOWN)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_PWD_KEYDOWN)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_PWD_KEYPRESS)):
        X.append(int(statistic[str(COL_EVENT_IBX_PWD_KEYPRESS)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_PWD_KEYPRESS)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_PWD_KEYUP)):
        X.append(int(statistic[str(COL_EVENT_IBX_PWD_KEYUP)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_PWD_KEYUP)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_PWD_MOUSEDOWN)):
        X.append(int(statistic[str(COL_EVENT_IBX_PWD_MOUSEDOWN)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_PWD_MOUSEDOWN)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_PWD_MOUSEMOVE)):
        X.append(int(statistic[str(COL_EVENT_IBX_PWD_MOUSEMOVE)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_PWD_MOUSEMOVE)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
    if statistic.has_key(str(COL_EVENT_IBX_PWD_MOUSEOUT)):
        X.append(int(statistic[str(COL_EVENT_IBX_PWD_MOUSEOUT)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_PWD_MOUSEOUT)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_PWD_MOUSEOVER)):
        X.append(int(statistic[str(COL_EVENT_IBX_PWD_MOUSEOVER)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_PWD_MOUSEOVER)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_PWD_MOUSEUP)):
        X.append(int(statistic[str(COL_EVENT_IBX_PWD_MOUSEUP)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_PWD_MOUSEUP)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_PWD_TOUCHSTART)):
        X.append(int(statistic[str(COL_EVENT_IBX_PWD_TOUCHSTART)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_PWD_TOUCHSTART)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_PWD_TOUCHMOVE)):
        X.append(int(statistic[str(COL_EVENT_IBX_PWD_TOUCHMOVE)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_PWD_TOUCHMOVE)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_PWD_TOUCHEND)):
        X.append(int(statistic[str(COL_EVENT_IBX_PWD_TOUCHEND)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_PWD_TOUCHEND)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    # C - 图形验证码输入框
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_IMG_CHANGE)):
        X.append(int(statistic[str(COL_EVENT_IBX_IMG_CHANGE)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_IMG_CHANGE)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_IMG_CLICK)):
        X.append(int(statistic[str(COL_EVENT_IBX_IMG_CLICK)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_IMG_CLICK)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_IMG_DBLCLICK)):
        X.append(int(statistic[str(COL_EVENT_IBX_IMG_DBLCLICK)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_IMG_DBLCLICK)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_IMG_FOCUS)):
        X.append(int(statistic[str(COL_EVENT_IBX_IMG_FOCUS)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_IMG_FOCUS)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_IMG_KEYDOWN)):
        X.append(int(statistic[str(COL_EVENT_IBX_IMG_KEYDOWN)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_IMG_KEYDOWN)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_IMG_KEYPRESS)):
        X.append(int(statistic[str(COL_EVENT_IBX_IMG_KEYPRESS)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_IMG_KEYPRESS)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_IMG_KEYUP)):
        X.append(int(statistic[str(COL_EVENT_IBX_IMG_KEYUP)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_IMG_KEYUP)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_IMG_MOUSEDOWN)):
        X.append(int(statistic[str(COL_EVENT_IBX_IMG_MOUSEDOWN)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_IMG_MOUSEDOWN)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_IMG_MOUSEMOVE)):
        X.append(int(statistic[str(COL_EVENT_IBX_IMG_MOUSEMOVE)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_IMG_MOUSEMOVE)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_IMG_MOUSEOUT)):
        X.append(int(statistic[str(COL_EVENT_IBX_IMG_MOUSEOUT)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_IMG_MOUSEOUT)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_IMG_MOUSEOVER)):
        X.append(int(statistic[str(COL_EVENT_IBX_IMG_MOUSEOVER)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_IMG_MOUSEOVER)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_IMG_MOUSEUP)):
        X.append(int(statistic[str(COL_EVENT_IBX_IMG_MOUSEUP)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_IMG_MOUSEUP)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_IMG_TOUCHSTART)):
        X.append(int(statistic[str(COL_EVENT_IBX_IMG_TOUCHSTART)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_IMG_TOUCHSTART)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_IMG_TOUCHMOVE)):
        X.append(int(statistic[str(COL_EVENT_IBX_IMG_TOUCHMOVE)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_IMG_TOUCHMOVE)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_IMG_TOUCHEND)):
        X.append(int(statistic[str(COL_EVENT_IBX_IMG_TOUCHEND)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_IMG_TOUCHEND)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档

    # D - 图形验证码刷新按钮
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_IMG_CLICK)):
        X.append(int(statistic[str(COL_EVENT_BTN_IMG_CLICK)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_IMG_CLICK)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_IMG_DBLCLICK)):
        X.append(int(statistic[str(COL_EVENT_BTN_IMG_DBLCLICK)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_IMG_DBLCLICK)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_IMG_FOCUS)):
        X.append(int(statistic[str(COL_EVENT_BTN_IMG_FOCUS)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_IMG_FOCUS)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_IMG_KEYDOWN)):
        X.append(int(statistic[str(COL_EVENT_BTN_IMG_KEYDOWN)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_IMG_KEYDOWN)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_IMG_KEYPRESS)):
        X.append(int(statistic[str(COL_EVENT_BTN_IMG_KEYPRESS)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_IMG_KEYPRESS)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_IMG_KEYUP)):
        X.append(int(statistic[str(COL_EVENT_BTN_IMG_KEYUP)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_IMG_KEYUP)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_IMG_MOUSEDOWN)):
        X.append(int(statistic[str(COL_EVENT_BTN_IMG_MOUSEDOWN)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_IMG_MOUSEDOWN)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_IMG_MOUSEMOVE)):
        X.append(int(statistic[str(COL_EVENT_BTN_IMG_MOUSEMOVE)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_IMG_MOUSEMOVE)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_IMG_MOUSEOUT)):
        X.append(int(statistic[str(COL_EVENT_BTN_IMG_MOUSEOUT)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_IMG_MOUSEOUT)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_IMG_MOUSEOVER)):
        X.append(int(statistic[str(COL_EVENT_BTN_IMG_MOUSEOVER)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_IMG_MOUSEOVER)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_IMG_MOUSEUP)):
        X.append(int(statistic[str(COL_EVENT_BTN_IMG_MOUSEUP)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_IMG_MOUSEUP)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_IMG_TOUCHSTART)):
        X.append(int(statistic[str(COL_EVENT_BTN_IMG_TOUCHSTART)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_IMG_TOUCHSTART)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_IMG_TOUCHMOVE)):
        X.append(int(statistic[str(COL_EVENT_BTN_IMG_TOUCHMOVE)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_IMG_TOUCHMOVE)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_IMG_TOUCHEND)):
        X.append(int(statistic[str(COL_EVENT_BTN_IMG_TOUCHEND)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_IMG_TOUCHEND)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档

    # E - 手机号输入框
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_TEL_CHANGE)):
        X.append(int(statistic[str(COL_EVENT_IBX_TEL_CHANGE)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_TEL_CHANGE)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_TEL_CLICK)):
        X.append(int(statistic[str(COL_EVENT_IBX_TEL_CLICK)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_TEL_CLICK)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_TEL_DBLCLICK)):
        X.append(int(statistic[str(COL_EVENT_IBX_TEL_DBLCLICK)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_TEL_DBLCLICK)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_TEL_FOCUS)):
        X.append(int(statistic[str(COL_EVENT_IBX_TEL_FOCUS)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_TEL_FOCUS)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_TEL_KEYDOWN)):
        X.append(int(statistic[str(COL_EVENT_IBX_TEL_KEYDOWN)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_TEL_KEYDOWN)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_TEL_KEYPRESS)):
        X.append(int(statistic[str(COL_EVENT_IBX_TEL_KEYPRESS)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_TEL_KEYPRESS)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_TEL_KEYUP)):
        X.append(int(statistic[str(COL_EVENT_IBX_TEL_KEYUP)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_TEL_KEYUP)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_TEL_MOUSEDOWN)):
        X.append(int(statistic[str(COL_EVENT_IBX_TEL_MOUSEDOWN)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_TEL_MOUSEDOWN)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_TEL_MOUSEMOVE)):
        X.append(int(statistic[str(COL_EVENT_IBX_TEL_MOUSEMOVE)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_TEL_MOUSEMOVE)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_TEL_MOUSEOUT)):
        X.append(int(statistic[str(COL_EVENT_IBX_TEL_MOUSEOUT)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_TEL_MOUSEOUT)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_TEL_MOUSEOVER)):
        X.append(int(statistic[str(COL_EVENT_IBX_TEL_MOUSEOVER)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_TEL_MOUSEOVER)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_TEL_MOUSEUP)):
        X.append(int(statistic[str(COL_EVENT_IBX_TEL_MOUSEUP)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_TEL_MOUSEUP)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_TEL_TOUCHSTART)):
        X.append(int(statistic[str(COL_EVENT_IBX_TEL_TOUCHSTART)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_TEL_TOUCHSTART)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_TEL_TOUCHMOVE)):
        X.append(int(statistic[str(COL_EVENT_IBX_TEL_TOUCHMOVE)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_TEL_TOUCHMOVE)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_TEL_TOUCHEND)):
        X.append(int(statistic[str(COL_EVENT_IBX_TEL_TOUCHEND)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_TEL_TOUCHEND)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档

    # H - 手机验证码输入框(FOR TEL)
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_SMS_CHANGE)):
        X.append(int(statistic[str(COL_EVENT_IBX_SMS_CHANGE)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_SMS_CHANGE)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_SMS_CLICK)):
        X.append(int(statistic[str(COL_EVENT_IBX_SMS_CLICK)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_SMS_CLICK)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_SMS_DBLCLICK)):
        X.append(int(statistic[str(COL_EVENT_IBX_SMS_DBLCLICK)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_SMS_DBLCLICK)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_SMS_FOCUS)):
        X.append(int(statistic[str(COL_EVENT_IBX_SMS_FOCUS)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_SMS_FOCUS)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_SMS_KEYDOWN)):
        X.append(int(statistic[str(COL_EVENT_IBX_SMS_KEYDOWN)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_SMS_KEYDOWN)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_SMS_KEYPRESS)):
        X.append(int(statistic[str(COL_EVENT_IBX_SMS_KEYPRESS)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_SMS_KEYPRESS)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_SMS_KEYUP)):
        X.append(int(statistic[str(COL_EVENT_IBX_SMS_KEYUP)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_SMS_KEYUP)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_SMS_MOUSEDOWN)):
        X.append(int(statistic[str(COL_EVENT_IBX_SMS_MOUSEDOWN)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_SMS_MOUSEDOWN)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_SMS_MOUSEMOVE)):
        X.append(int(statistic[str(COL_EVENT_IBX_SMS_MOUSEMOVE)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_SMS_MOUSEMOVE)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_SMS_MOUSEOUT)):
        X.append(int(statistic[str(COL_EVENT_IBX_SMS_MOUSEOUT)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_SMS_MOUSEOUT)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_SMS_MOUSEOVER)):
        X.append(int(statistic[str(COL_EVENT_IBX_SMS_MOUSEOVER)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_SMS_MOUSEOVER)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_SMS_MOUSEUP)):
        X.append(int(statistic[str(COL_EVENT_IBX_SMS_MOUSEUP)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_SMS_MOUSEUP)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_SMS_TOUCHSTART)):
        X.append(int(statistic[str(COL_EVENT_IBX_SMS_TOUCHSTART)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_SMS_TOUCHSTART)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_SMS_TOUCHMOVE)):
        X.append(int(statistic[str(COL_EVENT_IBX_SMS_TOUCHMOVE)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_SMS_TOUCHMOVE)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_IBX_SMS_TOUCHEND)):
        X.append(int(statistic[str(COL_EVENT_IBX_SMS_TOUCHEND)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_IBX_SMS_TOUCHEND)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档

    # I - 手机验证码获取按钮(FOR TEL)
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_SMS_CLICK)):
        X.append(int(statistic[str(COL_EVENT_BTN_SMS_CLICK)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_SMS_CLICK)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_SMS_DBLCLICK)):
        X.append(int(statistic[str(COL_EVENT_BTN_SMS_DBLCLICK)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_SMS_DBLCLICK)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_SMS_FOCUS)):
        X.append(int(statistic[str(COL_EVENT_BTN_SMS_FOCUS)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_SMS_FOCUS)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_SMS_KEYDOWN)):
        X.append(int(statistic[str(COL_EVENT_BTN_SMS_KEYDOWN)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_SMS_KEYDOWN)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_SMS_KEYPRESS)):
        X.append(int(statistic[str(COL_EVENT_BTN_SMS_KEYPRESS)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_SMS_KEYPRESS)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_SMS_KEYUP)):
        X.append(int(statistic[str(COL_EVENT_BTN_SMS_KEYUP)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_SMS_KEYUP)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_SMS_MOUSEDOWN)):
        X.append(int(statistic[str(COL_EVENT_BTN_SMS_MOUSEDOWN)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_SMS_MOUSEDOWN)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_SMS_MOUSEMOVE)):
        X.append(int(statistic[str(COL_EVENT_BTN_SMS_MOUSEMOVE)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_SMS_MOUSEMOVE)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_SMS_MOUSEOUT)):
        X.append(int(statistic[str(COL_EVENT_BTN_SMS_MOUSEOUT)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_SMS_MOUSEOUT)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_SMS_MOUSEOVER)):
        X.append(int(statistic[str(COL_EVENT_BTN_SMS_MOUSEOVER)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_SMS_MOUSEOVER)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_SMS_MOUSEUP)):
        X.append(int(statistic[str(COL_EVENT_BTN_SMS_MOUSEUP)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_SMS_MOUSEUP)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_SMS_TOUCHSTART)):
        X.append(int(statistic[str(COL_EVENT_BTN_SMS_TOUCHSTART)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_SMS_TOUCHSTART)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_SMS_TOUCHMOVE)):
        X.append(int(statistic[str(COL_EVENT_BTN_SMS_TOUCHMOVE)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_SMS_TOUCHMOVE)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_SMS_TOUCHEND)):
        X.append(int(statistic[str(COL_EVENT_BTN_SMS_TOUCHEND)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_SMS_TOUCHEND)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档

    # J - 登录按钮
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_LGN_CLICK)):
        X.append(int(statistic[str(COL_EVENT_BTN_LGN_CLICK)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_LGN_CLICK)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_LGN_DBLCLICK)):
        X.append(int(statistic[str(COL_EVENT_BTN_LGN_DBLCLICK)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_LGN_DBLCLICK)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_LGN_FOCUS)):
        X.append(int(statistic[str(COL_EVENT_BTN_LGN_FOCUS)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_LGN_FOCUS)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_LGN_KEYDOWN)):
        X.append(int(statistic[str(COL_EVENT_BTN_LGN_KEYDOWN)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_LGN_KEYDOWN)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_LGN_KEYPRESS)):
        X.append(int(statistic[str(COL_EVENT_BTN_LGN_KEYPRESS)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_LGN_KEYPRESS)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_LGN_KEYUP)):
        X.append(int(statistic[str(COL_EVENT_BTN_LGN_KEYUP)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_LGN_KEYUP)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_LGN_MOUSEDOWN)):
        X.append(int(statistic[str(COL_EVENT_BTN_LGN_MOUSEDOWN)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_LGN_MOUSEDOWN)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_LGN_MOUSEMOVE)):
        X.append(int(statistic[str(COL_EVENT_BTN_LGN_MOUSEMOVE)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_LGN_MOUSEMOVE)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_LGN_MOUSEOUT)):
        X.append(int(statistic[str(COL_EVENT_BTN_LGN_MOUSEOUT)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_LGN_MOUSEOUT)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_LGN_MOUSEOVER)):
        X.append(int(statistic[str(COL_EVENT_BTN_LGN_MOUSEOVER)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_LGN_MOUSEOVER)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_LGN_MOUSEUP)):
        X.append(int(statistic[str(COL_EVENT_BTN_LGN_MOUSEUP)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_LGN_MOUSEUP)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_LGN_TOUCHSTART)):
        X.append(int(statistic[str(COL_EVENT_BTN_LGN_TOUCHSTART)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_LGN_TOUCHSTART)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_LGN_TOUCHMOVE)):
        X.append(int(statistic[str(COL_EVENT_BTN_LGN_TOUCHMOVE)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_LGN_TOUCHMOVE)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    col += 1
    if statistic.has_key(str(COL_EVENT_BTN_LGN_TOUCHEND)):
        X.append(int(statistic[str(COL_EVENT_BTN_LGN_TOUCHEND)]))
        item = unicode(DescMap[col] + statistic[str(COL_EVENT_BTN_LGN_TOUCHEND)])
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档

    # 时间信息
    col += 1
    ctm = time.time()
    if statistic.has_key('UTM'): # 更新时间
        if int(statistic['UTM']) < ctm:
            #X.append(ctm - int(statistic['UTM')]))
            X.append(0)
            item = unicode(DescMap[col] + '0')
            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
        else:
            X.append(0)
            item = unicode(DescMap[col] + '0')
            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    else:
        X.append(0)
        item = unicode(DescMap[col] + '0')
        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
    print(X)
    return numpy.array(X).reshape(1, -1)

# 分析风险指数
def PredictRisk(X):
    global gClassfier

    return gClassfier.predict(X)

# 预测处理
def PredictByToken(sheet, row, token):
    global style
    risk = 10

    # 通过TOKEN获取SID
    sid = GetSid(token)
    if sid is None:
        logging.warning("Get sid by token failed!")
        # 发送预测结果
        mesg = {}
        mesg.setdefault("risk", risk)
        mesg.setdefault("token", token)
        mesg.setdefault("errmsg", "Get sid by token failed!")

        return json.dumps(mesg)

    # 通过SID获取统计数据
    X = GetStatistic(sheet, row, sid)
    if X is None:
        # 发送预测结果
        mesg = {}
        mesg.setdefault("risk", risk)
        mesg.setdefault("token", token)
        mesg.setdefault("errmsg", "Get data by token failed!")

        return json.dumps(mesg)

    # 进行风险预测
    risk = PredictRisk(X)

    sheet.write(row, 0, str(int(risk)), style) # 撰写EXECL文档

    # 发送预测结果
    mesg = {}
    mesg.setdefault("risk", int(risk))
    mesg.setdefault("token", token)
    mesg.setdefault("errmsg", "Ok")

    return json.dumps(mesg)

################################################################################
##函数名称: main
##功    能:
##输入参数:
##输出参数:
##返    回:
##实现描述:
##注意事项:
##作    者: # Qifeng.zou # 2017.04.14 16:54:32 #
################################################################################
if __name__ == "__main__":
    #global redis_pool
    rds = redis.Redis(connection_pool=redis_pool)

    # 新建EXECL文件
    wk = xlwt.Workbook()
    sheet = wk.add_sheet(u'SAMPLE', cell_overwrite_ok=True)

    # 获取TOKEN列表
    token_list = rds.zrangebyscore('ae:token:zset', 0, 9999999999999999999999999999)
    if token_list is None:
        print "Get token list failed!"
        exit(0)

    # 进行预测分析
    row = 0
    for token in token_list:
        PredictByToken(sheet, row, token)
        row += 1
        if row > 100:
            break

    # 调整文档格式
    for idx in range(COL_PLUGIN_HAS_NAME+COL_RESERVED, COL_TIME_DIFF_SEC+COL_RESERVED+1):
        col = sheet.col(idx)       #xlwt中是行和列都是从0开始计算的
        col.width=30*256
    wk.save('./sample.xlsx')
