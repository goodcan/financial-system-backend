#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/4/30 下午11:17
# @Author   : cancan
# @File     : OrderUtil.py
# @Function : 订单功能方法


class OrderUtil(object):
    """
        订单功能方法
    """

    @classmethod
    def orderListByTime(cls, data, reverse=True):
        """
            生成返回数据
        """
        return sorted(
            data,
            key=lambda x: x['createTimeStamp'],
            reverse=reverse
        )