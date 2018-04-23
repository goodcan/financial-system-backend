#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/14 下午10:26
# @Author   : cancan
# @File     : BaseRequest.py
# @Function : 基础请求
import time
from tornado.web import RequestHandler
from tornado.escape import json_decode

from base.authentication.Authentication import Authentication


class BaseRequest(RequestHandler):
    """
        所有请求的基类
    """

    result = {'code': 0, 'msg': None, 'result': None}

    def get(self):
        self.handler_download()

    def post(self):
        verify = self.verifyUser()
        if not verify:
            self.response_failure()
            self.result['code'] = 1001
        else:
            self.handler_function()
        return self.write(self.result)

    def handler_function(self):
        """
            用于继承处理业务
        """
        pass

    def handler_download(self):
        """
            处理下载
        """
        pass

    def verifyUser(self):
        """
            用户认证
        """
        protocol = self.request.uri

        # 忽略token需求的请求
        white_list = ['register', 'login', 'checkLogin', 'registerInitData']

        if protocol.split('/')[2] in white_list:
            return True

        token = self.request.headers.get('Authorization', None)

        if token:
            res = Authentication.verifyToken(token)
            if res:
                return True
            else:
                return False
        else:
            return False

    def getUserIdByToken(self):
        """
            根据token获得用户ID
        """
        token = self.request.headers.get('Authorization', None)
        setToken, header = Authentication.getVerifyToken(token)
        return setToken['userId']

    def response_success(self, msg='success'):
        """
            响应成功
        """
        self.result['code'] = 1
        self.result['msg'] = msg

    def response_failure(self, msg='failure'):
        """
            响应成功
        """
        self.result['code'] = 0
        self.result['msg'] = msg
        self.result['result'] = None

    def get_request_data(self):
        """
            解析球球参数
        """
        return json_decode(self.request.body)

    def time_conversion(self, obj, option):
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

    def orderListByTime(self, data, reverse=True):
        """
            生成返回数据
        """
        return sorted(
            data,
            key=lambda x: x['createTimeStamp'],
            reverse=reverse
        )

    def resUserData(self, user):
        """
            返回前端的信息
        """
        res = {
            'userId': user['_id'],
            'username': user['username'],
            'permissions': user['permissions'],
            # 'department': user['department'],
            'company': user['company'],
            'tel': user['tel'],
            'navCollapse': user.get('navCollapse', None)
        }
        return res
