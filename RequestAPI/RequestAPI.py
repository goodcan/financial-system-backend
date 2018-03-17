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
    (r'/api/addOrderClass', Order.AddOrderClass),
    (r'/api/addOrderCustomer', Order.AddOrderCustomer),
    (r'/api/addOrderDpt', Order.AddOrderDpt),
    (r'/api/orderInitData', Order.OrderInitData),
    (r'/api/addOrderContact', Order.AddOrderContact),
    (r'/api/createOrder', Order.CreateOrder),
    (r'/api/orderList', Order.OrderList),
    (r'/api/delOrder', Order.DelOrder),
    (r'/api/registerInitData', Account.RegisterIinitData),
    (r'/api/editOrderStatus', Order.EditOrderStatus),
    (r'/api/userList', Account.UserList),
    (r'/api/editUserInitData', Account.EditUserInitData),
    (r'/api/editUser', Account.EditUser),
    (r'/api/orderOptionInitData', Order.OrderOptionInitData),
    (r'/api/delOrderOption', Order.DelOrderOption),
]
