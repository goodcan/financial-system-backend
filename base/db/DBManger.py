#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/14 下午9:59
# @Author   : cancan
# @File     : DBManger.py
# @Function : 数据库连接

from pymongo import MongoClient


class DBManager(object):
    """
        数据库管理
    """
    HOST = '127.0.0.1'
    PORT = 27017
    db = None

    @classmethod
    def init(cls):
        """
            数据库初始化
        """

        username = 'admin'
        password = 'szx0982'

        cls.db = cls.connect_db(username, password)

        print 'connect db success'

    @classmethod
    def connect_db(cls, username, password):
        """
            连接数据库
        """
        client = MongoClient(cls.HOST, cls.PORT)

        dbAuth = client.szx_admin
        dbAuth.authenticate(username, password)

        return client.szx_admin

if __name__ == "__main__":
    DBManager.init()