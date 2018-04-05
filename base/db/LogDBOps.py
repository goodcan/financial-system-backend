#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/4/5 下午3:44
# @Author   : cancan
# @File     : LogDBOps.py
# @Function : 日志数据库操作
import time
from datetime import datetime

from config.DBCollConfig import DBCollonfig
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
