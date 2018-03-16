#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/14 下午11:10
# @Author   : cancan
# @File     : RequestInit.py
# @Function : 服务初始化

from base.db.DBManger import DBManager
from base.db.DBOps import DBOps


class RequestInit(object):
    """
        服务初始化
    """

    @classmethod
    def init(cls):
        DBManager.init()
        DBOps.init()
