#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/14 下午9:49
# @Author   : cancan
# @File     : RequestAPI.py
# @Function : 请求协议映射

from core.account import Account
from core.order import Order

HandleList = [
    (r'/api/register', Account.Register),
    (r'/api/login', Account.Login),
    (r'/api/checkLogin', Account.checkLogin),
    (r'/api/addOrderClass', Order.addOrderClass),
    (r'/api/addOrderCustomer', Order.addOrderCustomer)
]
