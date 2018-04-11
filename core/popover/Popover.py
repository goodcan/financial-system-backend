#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/4/11 17:27
# @Author   : cancan
# @File     : Popover.py
# @Function : popover信息

from RequestAPI.BaseRequest import BaseRequest
from config.DBCollConfig import DBCollonfig
from base.db.DBOps import DBOps


class getCustomerPopover(BaseRequest):
    """
        获得客户的popover信息
    """

    def handler_function(self):
        args = self.get_request_data()

        customerData = DBOps.getOneDoc(
            DBCollonfig.options,
            {
                '_id': DBCollonfig.orderCustomer,
                'customers.name': args['customerName']
            },
            {'customers.$': 1}
        )
        if customerData:
            self.result['result'] = customerData['customers'][0]
            self.response_success()
        else:
            self.response_failure(msg=u'该客户已删除')


class getContactPopover(BaseRequest):
    """
        获得客户的popover信息
    """

    def handler_function(self):
        args = self.get_request_data()

        customerData = DBOps.getOneDoc(
            DBCollonfig.options,
            {
                '_id': DBCollonfig.orderCustomer,
                'contacts.name': args['contactName']
            },
            {'contacts.$': 1}
        )
        if customerData:
            self.result['result'] = customerData['contacts'][0]
            self.response_success()
        else:
            self.response_failure(msg=u'该外包已删除')
