# -*- coding: utf-8 -*-
import os
import re
import cgi
import sys
import time
import json
import redis
import thread
import logging
import urllib2
import urlparse
import SocketServer
import SimpleHTTPServer
import io,shutil,urllib

from sklearn import tree

sys.path.append("3rd/xlrd")
sys.path.append("3rd/xlwt")
sys.path.append("3rd/xlutils")
import xlrd
import xlwt
import xlutils
from xlutils.copy import copy

reload(sys)
sys.setdefaultencoding('utf8')

type = sys.getfilesystemencoding()

# 密钥
CIPHER = "%b@e!e@h@i#v@e$s$tVu^d(i(o"

# 浏览器环境
COL_PLUGIN_HAS_NAME = 0
COL_PLUGIN_HAS_DESC = 1
COL_UA_EXISTS = 2

# 屏幕信息
COL_SCREEN_WIDTH = 3
COL_SCREEN_HEIGH = 4
COL_SCREEN_AVAIL_WIDTH = 5
COL_SCREEN_AVAIL_HEIGH = 6
COL_SCREEN_AVAIL_LEFT = 7
COL_SCREEN_AVAIL_TOP = 8
COL_SCREEN_OUTER_WIDTH = 9
COL_SCREEN_OUTER_HEIGH = 10
COL_SCREEN_INNER_WIDTH = 11
COL_SCREEN_INNER_HEIGH = 12

# 事件信息
# A - 用户名输入框
COL_EVENT_IBX_USR_CHANGE = 13
COL_EVENT_IBX_USR_CLICK = 14
COL_EVENT_IBX_USR_DBLCLICK = 15
COL_EVENT_IBX_USR_FOCUS = 16
COL_EVENT_IBX_USR_KEYDOWN = 17
COL_EVENT_IBX_USR_KEYPRESS = 18
COL_EVENT_IBX_USR_KEYUP = 19
COL_EVENT_IBX_USR_MOUSEDOWN = 20
COL_EVENT_IBX_USR_MOUSEMOVE = 21
COL_EVENT_IBX_USR_MOUSEOUT = 22
COL_EVENT_IBX_USR_MOUSEOVER = 23
COL_EVENT_IBX_USR_MOUSEUP = 24
COL_EVENT_IBX_USR_TOUCHSTART = 25
COL_EVENT_IBX_USR_TOUCHMOVE = 26
COL_EVENT_IBX_USR_TOUCHEND = 27
COL_EVENT_IBX_USR_TOUCHCANCEL = 28

# B - 密码输入框
COL_EVENT_IBX_PWD_CHANGE = 29
COL_EVENT_IBX_PWD_CLICK = 30
COL_EVENT_IBX_PWD_DBLCLICK = 31
COL_EVENT_IBX_PWD_FOCUS = 32
COL_EVENT_IBX_PWD_KEYDOWN = 33
COL_EVENT_IBX_PWD_KEYPRESS = 34
COL_EVENT_IBX_PWD_KEYUP = 35
COL_EVENT_IBX_PWD_MOUSEDOWN = 36
COL_EVENT_IBX_PWD_MOUSEMOVE = 37
COL_EVENT_IBX_PWD_MOUSEOUT = 38
COL_EVENT_IBX_PWD_MOUSEOVER = 39
COL_EVENT_IBX_PWD_MOUSEUP = 40
COL_EVENT_IBX_PWD_TOUCHSTART = 41
COL_EVENT_IBX_PWD_TOUCHMOVE = 42
COL_EVENT_IBX_PWD_TOUCHEND = 43
COL_EVENT_IBX_PWD_TOUCHCANCEL = 44

# C - 图形验证码输入框
COL_EVENT_IBX_IMG_CHANGE      = 45
COL_EVENT_IBX_IMG_CLICK       = 46
COL_EVENT_IBX_IMG_DBLCLICK    = 47
COL_EVENT_IBX_IMG_FOCUS       = 48
COL_EVENT_IBX_IMG_KEYDOWN     = 49
COL_EVENT_IBX_IMG_KEYPRESS    = 50
COL_EVENT_IBX_IMG_KEYUP       = 51
COL_EVENT_IBX_IMG_MOUSEDOWN   = 52
COL_EVENT_IBX_IMG_MOUSEMOVE   = 53
COL_EVENT_IBX_IMG_MOUSEOUT    = 54
COL_EVENT_IBX_IMG_MOUSEOVER   = 55
COL_EVENT_IBX_IMG_MOUSEUP     = 56
COL_EVENT_IBX_IMG_TOUCHSTART  = 57
COL_EVENT_IBX_IMG_TOUCHMOVE   = 58
COL_EVENT_IBX_IMG_TOUCHEND    = 59
COL_EVENT_IBX_IMG_TOUCHCANCEL = 60

