#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/4/4 12:51
# @Author   : cancan
# @File     : Statistics.py
# @Function : 订单统计

from RequestAPI.BaseRequest import BaseRequest
from base.db.DBOps import DBOps
from config.DBCollConfig import DBCollonfig


class ContactUseTop10(BaseRequest):
    """
        外包人员使用top10
    """

    def handler_function(self):
        params = [{
            '$group': {'_id': '$contactName', 'num': {'$sum': 1}}
        }, {
            '$sort': {'num': -1}
        }]
        top10Contacts = list(DBOps.getAggregate(DBCollonfig.orders, params))

        if top10Contacts:
            if len(top10Contacts) <= 10:
                self.result['result'] = top10Contacts
            else:
                self.result['result'] = top10Contacts[:10]
            return self.response_success()
        else:
            return self.response_failure(msg=u'暂无数据')

