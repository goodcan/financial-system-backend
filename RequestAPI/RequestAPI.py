#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/14 下午9:49
# @Author   : cancan
# @File     : RequestAPI.py
# @Function : 请求协议映射

from core.account.Register import Register

HandleList = [
    (r'/register', Register)
]
