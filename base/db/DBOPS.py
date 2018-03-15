#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/14 下午10:23
# @Author   : cancan
# @File     : DBOps.py
# @Function : 数据操作

from base.db.DBManger import DBManager


class DBOps(object):
    """
        数据想过操作
    """

    usersDb = None

    @classmethod
    def init(cls):
        cls.usersDb = DBManager.usersDb

    @classmethod
    def insertDoc(cls, table, doc):
        """
            插入文档
        """

        getattr(cls, table + 'Db')[table].insert(doc)

    @classmethod
    def getDocNum(cls, table):
        """
            获得表总数
        """
        return getattr(cls, table + 'Db')[table].find().count()

    @classmethod
    def getOneDoc(cls, table, params):
        """
            获得一个文档
        """

        return getattr(cls, table + 'Db')[table].find_one(params)