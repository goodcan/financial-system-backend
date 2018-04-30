#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/4/30 下午10:59
# @Author   : cancan
# @File     : AccountUtil.py
# @Function : 用户公共方法类


class AccountUtil(object):
    """
        用户公共方法类
    """

    @classmethod
    def resUserData(cls, user):
        """
            返回前端的信息
        """
        res = {
            'userId': user['_id'],
            'username': user['username'],
            'permissions': user['permissions'],
            'company': user['company'],
            'tel': user['tel'],
            'navCollapse': user.get('navCollapse', None)
        }
        return res
