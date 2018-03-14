#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/14 下午10:26
# @Author   : cancan
# @File     : BaseRequest.py
# @Function : 基础请求

from tornado.web import RequestHandler
from tornado.escape import json_decode

from base.authentication.Authentication import Authentication


class BaseRequest(RequestHandler):
    """
        所有请求的基类
    """

    result = {'status': 0, 'msg': None, 'result': None}

    def post(self):
        verify = self.verifyUser()
        if not verify:
            self.response_failure()
        else:
            self.handler_function()
        return self.write(self.result)

    def verifyUser(self):
        """
            用户认证
        """
        protocol = self.request.uri

        # 忽略token需求的请求
        white_list = ['register', 'login']

        if protocol.split('/')[1] in white_list:
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

    def response_success(self, msg='success'):
        """
            响应成功
        """
        self.result['status'] = 1
        self.result['msg'] = msg

    def response_failure(self, msg='failure'):
        """
            响应成功
        """
        self.result['status'] = 0
        self.result['msg'] = msg
        self.result['result'] = None

    def get_request_data(self):
        """
            解析球球参数
        """
        return json_decode(self.request.body)

    def handler_function(self):
        """
            用于继承处理业务
        """
        pass