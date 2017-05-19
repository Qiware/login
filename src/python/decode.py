#/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import cgi
import sys
import json
import time
import base64

if __name__ == "__main__":
    f = open("base64.log")

    for line in f.readlines():
        js = base64.decodestring(line)
        print js
