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

    db = None

    @classmethod
    def init(cls):
        cls.db = DBManager.db
        print 'DBOps init success'

    @classmethod
    def insertDoc(cls, table, doc):
        """
            插入文档
        """

        cls.db[table].insert(doc)

    @classmethod
    def removeDoc(cls, table, params):
        """
            插入文档
        """

        cls.db[table].remove(params)

    @classmethod
    def getDocNum(cls, table):
        """
            获得表总数
        """
        return cls.db[table].find().count()

    @classmethod
    def getOneDoc(cls, table, params, getParams=None):
        """
            获得一个文档
        """

        return cls.db[table].find_one(params, getParams)

    @classmethod
    def getSomeDoc(cls, table, params, getParams=None):
        """
            获得一些文档
        """

        return cls.db[table].find(params, getParams)

    @classmethod
    def setOneDoc(cls, table, params, setParams, multi=False):
        """
            获得一个文档
        """

        return cls.db[table].update(params, setParams, multi=multi)

    @classmethod
    def getAggregate(cls, table, params):
        """
            获得一个文档
        """

        return cls.db[table].aggregate(params)
