#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/4/29 下午2:46
# @Author   : cancan
# @File     : AccountMsg.py
# @Function : 用户统计信息相关操作
from datetime import datetime
from copy import deepcopy

from base.db.DBOps import DBOps
from config.Setting import DATETIME_FORMATE
from config.DBCollConfig import DBCollonfig
from base.time.TimeUtil import TimeUtil


class AccountMsg(object):
    """
        用户统计信息相关操作
    """

    baseData = {
        'sendUserId': None,  # 发送信息的人
        'sendTime': None,
        'sendTimeStamp': None,
        'rcvUserId': None,
        'isRead': False,
        'readTime': None,
        'readTimeStamp': None,
        'type': None,
        'content': None
    }

    @classmethod
    def writeToDB(cls, msg, status):

        if status == 2:
            DBOps.setOneDoc(
                DBCollonfig.users,
                {'permissions.summaryOrder': 1},
                {
                    '$push': {
                        'msg': msg
                    }
                },
                multi=True
            )
        elif status == 3:
            DBOps.setOneDoc(
                DBCollonfig.users,
                {'_id': msg['rcvUserId']},
                {
                    '$push': {
                        'msg': msg
                    }
                },
            )

    @classmethod
    def setOrderMsg(cls, content):
        msg = deepcopy(cls.baseData)
        msg['sendUserId'] = content['sendUserId']
        msg['rcvUserId'] = content['rcvUserId']
        msg['sendTime'] = datetime.now().strftime(DATETIME_FORMATE)
        msg['sendTimeStamp'] = TimeUtil.time_conversion(
            msg['sendTime'], 1
        )
        msg['type'] = 'order'
        msg['content'] = content

        cls.writeToDB(msg, content['status'])
