#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/14 下午9:49
# @Author   : cancan
# @File     : RequestAPI.py
# @Function : 请求协议映射

from core.account import Account
from core.order import Order
from core.statistics import Statistics
from core.popover import Popover
from base.message import Message
from base.log import LogContent

HandleList = [
    (r'/api/register', Account.Register),
    (r'/api/login', Account.Login),
    (r'/api/checkLogin', Account.checkLogin),
    (r'/api/userList', Account.UserList),
    (r'/api/editUser', Account.EditUser),
    (r'/api/registerInitData', Account.RegisterIinitData),
    (r'/api/editUserInitData', Account.EditUserInitData),
    (r'/api/setNavCollapse', Account.SetNavCollapse),

    (r'/api/addOrderClass', Order.AddOrderClass),
    (r'/api/addOrderCustomer', Order.AddOrderCustomer),
    (r'/api/addOrderCompany', Order.AddOrderCompany),
    (r'/api/orderInitData', Order.OrderInitData),
    (r'/api/addOrderContact', Order.AddOrderContact),
    (r'/api/createOrder', Order.CreateOrder),
    (r'/api/orderList', Order.OrderList),
    (r'/api/delOrder', Order.DelOrder),
    (r'/api/editOrderStatus', Order.EditOrderStatus),
    (r'/api/orderOptionInitData', Order.OrderOptionInitData),
    (r'/api/delOrderOption', Order.DelOrderOption),
    (r'/api/downloadTable', Order.DownloadTable),
    (r'/api/addOrderHelpInfo', Order.AddOrderHelpInfo),
    (r'/api/addWorkClass', Order.AddWorkClass),
    (r'/api/editOrderOption', Order.EditOrderOption),
    (r'/api/writeDownloadLog', Order.WriteDownloadLog),

    (r'/api/contactUseTop10', Statistics.ContactUseTop10),

    (r'/api/logList', LogContent.LogList),

    (r'/api/getCustomerPopover', Popover.getCustomerPopover),
    (r'/api/getContactPopover', Popover.getContactPopover),

    (r'/api/checkMsg', Message.CheckMsg),
]
