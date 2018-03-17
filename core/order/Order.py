#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/15 16:01
# @Author   : cancan
# @File     : Order.py
# @Function : 订单相关操作

from datetime import datetime

from RequestAPI.BaseRequest import BaseRequest
from base.db.DBOps import DBOps
from config.DBCollConfig import DBCollonfig


class EditOrderStatus(BaseRequest):
    """
        编辑订单状态
    """

    def handler_function(self):
        args = self.get_request_data()

        setStatus = args.get('status', None)
        userId = args.get('userId', None)
        orderId = args.get('orderId', None)

        nowStatus = DBOps.getOneDoc(
            DBCollonfig.users,
            {'_id': userId, 'orders.orderId': orderId},
            {'orders..$': 1}
        )['orders'][0]['status']

        if nowStatus == setStatus:
            return self.response_failure(msg='订单状态已被修改！')

        DBOps.setOneDoc(
            DBCollonfig.users,
            {'_id': userId, 'orders.orderId': orderId},
            {'$set': {'orders.$.status': setStatus}}
        )

        return self.response_success(msg='订单状态修改成功！')


class DelOrder(BaseRequest):
    """
        删除订单
    """

    def handler_function(self):
        args = self.get_request_data()

        DBOps.setOneDoc(
            DBCollonfig.users,
            {'_id': args['userId']},
            {
                '$pull': {
                    'orders': {
                        'orderId': args['orderId']
                    }
                }
            }
        )

        self.response_success()


class OrderList(BaseRequest):
    """
        订单列表
    """

    def handler_function(self):
        userId = self.getUserIdByToken()

        orders = DBOps.getOneDoc(
            DBCollonfig.users,
            {'_id': userId},
            {'orders': 1}
        )['orders']

        self.result['result'] = sorted(
            orders,
            key=lambda x: self.time_conversion(x['createTime'], 1),
            reverse=True
        )
        return self.response_success()


class CreateOrder(BaseRequest):
    """
        创建订单
    """

    def handler_function(self):
        args = self.get_request_data()

        now = datetime.now()
        orderId = str(args['userId']) + now.strftime('%Y%m%d%H%M%S')
        order = {
            'orderId': orderId,
            'userId': args['userId'],
            'createUser': args['createUser'],
            'department': args['department'],
            'className': args['className'],
            'customerName': args['customerName'],
            'contactName': args['contactName'],
            'expectDate': args['expectDate'],
            'price': args['price'],
            'desc': args['desc'],
            'createTime': now.strftime('%Y-%m-%d %H:%M:%S'),
            'status': 1
        }

        DBOps.setOneDoc(
            DBCollonfig.users,
            {'_id': args['userId']},
            {'$push': {'orders': order}}
        )

        self.response_success()


class OrderInitData(BaseRequest):
    """
        初始化订单数据
    """

    def handler_function(self):
        orderOptions = DBOps.getOneDoc(
            DBCollonfig.options,
            {'_id': DBCollonfig.orderOption}
        )
        classes = orderOptions['classes']
        customers = orderOptions['customers']
        contacts = orderOptions['contacts']
        departments = orderOptions['departments']

        self.result['result'] = {
            'classes': [
                {'label': _['name'], 'value': _['name']} for _ in classes
            ],
            'customers': [
                {'label': _['name'], 'value': _['name']} for _ in customers
            ],
            'contacts': [
                {'label': _['name'], 'value': _['name']} for _ in contacts
            ],
            'departments': [
                {'label': _['name'], 'value': _['name']} for _ in departments
            ]
        }

        return self.response_success()


class AddOrderClass(BaseRequest):
    """
        添加订单类目
    """

    def handler_function(self):
        args = self.get_request_data()

        createUser = args.get('createUser', None)
        newClasses = args.get('classes', None)

        error_list = []
        for each in newClasses:
            isExist = DBOps.getOneDoc(
                DBCollonfig.options,
                {
                    '_id': DBCollonfig.orderOption,
                    'classes.name': each['name']
                }
            )
            if isExist:
                error_list.append(each['name'])

        if error_list:
            msg = u','.join([_ for _ in error_list]) + u'已存在'
            return self.response_failure(msg=msg)

        for each in newClasses:
            DBOps.setOneDoc(
                DBCollonfig.options,
                {'_id': DBCollonfig.orderOption},
                {
                    '$push': {
                        'classes': {
                            'name': each['name'],
                            'createTime': self.time_conversion(
                                each['time'], 2),
                            'createUser': createUser
                        }
                    }
                }
            )

        return self.response_success()


class AddOrderCustomer(BaseRequest):
    """
        添加订单客户
    """

    def handler_function(self):
        args = self.get_request_data()

        createUser = args.get('createUser', None)
        newCustomers = args.get('customers', None)

        error_list = []
        for each in newCustomers:
            isExist = DBOps.getOneDoc(
                DBCollonfig.options,
                {
                    '_id': DBCollonfig.orderOption,
                    'customers.name': each['name']
                }
            )
            if isExist:
                error_list.append(each['name'])

        if error_list:
            msg = u','.join([_ for _ in error_list]) + u'已存在'
            return self.response_failure(msg=msg)

        for each in newCustomers:
            DBOps.setOneDoc(
                DBCollonfig.options,
                {'_id': DBCollonfig.orderOption},
                {
                    '$push': {
                        'customers': {
                            'name': each['name'],
                            'createTime': self.time_conversion(
                                each['time'], 2),
                            'createUser': createUser
                        }
                    }
                }
            )

        return self.response_success()


class AddOrderContact(BaseRequest):
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

        error_list = []
        for each in newContacts:
            isExist = DBOps.getOneDoc(
                DBCollonfig.options,
                {
                    '_id': DBCollonfig.orderOption,
                    'contacts.name': each['name']
                }
            )
            if isExist:
                error_list.append(each['name'])

        if error_list:
            msg = u','.join([_ for _ in error_list]) + u'已存在'
            return self.response_failure(msg=msg)

        for each in newContacts:
            DBOps.setOneDoc(
                DBCollonfig.options,
                {'_id': DBCollonfig.orderOption},
                {
                    '$push': {
                        'contacts': {
                            'name': each['name'],
                            'createTime': self.time_conversion(
                                each['time'], 2),
                            'createUser': createUser,
                            'tel': tel,
                            'email': email,
                            'qq': qq
                        }
                    }
                }
            )

        return self.response_success()


class AddOrderDpt(BaseRequest):
    """
        添加订单部门选项
    """

    def handler_function(self):
        args = self.get_request_data()

        createUser = args.get('createUser', None)
        newDepartments = args.get('departments', None)

        error_list = []
        for each in newDepartments:
            isExist = DBOps.getOneDoc(
                DBCollonfig.options,
                {
                    '_id': DBCollonfig.orderOption,
                    'departments.name': each['name']
                }
            )
            if isExist:
                error_list.append(each['name'])

        if error_list:
            msg = u','.join([_ for _ in error_list]) + u'已存在'
            return self.response_failure(msg=msg)

        for each in newDepartments:
            DBOps.setOneDoc(
                DBCollonfig.options,
                {'_id': DBCollonfig.orderOption},
                {
                    '$push': {
                        'departments': {
                            'name': each['name'],
                            'createTime': self.time_conversion(
                                each['time'], 2),
                            'createUser': createUser,
                        }
                    }
                }
            )

        return self.response_success()
