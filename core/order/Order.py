#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/15 16:01
# @Author   : cancan
# @File     : Order.py
# @Function : 订单相关操作

from RequestAPI.BaseRequest import BaseRequest
from base.db.DBOPS import DBOps
from config.DBCollConfig import DBCollonfig


class addOrderClass(BaseRequest):
    """
        添加订单类目
    """

    def handler_function(self):
        args = self.get_request_data()

        newClasses = args['classes']

        oldClasses = DBOps.getOneDoc(
            DBCollonfig.options,
            {'_id': DBCollonfig.orderClass}
        )['classes']

        print newClasses
        error_list = []
        for each in newClasses:
            if not oldClasses.has_key(each['name']):
                oldClasses.update(
                    {each['name']: {'createTime': each['time']}}
                )
            else:
                error_list.append(each['name'])

        if error_list:
            msg = u','.join([_  for _ in error_list]) + u'已存在'
            return self.response_failure(msg=msg)

        DBOps.setOneDoc(
            DBCollonfig.options,
            {'_id': DBCollonfig.orderClass},
            {'$set': {'classes': oldClasses}}
        )

        return self.response_success()

class addOrderCustomer(BaseRequest):
    """
        添加订单客户
    """

    def handler_function(self):
        args = self.get_request_data()

        newCustomers = args['customers']

        oldCustomers = DBOps.getOneDoc(
            DBCollonfig.options,
            {'_id': DBCollonfig.orderCustomer}
        )['customers']

        print newCustomers
        error_list = []
        for each in newCustomers:
            if not oldCustomers.has_key(each['name']):
                oldCustomers.update(
                    {each['name']: {'createTime': each['time']}}
                )
            else:
                error_list.append(each['name'])

        if error_list:
            msg = u','.join([_  for _ in error_list]) + u'已存在'
            return self.response_failure(msg=msg)

        DBOps.setOneDoc(
            DBCollonfig.options,
            {'_id': DBCollonfig.orderCustomer},
            {'$set': {'customers': oldCustomers}}
        )

        return self.response_success()
