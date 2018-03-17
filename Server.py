#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/14 下午9:32
# @Author   : cancan
# @File     : Server.py
# @Function : 服务端

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornado.web import Application

from RequestAPI.RequestAPI import HandleList
from RequestAPI.RequestInit import RequestInit

define('PORT', default=9090, help='Server port')

if __name__ == '__main__':
    options.parse_command_line()

    print 'Server start listen ' + str(options.PORT)

    # 初始化基础模块
    RequestInit.init()

    http_server = HTTPServer(Application(HandleList))
    http_server.listen(options.PORT)
    IOLoop.instance().start()
