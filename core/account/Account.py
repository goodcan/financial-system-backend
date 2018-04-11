#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/14 下午10:58
# @Author   : cancan
# @File     : Account.py
# @Function : 注册
from datetime import datetime

from RequestAPI.BaseRequest import BaseRequest
from base.authentication.Authentication import Authentication
from base.db.DBOps import DBOps
from base.encrypt.Encrypt import Encrypt
from config.DBCollConfig import DBCollonfig
from config.UserConfig import UserConfig
from base.db.LogDBOps import LogDBOps
from config.LogDBConfig import LogDBConfig


class EditUser(BaseRequest):
    """
        用户信息设置
    """

    def handler_function(self):
        args = self.get_request_data()

        newPermissions = {}
        for _ in UserConfig.permissions:
            if _ in args['setPermissions']:
                newPermissions[_] = 1
            else:
                newPermissions[_] = 0

        DBOps.setOneDoc(
            DBCollonfig.users,
            {'_id': args['_id']},
            {
                '$set': {
                    # 'department': args['department'],
                    'company': args['company'],
                    'tel': args['tel'],
                    'email': args['email'],
                    'qq': args['qq'],
                    'permissions': newPermissions
                }
            }
        )

        # 记录日志
        LogDBOps.writeLog(args['opsUserId'], LogDBConfig.doEditUser)

        args['permissions'] = newPermissions
        self.result['result'] = {
            'userObj': self.resUserData(args)
        }
        return self.response_success(msg=args['username'] + u'用户信息设置成功!')


class EditUserInitData(BaseRequest):
    """
        初始化用户编辑数据
    """

    def handler_function(self):
        args = self.get_request_data()

        userId = args['userId']

        user = DBOps.getOneDoc(
            DBCollonfig.users,
            {'_id': userId},
            {'orders': 0}
        )

        companies = DBOps.getOneDoc(
            DBCollonfig.options,
            {'_id': DBCollonfig.orderOption},
            {'companies': 1}
        )['companies']

        user['setPermissions'] = [
            k for k, v in user['permissions'].iteritems() if v == 1
        ]

        self.result['result'] = {
            'user': user,
            'companies': [
                {'label': _['name'], 'value': _['name']} for _ in companies
            ],
            'permissions': [
                {'key': k, 'label': v} for k, v in
                UserConfig.permissions.iteritems()
            ],
        }
        self.response_success()


class UserList(BaseRequest):
    """
        用户列表
    """

    def handler_function(self):
        total = DBOps.getSomeDoc(DBCollonfig.users, {}, {'orders': 0})

        userList = []
        for user in total:
            user.update({
                'userId': user['_id'],
                'pmsListName': [
                    UserConfig.permissions[k]
                    for k, v in user['permissions'].iteritems() if v == 1
                ]
            })
            userList.append(user)

        self.result['result'] = self.orderListByTime(userList, reverse=False)
        return self.response_success()


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
        key = args.get('registerKey', None)

        if key != 'szx2018':
            return self.response_failure(username + u'验证码错误')

        if password1 != password2:
            return self.response_failure(username + u'两次密码不一致')

        user = DBOps.getOneDoc(DBCollonfig.users, {'username': username})

        if user:
            return self.response_failure(username + u'用户已存在')

        userId = self.createUser(username, password1)

        # 记录日志
        LogDBOps.writeLog(userId, LogDBConfig.doRegister)
        LogDBOps.writeLog(userId, LogDBConfig.doLogin)

        self.response_success()

    def createUser(self, username, password):
        """
            创建账户
        """
        userNum = DBOps.getDocNum(DBCollonfig.users)

        userId = DBCollonfig.startNum + userNum + 1

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 初始化用户数据
        user = {
            '_id': userId,
            'username': username,
            'password': Encrypt.password_encrypt(password),
            'permissions': {_: 0 for _ in UserConfig.permissions},
            'createTime': now,
            'createTimeStamp': self.time_conversion(now, 1),
            'lastLogin': now,
            # 'department': '',
            'company': '',
            'tel': '',
            'email': '',
            'qq': ''
        }

        DBOps.insertDoc(DBCollonfig.users, user)

        self.result['result'] = {
            'userObj': self.resUserData(user),
            'token': Authentication.generateToken(userId)
        }

        return userId


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

        DBOps.setOneDoc(
            DBCollonfig.users,
            {'_id': user['_id']},
            {'$set': {
                'lastLogin': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}
        )

        self.result['result'] = {
            'userObj': self.resUserData(user),
            'token': Authentication.generateToken(user['_id'])
        }

        # 记录日志
        LogDBOps.writeLog(user['_id'], LogDBConfig.doLogin)

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

                DBOps.setOneDoc(
                    DBCollonfig.users,
                    {'_id': user['_id']},
                    {'$set': {'lastLogin': datetime.now().strftime(
                        '%Y-%m-%d %H:%M:%S')}}
                )

                self.result['result'] = {
                    'userObj': self.resUserData(user)
                }

                return self.response_success()
            else:
                self.result['result'] = {'userObj': None}
                return self.response_failure(u'登录过期')
        else:
            self.result['result'] = {'userObj': None}
            return self.response_failure(u'没有登录')
