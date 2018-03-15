#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/14 下午10:58
# @Author   : cancan
# @File     : Account.py
# @Function : 注册

from RequestAPI.BaseRequest import BaseRequest
from base.authentication.Authentication import Authentication
from base.db.DBOPS import DBOps
from base.encrypt.Encrypt import Encrypt
from config.DBCollConfig import DBCollonfig


class Register(BaseRequest):
    """
        注册
    """

    def handler_function(self):
        args = self.get_request_data()
        username = args.get('username', None)
        password = args.get('username', None)

        user = DBOps.getOneDoc(DBCollonfig.users, {'username': username})

        if user:
            return self.response_failure(username + u'用户已存在')

        self.createUser(username, password)
        self.response_success()

    def createUser(self, username, password):
        """
            创建账户
        """
        userNum = DBOps.getDocNum(DBCollonfig.users)

        userId =  DBCollonfig.startNum + userNum + 1

        item = {
            '_id': userId,
            'username': username,
            'password': Encrypt.password_encrypt(password),
            'level': 1,
            'type': 0
        }

        DBOps.insertDoc(DBCollonfig.users, item)

        self.result['result'] =  {
            'userObj': item,
            'token': Authentication.generateToken(userId)
        }


class Login(BaseRequest):
    """
        登录
    """

    def handler_function(self):
        args = self.get_request_data()

        username = args['username']
        password = args['password']

        user = DBOps.getOneDoc(DBCollonfig.users, {'username': username})

        if not user:
            return self.response_failure(username + u'用户不存在')

        if user['password'] != Encrypt.password_encrypt(password):
            return self.response_failure(username + u'用户密码错误')

        del user['password']
        self.result['result'] = {
            'userObj': user,
            'token': Authentication.generateToken(user['_id'])
        }
        return self.response_success()

class checkLogin(BaseRequest):
    """
        检测登录
    """

    def handler_function(self):
        args = self.get_request_data()
        token = args.get('token', None)

        if token:
            setToken, header = Authentication.getVerifyToken(token)
            if setToken.has_key('userId'):
                userId = setToken['userId']
                user = DBOps.getOneDoc(DBCollonfig.users, {'_id': userId})
                del user['password']
                self.result['result'] = {'userObj': user}
                return self.response_success()
            else:
                self.result['result'] = {'userObj': None}
                return self.response_failure('登录过期')
        else:
            self.result['result'] = {'userObj': None}
            return self.response_failure('没有登录')