# D - 图形验证码刷新按钮
COL_EVENT_BTN_IMG_CLICK       = 61
COL_EVENT_BTN_IMG_DBLCLICK    = 62
COL_EVENT_BTN_IMG_FOCUS       = 63
COL_EVENT_BTN_IMG_KEYDOWN     = 64
COL_EVENT_BTN_IMG_KEYPRESS    = 65
COL_EVENT_BTN_IMG_KEYUP       = 66
COL_EVENT_BTN_IMG_MOUSEDOWN   = 67
COL_EVENT_BTN_IMG_MOUSEMOVE   = 68
COL_EVENT_BTN_IMG_MOUSEOUT    = 69
COL_EVENT_BTN_IMG_MOUSEOVER   = 70
COL_EVENT_BTN_IMG_MOUSEUP     = 71
COL_EVENT_BTN_IMG_TOUCHSTART  = 72
COL_EVENT_BTN_IMG_TOUCHMOVE   = 73
COL_EVENT_BTN_IMG_TOUCHEND    = 74
COL_EVENT_BTN_IMG_TOUCHCANCEL = 75

# E - 手机号输入框
COL_EVENT_IBX_TEL_CHANGE      = 76
COL_EVENT_IBX_TEL_CLICK       = 77
COL_EVENT_IBX_TEL_DBLCLICK    = 78
COL_EVENT_IBX_TEL_FOCUS       = 79
COL_EVENT_IBX_TEL_KEYDOWN     = 80
COL_EVENT_IBX_TEL_KEYPRESS    = 81
COL_EVENT_IBX_TEL_KEYUP       = 82
COL_EVENT_IBX_TEL_MOUSEDOWN   = 83
COL_EVENT_IBX_TEL_MOUSEMOVE   = 84
COL_EVENT_IBX_TEL_MOUSEOUT    = 85
COL_EVENT_IBX_TEL_MOUSEOVER   = 86
COL_EVENT_IBX_TEL_MOUSEUP     = 87
COL_EVENT_IBX_TEL_TOUCHSTART  = 88
COL_EVENT_IBX_TEL_TOUCHMOVE   = 89
COL_EVENT_IBX_TEL_TOUCHEND    = 90
COL_EVENT_IBX_TEL_TOUCHCANCEL = 91

# H - 手机验证码输入框(FOR TEL)
COL_EVENT_IBX_SMS_CHANGE      = 92
COL_EVENT_IBX_SMS_CLICK       = 93
COL_EVENT_IBX_SMS_DBLCLICK    = 94
COL_EVENT_IBX_SMS_FOCUS       = 95
COL_EVENT_IBX_SMS_KEYDOWN     = 96
COL_EVENT_IBX_SMS_KEYPRESS    = 97
COL_EVENT_IBX_SMS_KEYUP       = 98
COL_EVENT_IBX_SMS_MOUSEDOWN   = 99
COL_EVENT_IBX_SMS_MOUSEMOVE   = 100
COL_EVENT_IBX_SMS_MOUSEOUT    = 101
COL_EVENT_IBX_SMS_MOUSEOVER   = 102
COL_EVENT_IBX_SMS_MOUSEUP     = 103
COL_EVENT_IBX_SMS_TOUCHSTART  = 104
COL_EVENT_IBX_SMS_TOUCHMOVE   = 105
COL_EVENT_IBX_SMS_TOUCHEND    = 106
COL_EVENT_IBX_SMS_TOUCHCANCEL = 107

