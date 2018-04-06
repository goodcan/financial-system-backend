#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/4/5 下午3:44
# @Author   : cancan
# @File     : LogDBOps.py
# @Function : 日志数据库操作
import time
from datetime import datetime

from config.DBCollConfig import DBCollonfig
from config.LogDBConfig import LogDBConfig
from base.db.DBOps import DBOps


class LogDBOps(object):
    """
        日志数据库操作
    """

    @classmethod
    def writeLog(cls, userId, action, content=None):
        """
            基础结构
        """
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = {
            'logTime': now,
            'logTimeStamp': int(
                time.mktime(time.strptime(now, '%Y-%m-%d %H:%M:%S')) * 1000
            ),
            'userId': userId,
            'action': action,
            'contact': content
        }

        DBOps.insertDoc(DBCollonfig.log, data)

    @classmethod
    def getlist(cls, page, pageSize):
        skip = (page - 1) * pageSize

        # 条件搜搜参数
        params = [{
            '$lookup': {
                'from': "users",
                'localField': "userId",
                'foreignField': "_id",
                'as': "user"
            }
        }, {
            '$sort': {'logTimeStamp': -1},
        }, {
            '$skip': skip
        }, {
            '$limit': pageSize
        }]

        searchLogs = DBOps.getAggregate(DBCollonfig.log, params)

        resLogs = []
        for log in searchLogs:
            resLogs.append({
                'userId': log['userId'],
                'username': log['user'][0]['username'],
                'logTime': log['logTime'],
                'action': log['action']
            })

        # 求和搜索参数
        params = [{'$group': {'_id': None, 'count': {'$sum': 1}}}]

        totalCount = list(
            DBOps.getAggregate(DBCollonfig.log, params)
        )[0]['count']

        res = {
            'page': page,
            'pageSize': pageSize,
            'totalCount': totalCount,
            'logs': resLogs
        }

        return res
