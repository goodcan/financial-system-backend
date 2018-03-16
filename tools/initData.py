#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/16 11:15
# @Author   : cancan
# @File     : initData.py
# @Function : 清理数据结构

from base.db.DBManger import DBManager

DBManager.init()

db = DBManager.db

total = db['users'].find()

for each in total:
    del each['order']
    each.update({
        'orders': []
    })
    db['users'].update({'_id': each['_id']}, each)
