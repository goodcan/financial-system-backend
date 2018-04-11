#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/16 下午10:10
# @Author   : cancan
# @File     : UserConfig.py
# @Function : 用户配置

class UserConfig:
    permissions = {
        'createOrder': u'创建订单',
        'editSelfOrder': u'修改自己创建的订单',
        # 'readDptOrder': u'查看自己部门的订单',
        # 'editDptOrder': u'修改自己部门的订单',
        'readCompanyOrder': u'查看所属公司的订单',
        'editCompanyOrder': u'修改所属公司的订单',
        'editAllOrder': u'修改所有订单',
        'editOrderOption': u'编辑订单选项',
        'editUser': u'管理用户',
        'summaryOrder': u'订单汇总',
        'editOrderMoreParam': u'修改订单的多个参数'
    }
