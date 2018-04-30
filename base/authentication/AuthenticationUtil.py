#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/4/30 下午11:24
# @Author   : cancan
# @File     : AuthenticationUtil.py
# @Function : 用户认证公共方法

from base.authentication.Authentication import Authentication


class AuthenticationUtil(object):
    """
        用户认证公共方法
    """

    @classmethod
    def verifyUser(cls, request):
        """
            用户认证
        """
        protocol = request.uri

        # 忽略token需求的请求
        white_list = ['register', 'login', 'checkLogin', 'registerInitData']

        if protocol.split('/')[2] in white_list:
            return True

        token = request.headers.get('Authorization', None)

        if token:
            res = Authentication.verifyToken(token)
            if res:
                return True
            else:
                return False
        else:
            return False

    @classmethod
    def getUserIdByToken(self, request):
        """
            根据token获得用户ID
        """
        token = request.headers.get('Authorization', None)
        setToken, header = Authentication.getVerifyToken(token)
        return setToken['userId']

