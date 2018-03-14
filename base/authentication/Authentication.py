#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/14 下午10:28
# @Author   : cancan
# @File     : Authentication.py
# @Function : 用户认证相关

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class Authentication(object):
    """
        用户认证类
    """

    token_secret_key = 'CANCANGOOD'
    token_expiration = 60 * 60 * 24

    @classmethod
    def generateToken(cls, userId):
        """
            生成token
        """

        setToken = {'userId': userId}

        # 生成他token
        s = Serializer(cls.token_secret_key,cls.token_expiration)
        token = s.dumps(setToken)

        return token

    @classmethod
    def verifyToken(cls, token):
        """
            token验证
        """

        s = Serializer(cls.token_secret_key)
        setToken, header = s.loads(token, return_header=True)

        # token验证
        # TODO 后续后续添加时间认证
        if setToken.has_key('userId'):
            return True
        else:
            return False