#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/16 11:15
# @Author   : cancan
# @File     : initData.py
# @Function : 清理数据结构

from base.db.DBManger import DBManager


def clearUserData():
    DBManager.init()

    db = DBManager.db

    total = db['users'].find()

    for each in total:
        del each['order']
        each.update({
            'orders': []
        })
        db['users'].update({'_id': each['_id']}, each)


def moveUserOrders():
    DBManager.init()

    db = DBManager.db

    total = db['users'].find()

    for each in total:
        for order in each['orders']:
            order.update({'_id': order['orderId']})
            db['orders'].insert(order)


def removeUserOrders():
    DBManager.init()

    db = DBManager.db

    total = db['users'].find()

    for each in total:
        del each['orders']
        db['users'].update({'_id': each['_id']}, each)


def addOrderTitile():
    DBManager.init()

    db = DBManager.db

    orders = db['orders'].find()

    i = 1
    for order in orders:
        db['orders'].update(
            {'_id': order['_id']},
            {'$set': {'title': 'test' + str(i)}}
        )
        i += 1

if __name__ == "__main__":
    addOrderTitile()
