#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/4/29 下午1:56
# @Author   : cancan
# @File     : Message.py
# @Function : 消息系统

from RequestAPI.BaseRequest import BaseRequest
from base.db.DBOps import DBOps
from config.DBCollConfig import DBCollonfig


class ClearBadgeMsg(BaseRequest):
    """
        清楚红点信息
    """

class CheckMsg(BaseRequest):
    """
        检测是否有新的消息
    """

    def handler_function(self):
        args = self.get_request_data()
        data = DBOps.getOneDoc(
            DBCollonfig.users,
            {
                '_id': args['userId'],
            },
            {'msg': 1}
        )
        msg = data.get('msg', None) if data else None
        resMsg = sorted(
            msg, key=lambda x: x['sendTimeStamp'], reverse=True
        ) if msg else []

        showBadge = False
        for each in resMsg:
            if not each['isRead']:
                showBadge = True

        self.result['result'] = {
            'msg': resMsg,
            'showBadge': showBadge
        }

        self.response_success()
