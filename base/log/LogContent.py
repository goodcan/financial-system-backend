#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/4/5 下午6:51
# @Author   : cancan
# @File     : LogContent.py
# @Function : 日志信息

from RequestAPI.BaseRequest import BaseRequest
from base.db.LogDBOps import LogDBOps


class LogList(BaseRequest):
    """
        日志信息
    """

    def handler_function(self):
        args = self.get_request_data()

        page = args['page']
        pageSize = args['pageSize']
        logType = args['logType']

        self.result['result'] = LogDBOps.getlist(page, pageSize, logType)

        self.response_success()
