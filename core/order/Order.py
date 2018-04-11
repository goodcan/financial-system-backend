#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/15 16:01
# @Author   : cancan
# @File     : Order.py
# @Function : 订单相关操作

import os
import re
import csv
from datetime import datetime, timedelta

from RequestAPI.BaseRequest import BaseRequest
from base.db.DBOps import DBOps
from config.DBCollConfig import DBCollonfig
from config.OrderConfig import OrderConfig
from base.db.LogDBOps import LogDBOps
from config.LogDBConfig import LogDBConfig


class WriteDownloadLog(BaseRequest):
    """
        记录下载日志
    """

    def handler_function(self):
        args = self.get_request_data()
        # 记录日志
        LogDBOps.writeLog(args['opsUserId'], LogDBConfig.doDownloadTable)


class EditOrderOption(BaseRequest):
    """
        编辑订单选项
    """

    def handler_function(self):
        args = self.get_request_data()
        option = args['option']
        createUser = args['createUser']
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if args['optionType'] == 'contacts':
            oldContact = DBOps.getOneDoc(
                DBCollonfig.options,
                {
                    '_id': DBCollonfig.orderContact,
                    'contacts.name': option['oldName']
                }
            )
            if not oldContact:
                return self.response_failure(msg=u'外包人员不存在')
            DBOps.setOneDoc(
                DBCollonfig.options,
                {
                    '_id': DBCollonfig.orderContact,
                    'contacts.name': option['oldName']
                },
                {
                    '$set': {
                        'contacts.$.name': option['name'],
                        'contacts.$.realName': option['realName'],
                        'contacts.$.tel': option['tel'],
                        'contacts.$.email': option['email'],
                        'contacts.$.workClass': option['workClass'],
                        'contacts.$.payInfo': option['payInfo'],
                        'contacts.$.qq': option['qq'],
                        'contacts.$.createUser': createUser,
                        'contacts.$.createTime': now,
                        'contacts.$.createTimeStamp': self.time_conversion(
                            now, 1
                        ),
                    }
                }
            )

            # 记录日志
            LogDBOps.writeLog(args['opsUserId'], LogDBConfig.doEditContact)

            return self.response_success()
        elif args['optionType'] == 'customers':
            DBOps.setOneDoc(
                DBCollonfig.options,
                {
                    '_id': DBCollonfig.orderCustomer,
                    'customers.name': option['name']
                },
                {
                    '$set': {
                        'customers.$.billInfo': option['billInfo'],
                        'customers.$.mailAddress': option['mailAddress'],
                        'customers.$.createUser': createUser,
                        'customers.$.createTime': now,
                        'customers.$.createTimeStamp': self.time_conversion(
                            now, 1
                        ),
                    }
                }
            )

            # 记录日志
            LogDBOps.writeLog(args['opsUserId'], LogDBConfig.doEditCustomer)

            return self.response_success()
        else:
            return self.response_failure(msg=u'没有需要修改的信息')


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
                  u'部门', u'类目', u'客户', u'外包人员',
                  u'预算单价', u'预算数量', u'预算总金额（￥）',
                  u'实际单价', u'实际数量', u'实际总金额（￥）',
                  u'状态（1：制作中；2：待付款；3：已付款）',
                  u'预计完成日期', u'实际完成时间', u'完成付款时间', u'备注']

        rows = []
        for order in orders:
            status = order['status']
            rows.append((
                order['orderId'],
                order['title'].encode('gbk'),
                order['createTime'],
                order['createUser'].encode('gbk'),
                order['department'].encode('gbk'),
                order['className'].encode('gbk'),
                order['customerName'].encode('gbk'),
                order['contactName'].encode('gbk'),
                self.getUnitPrice(order, 1),
                order['expect']['num'],
                order['expect']['sumPrice'],
                self.getUnitPrice(order) if status > 1 else '',
                order['num'] if status > 1 else '',
                order['sumPrice'] if status > 1 else '',
                status,
                order['expectDate'],
                order['completeTime'],
                order['paymentTime'],
                order['desc'].encode('gbk')
            ))

        path = self.downloadPath + filename
        self.create_csv(path, header, rows)

        self.download_file(path, filename)

    def getUnitPrice(self, order, choose=None):
        """
            显示单价
        """
        if choose == 1:
            res = OrderConfig.Tax[order['expect']['tax']] + ' | ' + \
                  str(order['expect']['unitNum']) + \
                  OrderConfig.Unit[order['expect']['unit']] + ' | ' + \
                  str(order['expect']['price'])
        else:
            res = OrderConfig.Tax[order['tax']] + ' | ' + \
                  str(order['unitNum']) + \
                  OrderConfig.Unit[order['unit']] + ' | ' + \
                  str(order['price'])

        return res.encode('gbk')

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

        logAction = None

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
                    'unit': args['unit'],
                    'unitNum': args['unitNum'],
                    'sumPrice': round(args['sumPrice'], 2),
                },
                'price': args['price'],
                'tax': args['tax'],
                'num': args['num'],
                'unit': args['unit'],
                'unitNum': args['unitNum'],
                'sumPrice': round(args['sumPrice'], 2),
                'evaluation': 0
            }

            # 订单统计用户修改订单其他信息
            if args.get('isCanEdit', ''):
                setParams.update({
                    'title': args['title'],
                    'className': args['className'],
                    'customerName': args['customerName'],
                    'contactName': args['contactName'],
                    # 'department': args['department'],
                    'company': args['company'],
                    'desc': args['desc']
                })

            # 记录日志时的操作说明
            logAction = LogDBConfig.doEditOrder

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
                'unitNum': args['unitNum'],
                'evaluation': args['evaluation'],
                'sumPrice': round(args['sumPrice'], 2)
            }

            # 记录日志时的操作说明
            logAction = LogDBConfig.doCompleteOrder

        elif setStatus == 3:
            setParams = {
                'status': setStatus,
                'paymentTime': nowString,
                'paymentTimeStamp': self.time_conversion(nowString, 1)
            }

            # 记录日志时的操作说明
            logAction = LogDBConfig.doPaymentOrder

        DBOps.setOneDoc(
            DBCollonfig.orders,
            {'_id': orderId},
            {'$set': setParams}
        )

        # 记录日志
        LogDBOps.writeLog(args['opsUserId'], logAction)
        self.result['result'] = {'opsTime': nowString}
        return self.response_success(msg='订单状态修改成功！')


