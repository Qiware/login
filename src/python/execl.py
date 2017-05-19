#/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import cgi
import sys
import time
import json
import random
import thread
import logging
import urllib2

sys.path.append('3rd/xlrd')
sys.path.append('3rd/xlwt')
sys.path.append('3rd/xlutils')
import xlrd
import xlwt
import xlutils
from xlutils.copy import copy

reload(sys)
sys.setdefaultencoding('utf8')

type = sys.getfilesystemencoding()

COL_RESERVED = 1
################################################################################
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
    COL_EVENT_IBX_USR_TOUCHCANCEL : '用户名TOUCHCANCEL:',
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
    COL_EVENT_IBX_PWD_TOUCHCANCEL : '密码TOUCHCANCEL:',
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
    COL_EVENT_IBX_IMG_TOUCHCANCEL : '图片验证码TOUCHCANCEL:',
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
    COL_EVENT_BTN_IMG_TOUCHCANCEL : '图片验证码刷新TOUCHCANCEL:',
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
    COL_EVENT_IBX_TEL_TOUCHCANCEL : '手机号TOUCHCANCEL:',
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
    COL_EVENT_IBX_SMS_TOUCHCANCEL : '短信TOUCHCANCEL:',
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
    COL_EVENT_BTN_SMS_TOUCHCANCEL : '短信按钮TOUCHCANCEL:',
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
    COL_EVENT_BTN_LGN_TOUCHCANCEL : '登录TOUCHCANCEL:',
    # 时间信息
    COL_TIME_DIFF_SEC : '间隔时间:'
}

################################################################################
# 对EXECL行列值进行转化
def execl_val_to_str(table, row_idx, col_idx):
    v = table.row(row_idx)[col_idx].value
    if type(v) is int or type(v) is float:
        return str(int(v))
    return v.encode('utf-8')

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

