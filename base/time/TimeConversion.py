#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/4/30 下午5:19
# @Author   : cancan
# @File     : TimeConversion.py
# @Function : 时间处理

import time


class TimeConversion(object):
    """
        时间处理类
    """

    @classmethod
    def time_conversion(cls, obj, option):
        """
            时间类型转换
        :param option:
            1.字符转转时间戳
            2.时间戳转字符串
        """

        # 字符转转时间戳
        if option == 1:
            return int(
                time.mktime(time.strptime(obj, '%Y-%m-%d %H:%M:%S')) * 1000)

        # 时间戳转字符串
        elif option == 2:
            return time.strftime('%Y-%m-%d %H:%M:%S',
                                 time.localtime(obj * 0.001))