class DelOrder(BaseRequest):
    """
        删除订单
    """

    def handler_function(self):
        args = self.get_request_data()

        DBOps.removeDoc(DBCollonfig.orders, {'_id': args['orderId']})

        # 记录日志
        LogDBOps.writeLog(args['opsUserId'], LogDBConfig.doDelOrder)

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
        elif args['orderListType'] == 'company':
            company = DBOps.getOneDoc(
                DBCollonfig.users,
                {'_id': userId},
                {'company': 1}
            )['company']
            params = {'company': company}
            params.update(searchParams)
            orders = DBOps.getSomeDoc(DBCollonfig.orders, params)
        # elif args['orderListType'] == 'department':
        #     department = DBOps.getOneDoc(
        #         DBCollonfig.users,
        #         {'_id': userId},
        #         {'department': 1}
        #     )['department']
        #     params = {'department': department}
        #     params.update(searchParams)
        #     orders = DBOps.getSomeDoc(DBCollonfig.orders, params)
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
            # 'department': args['department'],
            'company': args['company'],
            'className': args['className'],
            'customerName': args['customerName'],
            'contactName': args['contactName'],
            'expectDate': args['expectDate'],
            'expect': {
                'price': args['price'],
                'tax': args['tax'],
                'num': args['num'],
                'unit': args['unit'],
                'unitNum': args['unitNum'],
                'sumPrice': round(args['sumPrice'], 2),
            },
            'price': args['price'],
            'sumPrice': round(args['sumPrice'], 2),
            'tax': args['tax'],
            'num': args['num'],
            'unit': args['unit'],
            'unitNum': args['unitNum'],
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

        # 记录日志
        LogDBOps.writeLog(args['userId'], LogDBConfig.doCreateOrder)

        self.response_success()


