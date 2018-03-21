#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/15 16:01
# @Author   : cancan
# @File     : Order.py
# @Function : 订单相关操作

import os
import csv
from datetime import datetime, timedelta

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
                  u'部门', u'类目', u'客户', u'外包人员', u'金额（￥）',
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

        nowString = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        setParams = {}
        if setStatus == 1:
            setParams = {
                'status': setStatus,
                'completeTime': '',
                'paymentTime': '',
                'completeTimeStamp': 0,
                'paymentTimeStamp': 0,
                'expect': {
                    'price': args['price'],
                    'tax': args['tax'],
                    'num': args['num'],
                    'unit': args['unit']
                },
                'price': args['price'],
                'tax': args['tax'],
                'num': args['num'],
                'unit': args['unit'],
                'evaluation': 0
            }
        elif setStatus == 2:
            setParams = {
                'status': setStatus,
                'completeTime': nowString,
                'paymentTime': '',
                'completeTimeStamp': self.time_conversion(nowString, 1),
                'paymentTimeStamp': 0,
                'price': args['price'],
                'tax': args['tax'],
                'num': args['num'],
                'unit': args['unit'],
                'evaluation': args['evaluation']
            }
        elif setStatus == 3:
            setParams = {
                'status': setStatus,
                'paymentTime': nowString,
                'paymentTimeStamp': self.time_conversion(nowString, 1)
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

        search = args['search']
        if search['date']:
            startDate = search['date'][0] + ' 00:00:00'
            endDate = search['date'][1] + ' 23:59:59'
        else:
            now = datetime.now()
            endDate = now.strftime('%Y-%m-%d') + ' 23:59:59'
            startDate = (now - timedelta(days=15)).strftime('%Y-%m-%d') + \
                        ' 00:00:00'

        searchParams = {
            'createTimeStamp': {
                '$gte': self.time_conversion(startDate, 1),
                '$lte': self.time_conversion(endDate, 1)
            },
        }

        if search['status'] != -1:
            searchParams.update({
                'status': search['status']
            })

        orders = []
        if args['orderListType'] == 'self':
            params = {'userId': userId}
            params.update(searchParams)
            orders = DBOps.getSomeDoc(DBCollonfig.orders, params)
        elif args['orderListType'] == 'department':
            department = DBOps.getOneDoc(
                DBCollonfig.users,
                {'_id': userId},
                {'department': 1}
            )['department']
            params = {'department': department}
            params.update(searchParams)
            orders = DBOps.getSomeDoc(DBCollonfig.orders, params)
        elif args['orderListType'] == 'summary':
            orders = DBOps.getSomeDoc(DBCollonfig.orders, searchParams)

        self.result['result'] = {
            'orders': self.orderListByTime(orders),
            'searchDate': [startDate.split(' ')[0], endDate.split(' ')[0]]
        }
        return self.response_success()


class CreateOrder(BaseRequest):
    """
        创建订单
    """

    def handler_function(self):
        args = self.get_request_data()

        now = datetime.now()
        orderId = str(args['userId']) + now.strftime('%Y%m%d%H%M%S')
        nowString = now.strftime('%Y-%m-%d %H:%M:%S')
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
            'expect': {
                'price': args['price'],
                'tax': args['tax'],
                'num': args['num'],
                'unit': args['unit'],
            },
            'price': args['price'],
            'tax': args['tax'],
            'num': args['num'],
            'unit': args['unit'],
            'desc': args['desc'],
            'createTime': nowString,
            'completeTime': '',
            'paymentTime': '',
            'createTimeStamp': self.time_conversion(nowString, 1),
            'completeTimeStamp': 0,
            'paymentTimeStamp': 0,
            'status': 1,
            'evaluation': 0
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
                                each['time'], 2
                            ),
                            'createTimeStamp': each['time'],
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
                                each['time'], 2
                            ),
                            'createTimeStamp': each['time'],
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
                                each['time'], 2
                            ),
                            'createTimeStamp': each['time'],
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
                                each['time'], 2
                            ),
                            'createTimeStamp': each['time'],
                            'createUser': createUser,
                        }
                    }
                }
            )

        return self.response_success()