# I - 手机验证码获取按钮(FOR TEL)
COL_EVENT_BTN_SMS_CLICK       = 108
COL_EVENT_BTN_SMS_DBLCLICK    = 109
COL_EVENT_BTN_SMS_FOCUS       = 110
COL_EVENT_BTN_SMS_KEYDOWN     = 111
COL_EVENT_BTN_SMS_KEYPRESS    = 112
COL_EVENT_BTN_SMS_KEYUP       = 113
COL_EVENT_BTN_SMS_MOUSEDOWN   = 114
COL_EVENT_BTN_SMS_MOUSEMOVE   = 115
COL_EVENT_BTN_SMS_MOUSEOUT    = 116
COL_EVENT_BTN_SMS_MOUSEOVER   = 117
COL_EVENT_BTN_SMS_MOUSEUP     = 118
COL_EVENT_BTN_SMS_TOUCHSTART  = 119
COL_EVENT_BTN_SMS_TOUCHMOVE   = 120
COL_EVENT_BTN_SMS_TOUCHEND    = 121
COL_EVENT_BTN_SMS_TOUCHCANCEL = 122

# J - 登录按钮
COL_EVENT_BTN_LGN_CLICK       = 123
COL_EVENT_BTN_LGN_DBLCLICK    = 124
COL_EVENT_BTN_LGN_FOCUS       = 125
COL_EVENT_BTN_LGN_KEYDOWN     = 126
COL_EVENT_BTN_LGN_KEYPRESS    = 127
COL_EVENT_BTN_LGN_KEYUP       = 128
COL_EVENT_BTN_LGN_MOUSEDOWN   = 129
COL_EVENT_BTN_LGN_MOUSEMOVE   = 130
COL_EVENT_BTN_LGN_MOUSEOUT    = 131
COL_EVENT_BTN_LGN_MOUSEOVER   = 132
COL_EVENT_BTN_LGN_MOUSEUP     = 133
COL_EVENT_BTN_LGN_TOUCHSTART  = 134
COL_EVENT_BTN_LGN_TOUCHMOVE   = 135
COL_EVENT_BTN_LGN_TOUCHEND    = 136
COL_EVENT_BTN_LGN_TOUCHCANCEL = 137

# 时间信息
COL_TIME_DIFF_SEC = 138

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
            X = []
            Y = []
            r += 1
            # 加载所有属性
            for idx in range(COL_PLUGIN_HAS_NAME, COL_TIME_DIFF_SEC+1):
                col = idx + 1
                #print("uid:%s %s" % (uid, table.row(row)[col].value.split(":")[1]))
                print("row:%d col:%d %s|%s" % (r, col, table.row(row)[col].value.split(":")[0], table.row(row)[col].value.split(":")[1]))
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
    cls.load("./train/train-1.xlsx")

    cls.train()

    return cls

gClassfier = ClassfierTrain()
redis_pool = redis.ConnectionPool(host="10.130.212.77", port=19001, db=0)

################################################################################
################################################################################

class AiEyeHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    # 获取会话SID
    def GetSid(self, token):
        global redis_pool
        rds = redis.Redis(connection_pool=redis_pool)

        return rds.hget('ae:token:to:sid', token)
    # 获取统计数据
    def GetStatistic(self, sid):
        global redis_pool
        rds = redis.Redis(connection_pool=redis_pool);

        statistic = rds.hgetall("ae:sid:%d:statistic" % (sid))
        if statistic is None:
            return None

        X = []
        # 浏览器环境
        ## 是否存在插件名
        if statistic.has_key(COL_PLUGIN_HAS_NAME):
            X.append(1)
        else:
            X.append(0)
        ## 是否存在描述信息
        if statistic.has_key(COL_PLUGIN_HAS_DESC):
            X.append(1)
        else:
            X.append(0)
        ## 是否存在用户代理
        if statistic.has_key(COL_UA_EXISTS):
            X.append(1)
        else:
            X.append(0)

        # 屏幕信息
        ## 屏幕宽度
        if statistic.has_key(COL_SCREEN_WIDTH):
            X.append(int(statistic[COL_SCREEN_WIDTH]))
        else:
            X.append(0)
        ## 屏幕高度
        if statistic.has_key(COL_SCREEN_HEIGH):
            X.append(int(statistic[COL_SCREEN_HEIGH]))
        else:
            X.append(0)
        ## 屏幕AVAIL宽度
        if statistic.has_key(COL_SCREEN_AVAIL_WIDTH):
            X.append(int(statistic[COL_SCREEN_AVAIL_WIDTH]))
        else:
            X.append(0)
        ## 屏幕AVAIL高度
        if statistic.has_key(COL_SCREEN_AVAIL_HEIGH):
            X.append(int(statistic[COL_SCREEN_AVAIL_HEIGH]))
        else:
            X.append(0)
        ## 屏幕AVAIL左边距
        if statistic.has_key(COL_SCREEN_AVAIL_LEFT):
            X.append(int(statistic[COL_SCREEN_AVAIL_LEFT]))
        else:
            X.append(0)
        ## 屏幕AVAIL顶部
        if statistic.has_key(COL_SCREEN_AVAIL_TOP):
            X.append(int(statistic[COL_SCREEN_AVAIL_TOP]))
        else:
            X.append(0)
        ## 屏幕OUTER宽度
        if statistic.has_key(COL_SCREEN_OUTER_WIDTH):
            X.append(int(statistic[COL_SCREEN_OUTER_WIDTH]))
        else:
            X.append(0)
        ## 屏幕OUTER高度
        if statistic.has_key(COL_SCREEN_OUTER_HEIGH):
            X.append(int(statistic[COL_SCREEN_OUTER_HEIGH]))
        else:
            X.append(0)
        ## 屏幕INNER宽度
        if statistic.has_key(COL_SCREEN_INNER_WIDTH):
            X.append(int(statistic[COL_SCREEN_INNER_WIDTH]))
        else:
            X.append(0)
        COL_SCREEN_OUTER_HEIGH = 10
        ## 屏幕INNER高度
        if statistic.has_key(COL_SCREEN_OUTER_HEIGH):
            X.append(int(statistic[COL_SCREEN_OUTER_HEIGH]))
        else:
            X.append(0)

        # 事件信息
        # A - 用户名输入框
        if statistic.has_key(COL_EVENT_IBX_USR_CHANGE):
            X.append(int(statistic[COL_EVENT_IBX_USR_CHANGE]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_USR_CLICK):
            X.append(int(statistic[COL_EVENT_IBX_USR_CLICK]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_USR_DBLCLICK):
            X.append(int(statistic[COL_EVENT_IBX_USR_DBLCLICK]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_USR_FOCUS):
            X.append(int(statistic[COL_EVENT_IBX_USR_FOCUS]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_USR_KEYDOWN):
            X.append(int(statistic[COL_EVENT_IBX_USR_KEYDOWN]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_USR_KEYPRESS):
            X.append(int(statistic[COL_EVENT_IBX_USR_KEYPRESS]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_USR_KEYUP):
            X.append(int(statistic[COL_EVENT_IBX_USR_KEYUP]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_USR_MOUSEDOWN):
            X.append(int(statistic[COL_EVENT_IBX_USR_MOUSEDOWN]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_USR_MOUSEMOVE):
            X.append(int(statistic[COL_EVENT_IBX_USR_MOUSEMOVE]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_USR_MOUSEOUT):
            X.append(int(statistic[COL_EVENT_IBX_USR_MOUSEOUT]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_USR_MOUSEOVER):
            X.append(int(statistic[COL_EVENT_IBX_USR_MOUSEOVER]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_USR_MOUSEUP):
            X.append(int(statistic[COL_EVENT_IBX_USR_MOUSEUP]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_USR_TOUCHSTART):
            X.append(int(statistic[COL_EVENT_IBX_USR_TOUCHSTART]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_USR_TOUCHMOVE):
            X.append(int(statistic[COL_EVENT_IBX_USR_TOUCHMOVE]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_USR_TOUCHEND):
            X.append(int(statistic[COL_EVENT_IBX_USR_TOUCHEND]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_USR_TOUCHCANCEL):
            X.append(int(statistic[COL_EVENT_IBX_USR_TOUCHCANCEL]))
        else:
            X.append(0)

        # B - 密码输入框
        if statistic.has_key(COL_EVENT_IBX_PWD_CHANGE):
            X.append(int(statistic[COL_EVENT_IBX_PWD_CHANGE]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_PWD_CLICK):
            X.append(int(statistic[COL_EVENT_IBX_PWD_CLICK]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_PWD_DBLCLICK):
            X.append(int(statistic[COL_EVENT_IBX_PWD_DBLCLICK]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_PWD_FOCUS):
            X.append(int(statistic[COL_EVENT_IBX_PWD_FOCUS]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_PWD_KEYDOWN):
            X.append(int(statistic[COL_EVENT_IBX_PWD_KEYDOWN]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_PWD_KEYPRESS):
            X.append(int(statistic[COL_EVENT_IBX_PWD_KEYPRESS]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_PWD_KEYUP):
            X.append(int(statistic[COL_EVENT_IBX_PWD_KEYUP]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_PWD_MOUSEDOWN):
            X.append(int(statistic[COL_EVENT_IBX_PWD_MOUSEDOWN]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_PWD_MOUSEMOVE):
            X.append(int(statistic[COL_EVENT_IBX_PWD_MOUSEMOVE]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_PWD_MOUSEOUT):
            X.append(int(statistic[COL_EVENT_IBX_PWD_MOUSEOUT]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_PWD_MOUSEOVER):
            X.append(int(statistic[COL_EVENT_IBX_PWD_MOUSEOVER]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_PWD_MOUSEUP):
            X.append(int(statistic[COL_EVENT_IBX_PWD_MOUSEUP]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_PWD_TOUCHSTART):
            X.append(int(statistic[COL_EVENT_IBX_PWD_TOUCHSTART]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_PWD_TOUCHMOVE):
            X.append(int(statistic[COL_EVENT_IBX_PWD_TOUCHMOVE]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_PWD_TOUCHEND):
            X.append(int(statistic[COL_EVENT_IBX_PWD_TOUCHEND]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_PWD_TOUCHCANCEL):
            X.append(int(statistic[COL_EVENT_IBX_PWD_TOUCHCANCEL]))
        else:
            X.append(0)

        # C - 图形验证码输入框
        if statistic.has_key(COL_EVENT_IBX_IMG_CHANGE):
            X.append(int(statistic[COL_EVENT_IBX_IMG_CHANGE]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_IMG_CLICK):
            X.append(int(statistic[COL_EVENT_IBX_IMG_CLICK]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_IMG_DBLCLICK):
            X.append(int(statistic[COL_EVENT_IBX_IMG_DBLCLICK]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_IMG_FOCUS):
            X.append(int(statistic[COL_EVENT_IBX_IMG_FOCUS]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_IMG_KEYDOWN):
            X.append(int(statistic[COL_EVENT_IBX_IMG_KEYDOWN]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_IMG_KEYPRESS):
            X.append(int(statistic[COL_EVENT_IBX_IMG_KEYPRESS]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_IMG_KEYUP):
            X.append(int(statistic[COL_EVENT_IBX_IMG_KEYUP]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_IMG_MOUSEDOWN):
            X.append(int(statistic[COL_EVENT_IBX_IMG_MOUSEDOWN]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_IMG_MOUSEMOVE):
            X.append(int(statistic[COL_EVENT_IBX_IMG_MOUSEMOVE]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_IMG_MOUSEOUT):
            X.append(int(statistic[COL_EVENT_IBX_IMG_MOUSEOUT]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_IMG_MOUSEOVER):
            X.append(int(statistic[COL_EVENT_IBX_IMG_MOUSEOVER]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_IMG_MOUSEUP):
            X.append(int(statistic[COL_EVENT_IBX_IMG_MOUSEUP]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_IMG_TOUCHSTART):
            X.append(int(statistic[COL_EVENT_IBX_IMG_TOUCHSTART]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_IMG_TOUCHMOVE):
            X.append(int(statistic[COL_EVENT_IBX_IMG_TOUCHMOVE]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_IMG_TOUCHEND):
            X.append(int(statistic[COL_EVENT_IBX_IMG_TOUCHEND]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_IMG_TOUCHCANCEL):
            X.append(int(statistic[COL_EVENT_IBX_IMG_TOUCHCANCEL]))
        else:
            X.append(0)

        # D - 图形验证码刷新按钮
        if statistic.has_key(COL_EVENT_BTN_IMG_CLICK):
            X.append(int(statistic[COL_EVENT_BTN_IMG_CLICK]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_IMG_DBLCLICK):
            X.append(int(statistic[COL_EVENT_BTN_IMG_DBLCLICK]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_IMG_FOCUS):
            X.append(int(statistic[COL_EVENT_BTN_IMG_FOCUS]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_IMG_KEYDOWN):
            X.append(int(statistic[COL_EVENT_BTN_IMG_KEYDOWN]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_IMG_KEYPRESS):
            X.append(int(statistic[COL_EVENT_BTN_IMG_KEYPRESS]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_IMG_KEYUP):
            X.append(int(statistic[COL_EVENT_BTN_IMG_KEYUP]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_IMG_MOUSEDOWN):
            X.append(int(statistic[COL_EVENT_BTN_IMG_MOUSEDOWN]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_IMG_MOUSEMOVE):
            X.append(int(statistic[COL_EVENT_BTN_IMG_MOUSEMOVE]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_IMG_MOUSEOUT):
            X.append(int(statistic[COL_EVENT_BTN_IMG_MOUSEOUT]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_IMG_MOUSEOVER):
            X.append(int(statistic[COL_EVENT_BTN_IMG_MOUSEOVER]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_IMG_MOUSEUP):
            X.append(int(statistic[COL_EVENT_BTN_IMG_MOUSEUP]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_IMG_TOUCHSTART):
            X.append(int(statistic[COL_EVENT_BTN_IMG_TOUCHSTART]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_IMG_TOUCHMOVE):
            X.append(int(statistic[COL_EVENT_BTN_IMG_TOUCHMOVE]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_IMG_TOUCHEND):
            X.append(int(statistic[COL_EVENT_BTN_IMG_TOUCHEND]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_IMG_TOUCHCANCEL):
            X.append(int(statistic[COL_EVENT_BTN_IMG_TOUCHCANCEL]))
        else:
            X.append(0)

        # E - 手机号输入框
        if statistic.has_key(COL_EVENT_IBX_TEL_CHANGE):
            X.append(int(statistic[COL_EVENT_IBX_TEL_CHANGE]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_TEL_CLICK):
            X.append(int(statistic[COL_EVENT_IBX_TEL_CLICK]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_TEL_DBLCLICK):
            X.append(int(statistic[COL_EVENT_IBX_TEL_DBLCLICK]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_TEL_FOCUS):
            X.append(int(statistic[COL_EVENT_IBX_TEL_FOCUS]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_TEL_KEYDOWN):
            X.append(int(statistic[COL_EVENT_IBX_TEL_KEYDOWN]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_TEL_KEYPRESS):
            X.append(int(statistic[COL_EVENT_IBX_TEL_KEYPRESS]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_TEL_KEYUP):
            X.append(int(statistic[COL_EVENT_IBX_TEL_KEYUP]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_TEL_MOUSEDOWN):
            X.append(int(statistic[COL_EVENT_IBX_TEL_MOUSEDOWN]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_TEL_MOUSEMOVE):
            X.append(int(statistic[COL_EVENT_IBX_TEL_MOUSEMOVE]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_TEL_MOUSEOUT):
            X.append(int(statistic[COL_EVENT_IBX_TEL_MOUSEOUT]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_TEL_MOUSEOVER):
            X.append(int(statistic[COL_EVENT_IBX_TEL_MOUSEOVER]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_TEL_MOUSEUP):
            X.append(int(statistic[COL_EVENT_IBX_TEL_MOUSEUP]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_TEL_TOUCHSTART):
            X.append(int(statistic[COL_EVENT_IBX_TEL_TOUCHSTART]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_TEL_TOUCHMOVE):
            X.append(int(statistic[COL_EVENT_IBX_TEL_TOUCHMOVE]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_TEL_TOUCHEND):
            X.append(int(statistic[COL_EVENT_IBX_TEL_TOUCHEND]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_TEL_TOUCHCANCEL):
            X.append(int(statistic[COL_EVENT_IBX_TEL_TOUCHCANCEL]))
        else:
            X.append(0)

        # H - 手机验证码输入框(FOR TEL)
        if statistic.has_key(COL_EVENT_IBX_SMS_CHANGE):
            X.append(int(statistic[COL_EVENT_IBX_SMS_CHANGE]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_SMS_CLICK):
            X.append(int(statistic[COL_EVENT_IBX_SMS_CLICK]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_SMS_DBLCLICK):
            X.append(int(statistic[COL_EVENT_IBX_SMS_DBLCLICK]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_SMS_FOCUS):
            X.append(int(statistic[COL_EVENT_IBX_SMS_FOCUS]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_SMS_KEYDOWN):
            X.append(int(statistic[COL_EVENT_IBX_SMS_KEYDOWN]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_SMS_KEYPRESS):
            X.append(int(statistic[COL_EVENT_IBX_SMS_KEYPRESS]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_SMS_KEYUP):
            X.append(int(statistic[COL_EVENT_IBX_SMS_KEYUP]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_SMS_MOUSEDOWN):
            X.append(int(statistic[COL_EVENT_IBX_SMS_MOUSEDOWN]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_SMS_MOUSEMOVE):
            X.append(int(statistic[COL_EVENT_IBX_SMS_MOUSEMOVE]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_SMS_MOUSEOUT):
            X.append(int(statistic[COL_EVENT_IBX_SMS_MOUSEOUT]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_SMS_MOUSEOVER):
            X.append(int(statistic[COL_EVENT_IBX_SMS_MOUSEOVER]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_SMS_MOUSEUP):
            X.append(int(statistic[COL_EVENT_IBX_SMS_MOUSEUP]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_SMS_TOUCHSTART):
            X.append(int(statistic[COL_EVENT_IBX_SMS_TOUCHSTART]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_SMS_TOUCHMOVE):
            X.append(int(statistic[COL_EVENT_IBX_SMS_TOUCHMOVE]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_SMS_TOUCHEND):
            X.append(int(statistic[COL_EVENT_IBX_SMS_TOUCHEND]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_IBX_SMS_TOUCHCANCEL):
            X.append(int(statistic[COL_EVENT_IBX_SMS_TOUCHCANCEL]))
        else:
            X.append(0)

        # I - 手机验证码获取按钮(FOR TEL)
        if statistic.has_key(COL_EVENT_BTN_SMS_CLICK):
            X.append(int(statistic[COL_EVENT_BTN_SMS_CLICK]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_SMS_DBLCLICK):
            X.append(int(statistic[COL_EVENT_BTN_SMS_DBLCLICK]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_SMS_FOCUS):
            X.append(int(statistic[COL_EVENT_BTN_SMS_FOCUS]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_SMS_KEYDOWN):
            X.append(int(statistic[COL_EVENT_BTN_SMS_KEYDOWN]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_SMS_KEYPRESS):
            X.append(int(statistic[COL_EVENT_BTN_SMS_KEYPRESS]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_SMS_KEYUP):
            X.append(int(statistic[COL_EVENT_BTN_SMS_KEYUP]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_SMS_MOUSEDOWN):
            X.append(int(statistic[COL_EVENT_BTN_SMS_MOUSEDOWN]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_SMS_MOUSEMOVE):
            X.append(int(statistic[COL_EVENT_BTN_SMS_MOUSEMOVE]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_SMS_MOUSEOUT):
            X.append(int(statistic[COL_EVENT_BTN_SMS_MOUSEOUT]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_SMS_MOUSEOVER):
            X.append(int(statistic[COL_EVENT_BTN_SMS_MOUSEOVER]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_SMS_MOUSEUP):
            X.append(int(statistic[COL_EVENT_BTN_SMS_MOUSEUP]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_SMS_TOUCHSTART):
            X.append(int(statistic[COL_EVENT_BTN_SMS_TOUCHSTART]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_SMS_TOUCHMOVE):
            X.append(int(statistic[COL_EVENT_BTN_SMS_TOUCHMOVE]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_SMS_TOUCHEND):
            X.append(int(statistic[COL_EVENT_BTN_SMS_TOUCHEND]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_SMS_TOUCHCANCEL):
            X.append(int(statistic[COL_EVENT_BTN_SMS_TOUCHCANCEL]))
        else:
            X.append(0)

        # J - 登录按钮
        if statistic.has_key(COL_EVENT_BTN_LGN_CLICK):
            X.append(int(statistic[COL_EVENT_BTN_LGN_CLICK]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_LGN_DBLCLICK):
            X.append(int(statistic[COL_EVENT_BTN_LGN_DBLCLICK]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_LGN_FOCUS):
            X.append(int(statistic[COL_EVENT_BTN_LGN_FOCUS]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_LGN_KEYDOWN):
            X.append(int(statistic[COL_EVENT_BTN_LGN_KEYDOWN]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_LGN_KEYPRESS):
            X.append(int(statistic[COL_EVENT_BTN_LGN_KEYPRESS]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_LGN_KEYUP):
            X.append(int(statistic[COL_EVENT_BTN_LGN_KEYUP]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_LGN_MOUSEDOWN):
            X.append(int(statistic[COL_EVENT_BTN_LGN_MOUSEDOWN]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_LGN_MOUSEMOVE):
            X.append(int(statistic[COL_EVENT_BTN_LGN_MOUSEMOVE]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_LGN_MOUSEOUT):
            X.append(int(statistic[COL_EVENT_BTN_LGN_MOUSEOUT]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_LGN_MOUSEOVER):
            X.append(int(statistic[COL_EVENT_BTN_LGN_MOUSEOVER]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_LGN_MOUSEUP):
            X.append(int(statistic[COL_EVENT_BTN_LGN_MOUSEUP]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_LGN_TOUCHSTART):
            X.append(int(statistic[COL_EVENT_BTN_LGN_TOUCHSTART]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_LGN_TOUCHMOVE):
            X.append(int(statistic[COL_EVENT_BTN_LGN_TOUCHMOVE]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_LGN_TOUCHEND):
            X.append(int(statistic[COL_EVENT_BTN_LGN_TOUCHEND]))
        else:
            X.append(0)
        if statistic.has_key(COL_EVENT_BTN_LGN_TOUCHCANCEL):
            X.append(int(statistic[COL_EVENT_BTN_LGN_TOUCHCANCEL]))
        else:
            X.append(0)

        # 时间信息
        ctm = time.time()
        if statistic.has_key('UTM'): # 更新时间
            if int(statistic['UTM']) < ctm:
                X.append(ctm - int(statistic['UTM']))
            else:
                X.append(0)
        else:
            X.append(0)

        return X
    # 分析风险指数
    def PredictRisk(self, vec):
        global gClassfier

        return gClassfier.predict(vec)
    # 预测处理
    def predict(self, params):
        risk = 10

        # 判断报体合法性
        if not params.has_key("token"):
            logging.warning("Get token failed!")
            # 发送预测结果
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            mesg = {}
            mesg.setdefault("token", '')
            mesg.setdefault("risk", risk)
            mesg.setdefault("errmsg", "Get token failed!")

            self.wfile.write(json.dumps(mesg))
            return

        # 通过TOKEN获取SID
        sid = self.GetSid(params["token"][0])
        if sid is None:
            logging.warning("Get sid by token failed!")
            # 发送预测结果
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            mesg = {}
            mesg.setdefault("token", params["token"][0])
            mesg.setdefault("risk", risk)
            mesg.setdefault("errmsg", "Get sid by token failed!")

            self.wfile.write(json.dumps(mesg))
            return

        # 通过SID获取统计数据
        vec = self.GetStatistic(sid)
        if vec is None:
            # 发送预测结果
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            mesg = {}
            mesg.setdefault("token", params["token"])
            mesg.setdefault("risk", risk)
            mesg.setdefault("errmsg", "Get data by token failed!")

            self.wfile.write(json.dumps(mesg))
            return

        # 进行风险预测
        risk = self.PredictRisk(vec)

        # 发送预测结果
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        mesg = {}
        mesg.setdefault("token", token)
        mesg.setdefault("risk", risk)
        mesg.setdefault("errmsg", "Ok")

        self.wfile.write(json.dumps(mesg))

        return

    def do_GET(self):
        logging.warning("======= GET STARTED =======")
        logging.warning(self.headers)

        token="invalid-token"
        parmas = {}
        if '?' in self.path: #如果带有参数
            query = urllib.unquote(self.path.split('?',1)[1])
            params = urlparse.parse_qs(query)
            print(params)
        self.predict(params)

    def do_POST(self):
        logging.warning("======= POST STARTED =======")
        logging.warning(self.headers)

        SimpleHTTPServer.SimpleHTTPRequestHandler.do_POST(self)

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
PORT = 8081
if __name__ == "__main__":
    # 启动服务
    httpd = SocketServer.TCPServer(("", PORT), AiEyeHandler)

    httpd.serve_forever()
