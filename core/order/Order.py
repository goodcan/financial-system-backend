#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/15 16:01
# @Author   : cancan
# @File     : Order.py
# @Function : 订单相关操作

import os
import csv
from datetime import datetime

from RequestAPI.BaseRequest import BaseRequest
from base.db.DBOps import DBOps
from config.DBCollConfig import DBCollonfig


class DownloadTable(BaseRequest):
    """
        下载汇总表
    """

    downloadPath = os.path.dirname(__file__).split('core')[0] + 'downloadData/'

    def handler_download(self):
        tableType = self.get_argument('tableType')

        filename = tableType + '_' + \
                   datetime.now().strftime('%Y-%m-%d') + '.csv'
        orders = None
        if tableType == 'summaryAll':
            orders = DBOps.getSomeDoc(DBCollonfig.orders, {})
        elif tableType == 'summaryExpect':
            orders = DBOps.getSomeDoc(
                DBCollonfig.orders,
                {'status': {'$in': [1, 2]}}
            )
        elif tableType == 'summaryPayment':
            orders = DBOps.getSomeDoc(
                DBCollonfig.orders,
                {'status': 3}
            )

        self.createToDownload(orders, filename)

    def createToDownload(self, orders, filename):
        """
            获得所有订单
        """

        header = [u'订单ID', u'名称', u'创建时间', u'创建人',
                  u'部门', u'类目', u'客户', u'对接人员', u'金额（￥）',
                  u'状态（1：制作中；2：待付款；3：已付款）',
                  u'预计完成日期', u'实际完成时间', u'完成付款时间', u'备注']

        rows = []
        for order in orders:
            rows.append((
                order['orderId'],
                order['title'].encode('gbk'),
                order['createTime'],
                order['createUser'].encode('gbk'),
                order['department'].encode('gbk'),
                order['className'].encode('gbk'),
                order['customerName'].encode('gbk'),
                order['contactName'].encode('gbk'),
                order['price'],
                order['status'],
                order['expectDate'],
                order['completeTime'],
                order['paymentTime'],
                order['desc'].encode('gbk')
            ))

        path = self.downloadPath + filename
        self.create_csv(path, header, rows)

        self.download_file(path, filename)

    def create_csv(self, filename, header, rows):
        """
            生成csv
        """
        with open(filename, 'wb') as f:
            f_csv = csv.writer(f)
            f_csv.writerow([x.encode('gbk') for x in header])
            f_csv.writerows(rows)

    def download_file(self, path, filename):
        """
        文件下载
        """
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition',
                        'attachment; filename=' + filename)
        buf_size = 4096

        with open(path, 'rb') as f:
            while True:
                data = f.read(buf_size)
                if not data:
                    break
                self.write(data)

        self.finish()

class EditOrderStatus(BaseRequest):
    """
        编辑订单状态
    """

    def handler_function(self):
        args = self.get_request_data()

        setStatus = args.get('status', None)
        orderId = args.get('orderId', None)

        nowStatus = DBOps.getOneDoc(
            DBCollonfig.orders,
            {'_id': orderId}
        )['status']

        if nowStatus == setStatus:
            return self.response_failure(msg='订单状态已被修改！')

        setParams = {}
        if setStatus == 1:
            setParams = {
                'status': setStatus,
                'completeTime': '',
                'paymentTime': ''
            }
        elif setStatus == 2:
            setParams = {
                'status': setStatus,
                'completeTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'paymentTime': ''
            }
        elif setStatus == 3:
            setParams = {
                'status': setStatus,
                'paymentTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        DBOps.setOneDoc(
            DBCollonfig.orders,
            {'_id': orderId},
            {'$set': setParams}
        )

        return self.response_success(msg='订单状态修改成功！')


class DelOrder(BaseRequest):
    """
        删除订单
    """

    def handler_function(self):
        args = self.get_request_data()

        DBOps.removeDoc(DBCollonfig.orders, {'_id': args['orderId']})

        self.response_success()


class OrderList(BaseRequest):
    """
        订单列表
    """

    def handler_function(self):
        args = self.get_request_data()

        userId = self.getUserIdByToken()

        if args['orderListType'] == 'self':
            self.result['result'] = self.getSelfOrderList(userId)
        elif args['orderListType'] == 'department':
            department = DBOps.getOneDoc(
                DBCollonfig.users,
                {'_id': userId},
                {'department': 1}
            )['department']
            self.result['result'] = self.getDptOrderList(department)
        elif args['orderListType'] == 'summary':
            self.result['result'] = self.getSummaryOrderList()

        return self.response_success()

    def getSummaryOrderList(self):
        """
            获得所有的订单列表
        """
        orders = DBOps.getSomeDoc(DBCollonfig.orders, {})

        return self.orderListByTime(orders)

    def getDptOrderList(self, department):
        """
            获得部门的订单列表
        """
        orders = DBOps.getSomeDoc(
            DBCollonfig.orders,
            {'department': department}
        )

        return self.orderListByTime(orders)

    def getSelfOrderList(self, userId):
        """
            获得紫的订单列表
        """

        orders = DBOps.getSomeDoc(DBCollonfig.orders, {'userId': userId})

        return self.orderListByTime(orders)


class CreateOrder(BaseRequest):
    """
        创建订单
    """

    def handler_function(self):
        args = self.get_request_data()

        now = datetime.now()
        orderId = str(args['userId']) + now.strftime('%Y%m%d%H%M%S')
        order = {
            '_id': orderId,
            'orderId': orderId,
            'userId': args['userId'],
            'title': args['title'],
            'createUser': args['createUser'],
            'department': args['department'],
            'className': args['className'],
            'customerName': args['customerName'],
            'contactName': args['contactName'],
            'expectDate': args['expectDate'],
            'price': args['price'],
            'desc': args['desc'],
            'createTime': now.strftime('%Y-%m-%d %H:%M:%S'),
            'completeTime': '',
            'paymentTime': '',
            'status': 1
        }

        DBOps.insertDoc(DBCollonfig.orders, order)

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


class OrderOptionInitData(BaseRequest):
    """
        设置订单选项时的初始数据
    """

    def handler_function(self):
        args = self.get_request_data()

        initData = DBOps.getOneDoc(
            DBCollonfig.options,
            {'_id': DBCollonfig.orderOption},
            {args['optionType']: 1}
        )[args['optionType']]

        self.result['result'] = self.orderListByTime(initData)
        return self.response_success()


class DelOrderOption(BaseRequest):
    """
        删除订单选项
    """

    def handler_function(self):
        args = self.get_request_data()

        DBOps.setOneDoc(
            DBCollonfig.options,
            {'_id': DBCollonfig.orderOption},
            {
                '$pull': {
                    args['optionType']: {
                        'name': args['name']
                    }
                }
            }
        )

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
