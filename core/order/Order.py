#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/15 16:01
# @Author   : cancan
# @File     : Order.py
# @Function : 订单相关操作

import os
import re
import csv
import time
from datetime import datetime, timedelta

from RequestAPI.BaseRequest import BaseRequest
from base.db.DBOps import DBOps
from config.DBCollConfig import DBCollonfig
from config.OrderConfig import OrderConfig
from base.db.LogDBOps import LogDBOps
from config.LogDBConfig import LogDBConfig
from config.Setting import DATETIME_FORMAT, DATE_FORMAT
from core.account.AccountMsg import AccountMsg
from base.time.TimeUtil import TimeUtil
from core.order.OrderUtil import OrderUtil
from base.authentication.AuthenticationUtil import AuthenticationUtil


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
                        'contacts.$.createTimeStamp': TimeUtil.time_conversion(
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
                        'customers.$.createTimeStamp': TimeUtil.time_conversion(
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
    contacts = {}

    def handler_download(self):
        tableData = self.get_argument('tableDate')
        tableType = self.get_argument('tableType')

        filename = tableType + '_' + \
                   datetime.now().strftime('%Y-%m-%d') + '.csv'

        searchParams = {}

        if tableData:
            startDate = time.strptime(tableData, DATE_FORMAT)
            endDateList = tableData.split('-')
            if int(endDateList[1]) + 1 > 12:
                endDateList[0] = '{0:02}'.format(int(endDateList[0]) + 1)
                endDateList[1] = '01'
            else:
                endDateList[1] = '{0:02}'.format(int(endDateList[1]) + 1)
            endDate = time.strptime('-'.join(endDateList), DATE_FORMAT)
            searchParams.update({
                'createTimeStamp': {
                    '$gte': TimeUtil.time_conversion(startDate, 3),
                    '$lte': TimeUtil.time_conversion(endDate, 3)
                }
            })

        if tableType == 'summaryExpect':
            searchParams.update({'status': {'$in': [1, 2]}})
        elif tableType == 'summaryPayment':
            searchParams.update({'status': 3})

        orders = DBOps.getSomeDoc(DBCollonfig.orders, searchParams)

        self.initContactsData()
        self.createToDownload(orders, filename)

    def initContactsData(self):
        """
            初始化外包信息
        """
        contacts = DBOps.getOneDoc(
            DBCollonfig.options,
            {'_id': DBCollonfig.orderContact},
            {'contacts': 1}
        )['contacts']

        for contact in contacts:
            realName = contact['realName']
            payInfo = contact['payInfo']
            self.contacts[contact['name']] = {
                'realName': realName if realName else u'未设置',
                'payInfo': payInfo if payInfo else u'未设置'
            }

    def createToDownload(self, orders, filename):
        """
            获得所有订单
        """

        header = [u'订单ID', u'名称', u'创建时间', u'创建人',
                  u'所属公司', u'类目', u'客户', u'外包人员',
                  u'外包真实姓名', u'外包付款信息',
                  u'预算单价', u'预算数量', u'预算总金额（￥）',
                  u'实际单价', u'实际数量', u'实际总金额（￥）',
                  u'状态（1：制作中；2：待付款；3：已付款）',
                  u'预计完成日期', u'实际完成时间', u'完成付款时间', u'备注']

        rows = []
        for order in orders:
            status = order['status']
            contactInfo = self.contacts.get(order['contactName'], u'该外包已删除')
            if isinstance(contactInfo, dict):
                contactRealName = contactInfo['realName']
                contactPayInfo = contactInfo['payInfo']
            else:
                contactRealName = u'该外包已删除'
                contactPayInfo = u'该外包已删除'
            rows.append((
                order['orderId'],
                order['title'].encode('gbk', 'ignore'),
                order['createTime'],
                order['createUser'].encode('gbk', 'ignore'),
                order['company'].encode('gbk', 'ignore'),
                order['className'].encode('gbk', 'ignore'),
                order['customerName'].encode('gbk', 'ignore'),
                order['contactName'].encode('gbk', 'ignore'),
                contactRealName.encode('gbk', 'ignore'),
                contactPayInfo.encode('gbk', 'ignore'),
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
                order['desc'].encode('gbk', 'ignore')
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

        return res.encode('gbk', 'ignore')

    def create_csv(self, filename, header, rows):
        """
            生成csv
        """
        with open(filename, 'wb') as f:
            f_csv = csv.writer(f)
            f_csv.writerow([x.encode('gbk', 'ignore') for x in header])
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

        nowString = datetime.now().strftime(DATETIME_FORMAT)
        setParams = {}
        if setStatus == 1:
            setParams = self.setStatus1(setStatus, args)
            logAction = LogDBConfig.doEditOrder
            if args['opsUserId'] != args['userId']:
                content = {
                    'status': setStatus,
                    'sendUserId': args['opsUserId'],
                    'rcvUserId': args['userId'],
                    'orderTitle': args['title'],
                    'createUser': args['createUser']
                }
                AccountMsg.setOrderMsg(content)

        elif setStatus == 2:
            setParams = self.setStatus2(setStatus, nowString, args)
            logAction = LogDBConfig.doCompleteOrder
            content = {
                'status': setStatus,
                'sendUserId': args['opsUserId'],
                'rcvUserId': 'summaryUser',
                'orderTitle': args['title'],
                'createUser': args['createUser']
            }
            AccountMsg.setOrderMsg(content)

        elif setStatus == 3:
            setParams = self.setStatus3(setStatus, nowString, args)
            logAction = LogDBConfig.doPaymentOrder
            if args['opsUserId'] != args['userId']:
                content = {
                    'status': setStatus,
                    'sendUserId': args['opsUserId'],
                    'rcvUserId': args['userId'],
                    'orderTitle': args['title'],
                    'createUser': args['createUser']
                }
                AccountMsg.setOrderMsg(content)

        DBOps.setOneDoc(
            DBCollonfig.orders,
            {'_id': orderId},
            {'$set': setParams}
        )

        # 记录日志
        LogDBOps.writeLog(args['opsUserId'], logAction)
        self.result['result'] = {'opsTime': nowString}
        return self.response_success(msg='订单状态修改成功！')

    def setStatus1(self, setStatus, args):
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
            'evaluation': 0,
            'desc': args['desc']
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

        return setParams

    def setStatus2(self, setStatus, nowString, args):
        setParams = {
            'status': setStatus,
            'completeTime': nowString,
            'paymentTime': '',
            'completeTimeStamp': TimeUtil.time_conversion(nowString, 1),
            'paymentTimeStamp': 0,
            'price': args['price'],
            'tax': args['tax'],
            'num': args['num'],
            'unit': args['unit'],
            'unitNum': args['unitNum'],
            'evaluation': args['evaluation'],
            'sumPrice': round(args['sumPrice'], 2),
            'desc': args['desc']
        }

        return setParams

    def setStatus3(self, setStatus, nowString, args):
        setParams = {
            'status': setStatus,
            'paymentTime': nowString,
            'paymentTimeStamp': TimeUtil.time_conversion(nowString, 1),
            'desc': args['desc']
        }

        return setParams


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

        userId = AuthenticationUtil.getUserIdByToken(self.request)

        startDate, endDate, searchParams = self.getSearchParams(args['search'])

        orders = None
        if args['orderListType'] == 'self':
            searchParams.update({'userId': userId})
            orders = DBOps.getSomeDoc(DBCollonfig.orders, searchParams)
        elif args['orderListType'] == 'company':
            company = DBOps.getOneDoc(
                DBCollonfig.users,
                {'_id': userId},
                {'company': 1}
            )['company']
            searchParams.update({'company': company})
            orders = DBOps.getSomeDoc(DBCollonfig.orders, searchParams)
        elif args['orderListType'] == 'summary':
            orders = DBOps.getSomeDoc(DBCollonfig.orders, searchParams)

        self.result['result'] = {
            'orders': list(orders.sort('createTimeStamp', -1)),
            'searchDate': [startDate.split(' ')[0], endDate.split(' ')[0]],
            'totalCount': orders.count()
        }
        return self.response_success()

    def getSearchParams(self, search):
        """
            生成筛选条件
        """
        if search['date']:
            startDate = search['date'][0] + ' 00:00:00'
            endDate = search['date'][1] + ' 23:59:59'
        else:
            now = datetime.now()
            endDate = now.strftime('%Y-%m-%d') + ' 23:59:59'
            startDate = (now - timedelta(days=15)).strftime('%Y-%m-%d') + \
                        ' 00:00:00'

        # 订单创建日期
        searchParams = {
            'createTimeStamp': {
                '$gte': TimeUtil.time_conversion(startDate, 1),
                '$lte': TimeUtil.time_conversion(endDate, 1)
            },
        }

        # 订单名称
        if search['title']:
            searchParams.update({
                'title': {'$regex': search['title']}
            })

        # 订单状态
        if search['status'] != -1:
            searchParams.update({
                'status': search['status']
            })

        # 订单所属公司
        if search.get('company', 'all') != 'all':
            searchParams.update({
                'company': search['company']
            })

        # 订单客户
        if search['customer'] != 'all':
            searchParams.update({
                'customerName': search['customer']
            })

        # 订单外包人员
        if search['contact'] != 'all':
            searchParams.update({
                'contactName': search['contact']
            })

        return startDate, endDate, searchParams


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
            'createTimeStamp': TimeUtil.time_conversion(nowString, 1),
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
        companies = orderOptions['companies']
        helpInfo = orderOptions['helpInfo']

        self.result['result'] = {
            'classes': [
                {'label': cl['name'], 'value': cl['name']} for cl in classes
            ],
            'customers': [
                {'label': cu['name'], 'value': cu['name']} for cu in customers
            ],
            'contacts': [
                {
                    'label': con['name'] + ' | ' + con['workClass'],
                    'value': con['name']
                } for con in contacts
            ],
            'companies': [
                {'label': com['name'], 'value': com['name']}
                for com in companies
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
            self.result['result'] = self.initContactsData(args, initData)
        elif args['optionType'] == 'customers':
            self.result['result'] = self.initCustomersData(args, initData)
        else:
            self.result['result'] = OrderUtil.orderListByTime(initData)
        return self.response_success()

    def initCustomersData(self, args, initData):
        """
            初始化客户信息
        """
        # 搜索删选
        keyName = args['keyName']
        orderCustomers = OrderUtil.orderListByTime(initData)

        if keyName:
            try:
                totalCustomers = [
                    o for o in orderCustomers
                    if re.match(r'.*' + keyName + '.*', o['name'])
                ]
            except Exception as e:
                totalCustomers = []
        else:
            totalCustomers = orderCustomers

        page = args['page']
        pageSize = OrderConfig.optionPageSize
        pageStart = (page - 1) * pageSize
        pageEnd = page * pageSize
        customers = totalCustomers[pageStart:pageEnd]

        return {
            'customers': customers,
            'totalCount': len(totalCustomers),
            'pageSize': OrderConfig.optionPageSize
        }

    def initContactsData(self, args, initData):
        """
            初始化外包人员信息
        """

        # 搜索删选
        keyName = args['keyName']
        workClass = args['workClass']
        orderContacts = OrderUtil.orderListByTime(initData)

        if keyName or workClass:
            try:
                totalContacts = [
                    o for o in orderContacts
                    if re.match(r'.*' + keyName + '.*', o['name']) and \
                       re.match(workClass, o['workClass'])
                ]
            except Exception as e:
                totalContacts = []
        else:
            totalContacts = orderContacts

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

        return {
            'contacts': contacts,
            'totalCount': len(totalContacts),
            'pageSize': OrderConfig.optionPageSize,
            'workClasses': [
                {'label': w['name'], 'value': w['name']}
                for w in workClasses
            ],
        }


class DelOrderOption(BaseRequest):
    """
        删除订单选项
    """

    LogAction = {
        'classes': LogDBConfig.doDelClass,
        'customers': LogDBConfig.doDelCustomer,
        'contacts': LogDBConfig.doDelContact,
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
            msg = u','.join([err for err in error_list]) + u'已存在'
            return self.response_failure(msg=msg)

        for each in newClasses:
            DBOps.setOneDoc(
                DBCollonfig.options,
                {'_id': DBCollonfig.orderOption},
                {
                    '$push': {
                        'classes': {
                            'name': each['name'],
                            'createTime': TimeUtil.time_conversion(
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
            msg = u','.join([err for err in error_list]) + u'已存在'
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
                            'createTime': TimeUtil.time_conversion(
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
            msg = u','.join([err for err in error_list]) + u'已存在'
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
                            'createTime': TimeUtil.time_conversion(
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
            msg = u','.join([err for err in error_list]) + u'已存在'
            return self.response_failure(msg=msg)

        for each in newDepartments:
            DBOps.setOneDoc(
                DBCollonfig.options,
                {'_id': DBCollonfig.orderOption},
                {
                    '$push': {
                        'departments': {
                            'name': each['name'],
                            'createTime': TimeUtil.time_conversion(
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
                        'createTimeStamp': TimeUtil.time_conversion(now, 1)
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
                    'workClasses.name': each['name']
                }
            )
            if isExist:
                error_list.append(each['name'])

        if error_list:
            msg = u','.join([err for err in error_list]) + u'已存在'
            return self.response_failure(msg=msg)

        for each in newWorkClasswss:
            DBOps.setOneDoc(
                DBCollonfig.options,
                {'_id': DBCollonfig.orderOption},
                {
                    '$push': {
                        'workClasses': {
                            'name': each['name'],
                            'createTime': TimeUtil.time_conversion(
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
            msg = u','.join([err for err in error_list]) + u'已存在'
            return self.response_failure(msg=msg)

        for each in newCompanies:
            DBOps.setOneDoc(
                DBCollonfig.options,
                {'_id': DBCollonfig.orderOption},
                {
                    '$push': {
                        'companies': {
                            'name': each['name'],
                            'createTime': TimeUtil.time_conversion(
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
