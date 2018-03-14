#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/14 下午10:58
# @Author   : cancan
# @File     : Register.py
# @Function : 注册

from RequestAPI.BaseRequest import BaseRequest


class Register(BaseRequest):
    """
        注册
    """

    def handler_function(self):
        args = self.get_request_data()

        print args['username'], args['password']

        self.response_success()
