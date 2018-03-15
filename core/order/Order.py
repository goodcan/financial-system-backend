#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/15 16:01
# @Author   : cancan
# @File     : Order.py
# @Function : 订单相关操作

from RequestAPI.BaseRequest import BaseRequest
from base.db.DBOPS import DBOps
from config.DBCollConfig import DBCollonfig


class orderInitData(BaseRequest):
    """
        初始化订单数据
    """

    def handler_function(self):
        classes = DBOps.getOneDoc(
            DBCollonfig.options,
            {'_id': DBCollonfig.orderClass}
        )['classes']
        customers = DBOps.getOneDoc(
            DBCollonfig.options,
            {'_id': DBCollonfig.orderCustomer}
        )['customers']

        self.result['result'] = {
            'classes': [{'label': _, 'value': _} for _ in classes],
            'customers': [{'label': _, 'value': _} for _ in customers]
        }

        return self.response_success()


class addOrderClass(BaseRequest):
    """
        添加订单类目
    """

    def handler_function(self):
        args = self.get_request_data()

        createUser = args.get('createUser', None)
        newClasses = args.get('classes', None)

        oldClasses = DBOps.getOneDoc(
            DBCollonfig.options,
            {'_id': DBCollonfig.orderClass}
        )['classes']

        print newClasses
        error_list = []
        for each in newClasses:
            if not oldClasses.has_key(each['name']):
                oldClasses.update(
                    {
                        each['name']: {
                            'createTime': each['time'],
                            'createUser': createUser
                        }
                    }
                )
            else:
                error_list.append(each['name'])

        if error_list:
            msg = u','.join([_ for _ in error_list]) + u'已存在'
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

        createUser = args.get('createUser', None)
        newCustomers = args.get('customers', None)

        oldCustomers = DBOps.getOneDoc(
            DBCollonfig.options,
            {'_id': DBCollonfig.orderCustomer}
        )['customers']

        print newCustomers
        error_list = []
        for each in newCustomers:
            if not oldCustomers.has_key(each['name']):
                oldCustomers.update(
                    {
                        each['name']: {
                            'createTime': each['time'],
                            'createUser': createUser
                        },
                    }
                )
            else:
                error_list.append(each['name'])

        if error_list:
            msg = u','.join([_ for _ in error_list]) + u'已存在'
            return self.response_failure(msg=msg)

        DBOps.setOneDoc(
            DBCollonfig.options,
            {'_id': DBCollonfig.orderCustomer},
            {'$set': {'customers': oldCustomers}}
        )

        return self.response_success()


class addOrderContact(BaseRequest):
    """
        添加订单客户
    """

    def handler_function(self):
        args = self.get_request_data()

        createUser = args.get('createUser', None)
        tel = args.get('tel', None)
        email = args.get('email', None)
        qq = args.get('qq', None)
        newContacts = args.get('contacts', None)

        oldContacts = DBOps.getOneDoc(
            DBCollonfig.options,
            {'_id': DBCollonfig.orderContact}
        )['contacts']

        print newContacts
        error_list = []
        for each in newContacts:
            if not oldContacts.has_key(each['name']):
                oldContacts.update(
                    {
                        each['name']: {
                            'createTime': each['time'],
                            'createUser': createUser,
                            'tel': tel,
                            'email': email,
                            'qq': qq
                        }
                    }
                )
            else:
                error_list.append(each['name'])

        if error_list:
            msg = u','.join([_ for _ in error_list]) + u'已存在'
            return self.response_failure(msg=msg)

        DBOps.setOneDoc(
            DBCollonfig.options,
            {'_id': DBCollonfig.orderCustomer},
            {'$set': {'contacts': oldContacts}}
        )

        return self.response_success()