class OrderInitData(BaseRequest):
    """
        初始化订单数据
    """

    def handler_function(self):
        orderOptions = DBOps.getOneDoc(
            DBCollonfig.options,
            {'_id': DBCollonfig.orderOption},
            {'workClasses': 0}
        )
        classes = orderOptions['classes']
        customers = orderOptions['customers']
        contacts = orderOptions['contacts']
        # departments = orderOptions['departments']
        companies = orderOptions['companies']
        helpInfo = orderOptions['helpInfo']

        self.result['result'] = {
            'classes': [
                {'label': _['name'], 'value': _['name']} for _ in classes
            ],
            'customers': [
                {'label': _['name'], 'value': _['name']} for _ in customers
            ],
            'contacts': [
                {
                    'label': _['name'] + ' | ' + _['workClass'],
                    'value': _['name']
                } for _ in contacts
            ],
            'companies': [
                {'label': _['name'], 'value': _['name']} for _ in companies
            ],
            'helpInfo': helpInfo
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

        if args['optionType'] == 'contacts':

            # 搜索删选
            keyName = args['keyName']
            workClass = args['workClass']
            orderContacts = self.orderListByTime(initData)

            try:
                totalContacts = [
                    _ for _ in orderContacts
                    if re.match(r'.*' + keyName + '.*', _['name']) and \
                       re.match(workClass, _['workClass'])
                ]
            except Exception as e:
                totalContacts = []

            # 分页处理
            page = args['page']
            pageSize = OrderConfig.optionPageSize
            pageStart = (page - 1) * pageSize
            pageEnd = page * pageSize
            contacts = totalContacts[pageStart:pageEnd]

            workClasses = DBOps.getOneDoc(
                DBCollonfig.options,
                {'_id': DBCollonfig.orderOption},
                {'workClasses': 1}
            )['workClasses']
            self.result['result'] = {
                'contacts': contacts,
                'totalCount': len(totalContacts),
                'pageSize': OrderConfig.optionPageSize,
                'workClasses': [
                    {'label': _['name'], 'value': _['name']}
                    for _ in workClasses
                ],
            }
        else:
            self.result['result'] = self.orderListByTime(initData)
        return self.response_success()


class DelOrderOption(BaseRequest):
    """
        删除订单选项
    """

    LogAction = {
        'classes': LogDBConfig.doDelClass,
        'customers': LogDBConfig.doDelCustomer,
        'contacts': LogDBConfig.doDelContact,
        'departments': LogDBConfig.doDelDepartment,
        'workClasses': LogDBConfig.doDelWorkClass,
        'companies': LogDBConfig.doDelCompany
    }

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

        # 记录日志
        LogDBOps.writeLog(args['opsUserId'], self.LogAction[args['optionType']])

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

        # 记录日志
        LogDBOps.writeLog(args['opsUserId'], LogDBConfig.doCreateClass)

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
                            'billInfo': each['billInfo'],
                            'mailAddress': each['mailAddress'],
                            'createTime': self.time_conversion(
                                each['time'], 2
                            ),
                            'createTimeStamp': each['time'],
                            'createUser': createUser
                        }
                    }
                }
            )

        # 记录日志
        LogDBOps.writeLog(args['opsUserId'], LogDBConfig.doCreateCustomer)

        return self.response_success()


class AddOrderContact(BaseRequest):
    """
        添加订单客户
    """

    def handler_function(self):
        args = self.get_request_data()

        createUser = args.get('createUser', None)
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
                            'realName': each['realName'],
                            'createTime': self.time_conversion(
                                each['time'], 2
                            ),
                            'createTimeStamp': each['time'],
                            'createUser': createUser,
                            'tel': each['tel'],
                            'email': each['email'],
                            'qq': each['qq'],
                            'payInfo': each['payInfo'],
                            'workClass': each['workClass']
                        }
                    }
                }
            )

        # 记录日志
        LogDBOps.writeLog(args['opsUserId'], LogDBConfig.doCreateContact)

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

        # 记录日志
        LogDBOps.writeLog(args['opsUserId'], LogDBConfig.doCreateDepartment)

        return self.response_success()


class AddOrderHelpInfo(BaseRequest):
    """
        添加订单帮助信息
    """

    def handler_function(self):
        args = self.get_request_data()

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        DBOps.setOneDoc(
            DBCollonfig.options,
            {'_id': DBCollonfig.orderHelpInfo},
            {
                '$set': {
                    'helpInfo': [{
                        'content': args['helpInfo'],
                        'createTime': now,
                        'createTimeStamp': self.time_conversion(now, 1)
                    }]
                }
            }
        )

        # 记录日志
        LogDBOps.writeLog(args['opsUserId'], LogDBConfig.doEditHelpInfo)

        return self.response_success()


class AddWorkClass(BaseRequest):
    """
        添加订单部门选项
    """

    def handler_function(self):
        args = self.get_request_data()

        createUser = args.get('createUser', None)
        newWorkClasswss = args.get('workClasses', None)

        error_list = []
        for each in newWorkClasswss:
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

        for each in newWorkClasswss:
            DBOps.setOneDoc(
                DBCollonfig.options,
                {'_id': DBCollonfig.orderOption},
                {
                    '$push': {
                        'workClasses': {
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

        # 记录日志
        LogDBOps.writeLog(args['opsUserId'], LogDBConfig.doCreateWorkClass)

        return self.response_success()

class AddOrderCompany(BaseRequest):
    """
        添加订单部门选项
    """

    def handler_function(self):
        args = self.get_request_data()

        createUser = args.get('createUser', None)
        newCompanies = args.get('companies', None)

        error_list = []
        for each in newCompanies:
            isExist = DBOps.getOneDoc(
                DBCollonfig.options,
                {
                    '_id': DBCollonfig.orderOption,
                    'companies.name': each['name']
                }
            )
            if isExist:
                error_list.append(each['name'])

        if error_list:
            msg = u','.join([_ for _ in error_list]) + u'已存在'
            return self.response_failure(msg=msg)

        for each in newCompanies:
            DBOps.setOneDoc(
                DBCollonfig.options,
                {'_id': DBCollonfig.orderOption},
                {
                    '$push': {
                        'companies': {
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

        # 记录日志
        LogDBOps.writeLog(args['opsUserId'], LogDBConfig.doCreateCompany)

        return self.response_success()


