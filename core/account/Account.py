#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/14 下午10:58
# @Author   : cancan
# @File     : Account.py
# @Function : 注册

from RequestAPI.BaseRequest import BaseRequest
from base.authentication.Authentication import Authentication
from base.db.DBOps import DBOps
from base.encrypt.Encrypt import Encrypt
from config.DBCollConfig import DBCollonfig
from config.UserConfig import UserConfig


class RegisterIinitData(BaseRequest):
    """
        注册数据初始化
    """

    def handler_function(self):
        departments = DBOps.getOneDoc(
            DBCollonfig.options,
            {'_id': DBCollonfig.orderOption},
            {'departments': 1}
        )['departments']

        self.result['result'] = {
            'departments': [
                {'label': _['name'], 'value': _['name']} for _ in departments
            ]
        }

        return self.response_success()


class Register(BaseRequest):
    """
        注册
    """

    def handler_function(self):
        args = self.get_request_data()
        username = args.get('username', None)
        password1 = args.get('password1', None)
        password2 = args.get('password2', None)
        userType = args.get('userType', None)

        if password1 != password2:
            return self.response_failure(username + u'两次密码不一致')

        user = DBOps.getOneDoc(DBCollonfig.users, {'username': username})

        if user:
            return self.response_failure(username + u'用户已存在')

        self.createUser(username, password1, userType)
        self.response_success()

    def createUser(self, username, password, userType):
        """
            创建账户
        """
        userNum = DBOps.getDocNum(DBCollonfig.users)

        userId = DBCollonfig.startNum + userNum + 1

        # 初始化用户数据
        user = {
            '_id': userId,
            'username': username,
            'password': Encrypt.password_encrypt(password),
            'permissions': UserConfig.permissions,
            'userType': userType,
            'orders': []
        }

        DBOps.insertDoc(DBCollonfig.users, user)

        self.result['result'] = {
            'userObj': {
                'userId': user['_id'],
                'username': user['username'],
                'permissions': user['permissions'],
                'userType': user['userType']
            },
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

        self.result['result'] = {
            'userObj': {
                'userId': user['_id'],
                'username': user['username'],
                'permissions': user['permissions'],
                'userType': user['userType']
            },
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
                self.result['result'] = {
                    'userObj': {
                        'userId': user['_id'],
                        'username': user['username'],
                        'permissions': user['permissions'],
                        'userType': user['userType']
                    }
                }
                return self.response_success()
            else:
                self.result['result'] = {'userObj': None}
                return self.response_failure(u'登录过期')
        else:
            self.result['result'] = {'userObj': None}
            return self.response_failure(u'没有登录')
