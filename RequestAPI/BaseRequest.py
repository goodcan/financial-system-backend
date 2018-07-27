#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/14 下午10:26
# @Author   : cancan
# @File     : BaseRequest.py
# @Function : 基础请求
from tornado.web import RequestHandler
from tornado.escape import json_decode

from base.authentication.AuthenticationUtil import AuthenticationUtil


class BaseRequest(RequestHandler):
    """
        所有请求的基类
    """

    result = {'code': 0, 'msg': None, 'result': None}

    def get(self):
        self.handler_download()

    def post(self):
        verify = AuthenticationUtil.verifyUser(self.request)
        if not verify:
            self.response_failure()
            self.result['code'] = 1001
        else:
            self.handler_function()
        return self.write(self.result)

    def on_finish(self):
        """
            清理全局变量
        """
        self.result['code'] = 0
        self.result['msg'] = None
        self.result['result'] = None

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