# 样本分析
class Sample:
    def __init__(self): # 初始化对象
        self.user = {}
    def load(self, sheet): # 加载样本数据
        global DescMap
        f = open('./login.js')
        row = 0
        style = set_style('Times New Roman',220,True)
        for line in f.readlines():
            print line
            js = json.loads(line)
            col = 0
            # 插件信息
            if js.has_key('plugin'):
                # 插件名称
                col = 0
                if js['plugin'].has_key('name'):
                    if len(js['plugin']['name']) > 0:
                        item = unicode(DescMap[col] + '1')
                        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                    else:
                        item = unicode(DescMap[col] + '0')
                        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                else:
                    item = unicode(DescMap[col] + '0')
                    sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档

                # 插件描述
                col += 1
                if js['plugin'].has_key('description'):
                    if len(js['plugin']['description']) > 0:
                        item = unicode(DescMap[col] + '1')
                        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                    else:
                        item = unicode(DescMap[col] + '0')
                        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                else:
                    item = unicode(DescMap[col] + '0')
                    sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
            else:
                # 插件名称
                col = 0
                item = unicode(DescMap[col] + '0')
                sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档

                # 插件描述
                col += 1
                item = unicode(DescMap[col] + '0')
                sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档

            # 用户代理
            col += 1
            if js.has_key('ua'):
                item = unicode(DescMap[col] + '1')
                sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
            else:
                item = unicode(DescMap[col] + '0')
                sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档

            # 屏幕信息
            if js.has_key('screen'):
                # 屏幕宽度
                col += 1
                if js['screen'].has_key('w'):
                    item = unicode(DescMap[col] + str(js['screen']['w']))
                    sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                else:
                    item = unicode(DescMap[col] + '0')
                    sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                # 屏幕高度
                col += 1
                if js['screen'].has_key('h'):
                    item = unicode(DescMap[col] + str(js['screen']['h']))
                    sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                else:
                    item = unicode(DescMap[col] + '0')
                    sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                # 屏幕avial宽度
                col += 1
                if js['screen'].has_key('aw'):
                    item = unicode(DescMap[col] + str(js['screen']['aw']))
                    sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                else:
                    item = unicode(DescMap[col] + '0')
                    sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                # 屏幕avial高度
                col += 1
                if js['screen'].has_key('ah'):
                    item = unicode(DescMap[col] + str(js['screen']['ah']))
                    sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                else:
                    item = unicode(DescMap[col] + '0')
                    sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                # 屏幕avial左边距
                col += 1
                if js['screen'].has_key('al'):
                    item = unicode(DescMap[col] + str(js['screen']['al']))
                    sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                else:
                    item = unicode(DescMap[col] + '0')
                    sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                # 屏幕avial顶边距
                col += 1
                if js['screen'].has_key('at'):
                    item = unicode(DescMap[col] + str(js['screen']['at']))
                    sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                else:
                    item = unicode(DescMap[col] + '0')
                    sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                # 屏幕OUTER宽度
                col += 1
                if js['screen'].has_key('ow'):
                    item = unicode(DescMap[col] + str(js['screen']['ow']))
                    sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                else:
                    item = unicode(DescMap[col] + '0')
                    sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                # 屏幕OUTER高度
                col += 1
                if js['screen'].has_key('oh'):
                    item = unicode(DescMap[col] + str(js['screen']['oh']))
                    sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                else:
                    item = unicode(DescMap[col] + '0')
                    sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                # 屏幕INNER宽度
                col += 1
                if js['screen'].has_key('iw'):
                    item = unicode(DescMap[col] + str(js['screen']['iw']))
                    sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                else:
                    item = unicode(DescMap[col] + '0')
                    sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                # 屏幕INNER高度
                col += 1
                if js['screen'].has_key('ih'):
                    item = unicode(DescMap[col] + str(js['screen']['ih']))
                    sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                else:
                    item = unicode(DescMap[col] + '0')
                    sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
            else:
                # 屏幕宽度
                col += 1
                item = unicode(DescMap[col] + '0')
                sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                # 屏幕高度
                col += 1
                item = unicode(DescMap[col] + '0')
                sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                # 屏幕avial宽度
                col += 1
                item = unicode(DescMap[col] + '0')
                sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                # 屏幕avial左边距
                col += 1
                item = unicode(DescMap[col] + '0')
                sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                # 屏幕avial顶边距
                col += 1
                item = unicode(DescMap[col] + '0')
                sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                # 屏幕OUTER宽度
                col += 1
                item = unicode(DescMap[col] + '0')
                sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                # 屏幕OUTER高度
                col += 1
                item = unicode(DescMap[col] + '0')
                sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                # 屏幕INNER宽度
                col += 1
                item = unicode(DescMap[col] + '0')
                sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                # 屏幕INNER高度
                col += 1
                item = unicode(DescMap[col] + '0')
                sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档

            # 事件统计
            if js.has_key('events'):
                ctrls = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
                for idx in range(len(ctrls)):
                    ctrl = ctrls[idx]
                    # 获取各控件事件
                    if js['events'].has_key(ctrl):
                        if idx != 3 and idx != 6 and idx != 7:
                            # CHANGE
                            col += 1
                            if js['events'][ctrl].has_key('0'):
                                item = unicode(DescMap[col] + str(js['events'][ctrl]['0']))
                                sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                            else:
                                item = unicode(DescMap[col] + '0')
                                sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # CLICK
                        col += 1
                        if js['events'][ctrl].has_key('1'):
                            item = unicode(DescMap[col] + str(js['events'][ctrl]['1']))
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        else:
                            item = unicode(DescMap[col] + '0')
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # DBLCLICK
                        col += 1
                        if js['events'][ctrl].has_key('2'):
                            item = unicode(DescMap[col] + str(js['events'][ctrl]['2']))
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        else:
                            item = unicode(DescMap[col] + '0')
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # FOCUS
                        col += 1
                        if js['events'][ctrl].has_key('3'):
                            item = unicode(DescMap[col] + str(js['events'][ctrl]['3']))
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        else:
                            item = unicode(DescMap[col] + '0')
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # KEYDOWN
                        col += 1
                        if js['events'][ctrl].has_key('4'):
                            item = unicode(DescMap[col] + str(js['events'][ctrl]['4']))
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        else:
                            item = unicode(DescMap[col] + '0')
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # KEYPRESS
                        col += 1
                        if js['events'][ctrl].has_key('5'):
                            item = unicode(DescMap[col] + str(js['events'][ctrl]['5']))
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        else:
                            item = unicode(DescMap[col] + '0')
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # KEYUP
                        col += 1
                        if js['events'][ctrl].has_key('6'):
                            item = unicode(DescMap[col] + str(js['events'][ctrl]['6']))
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        else:
                            item = unicode(DescMap[col] + '0')
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # MOUSEDOWN
                        col += 1
                        if js['events'][ctrl].has_key('7'):
                            item = unicode(DescMap[col] + str(js['events'][ctrl]['7']))
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        else:
                            item = unicode(DescMap[col] + '0')
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # MOUSEMOVE
                        col += 1
                        if js['events'][ctrl].has_key('8'):
                            item = unicode(DescMap[col] + str(js['events'][ctrl]['8']))
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        else:
                            item = unicode(DescMap[col] + '0')
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # MOUSEOUT
                        col += 1
                        if js['events'][ctrl].has_key('9'):
                            item = unicode(DescMap[col] + str(js['events'][ctrl]['9']))
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        else:
                            item = unicode(DescMap[col] + '0')
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # MOUSEOVER
                        col += 1
                        if js['events'][ctrl].has_key('10'):
                            item = unicode(DescMap[col] + str(js['events'][ctrl]['10']))
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        else:
                            item = unicode(DescMap[col] + '0')
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # MOUSEUP
                        col += 1
                        if js['events'][ctrl].has_key('11'):
                            item = unicode(DescMap[col] + str(js['events'][ctrl]['11']))
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        else:
                            item = unicode(DescMap[col] + '0')
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # TOUCHSTART
                        col += 1
                        if js['events'][ctrl].has_key('12'):
                            item = unicode(DescMap[col] + str(js['events'][ctrl]['12']))
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        else:
                            item = unicode(DescMap[col] + '0')
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # TOUCHMOVE
                        col += 1
                        if js['events'][ctrl].has_key('13'):
                            item = unicode(DescMap[col] + str(js['events'][ctrl]['13']))
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        else:
                            item = unicode(DescMap[col] + '0')
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # TOUCHEND
                        col += 1
                        if js['events'][ctrl].has_key('14'):
                            item = unicode(DescMap[col] + str(js['events'][ctrl]['14']))
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        else:
                            item = unicode(DescMap[col] + '0')
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # TOUCHCANCEL
                        col += 1
                        if js['events'][ctrl].has_key('15'):
                            item = unicode(DescMap[col] + str(js['events'][ctrl]['15']))
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        else:
                            item = unicode(DescMap[col] + '0')
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                    else:
                        if idx != 3 and idx != 6 and idx != 7:
                            # CHANGE
                            col += 1
                            item = unicode(DescMap[col] + '0')
                            sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # CLICK
                        col += 1
                        item = unicode(DescMap[col] + '0')
                        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # DBLCLICK
                        col += 1
                        item = unicode(DescMap[col] + '0')
                        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # FOCUS
                        col += 1
                        item = unicode(DescMap[col] + '0')
                        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # KEYDOWN
                        col += 1
                        item = unicode(DescMap[col] + '0')
                        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # KEYPRESS
                        col += 1
                        item = unicode(DescMap[col] + '0')
                        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # KEYUP
                        col += 1
                        item = unicode(DescMap[col] + '0')
                        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # MOUSEDOWN
                        col += 1
                        item = unicode(DescMap[col] + '0')
                        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # MOUSEMOVE
                        col += 1
                        item = unicode(DescMap[col] + '0')
                        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # MOUSEOUT
                        col += 1
                        item = unicode(DescMap[col] + '0')
                        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # MOUSEOVER
                        col += 1
                        item = unicode(DescMap[col] + '0')
                        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # MOUSEUP
                        col += 1
                        item = unicode(DescMap[col] + '0')
                        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # TOUCHSTART
                        col += 1
                        item = unicode(DescMap[col] + '0')
                        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # TOUCHMOVE
                        col += 1
                        item = unicode(DescMap[col] + '0')
                        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # TOUCHEND
                        col += 1
                        item = unicode(DescMap[col] + '0')
                        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
                        # TOUCHCANCEL
                        col += 1
                        item = unicode(DescMap[col] + '0')
                        sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
            # 时间信息
            col += 1
            print col
            if js.has_key('t'):
                item = unicode(DescMap[col] + str(random.randint(0, 3)))
                sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
            else:
                item = unicode(DescMap[col] + '5')
                sheet.write(row, col+COL_RESERVED, item, style) # 撰写EXECL文档
            row += 1
        f.close()

################################################################################
##函数名称: main
##功    能: 从sample.s文件中格式化数据到execl文档中
##输入参数:
##输出参数:
##返    回:
##实现描述:
##注意事项:
##作    者: # Qifeng.zou # 2017.03.31 13:58:00 #
################################################################################
if __name__ == '__main__':
    sample = Sample()

    # 新建EXECL文件
    wk = xlwt.Workbook()
    sheet = wk.add_sheet(u'SAMPLE', cell_overwrite_ok=True)

    # 加载样本数据
    sample.load(sheet)

    for idx in range(COL_PLUGIN_HAS_NAME+COL_RESERVED, COL_TIME_DIFF_SEC+COL_RESERVED+1):
        col = sheet.col(idx)       #xlwt中是行和列都是从0开始计算的
        col.width=30*256
    wk.save('./sample.xlsx')
