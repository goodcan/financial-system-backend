#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/4/5 下午4:04
# @Author   : cancan
# @File     : LogDBConfig.py
# @Function : 日志配置


class LogDBConfig:
    """
        日志配置
    """
    logListPageSize = 30

    doRegister = u'注册'
    doLogin = u'登录'
    doLogout = u'登出'

    doCreateOrder = u'创建订单'
    doCompleteOrder = u'申请付款'
    doPaymentOrder = u'完成付款'
    doEditOrder = u'修改订单'
    doDelOrder = u'删除订单'

    doCreateClass = u'新增类目'
    doDelClass = u'删除类目'

    doCreateCustomer = u'新增客户'
    doEditCustomer = u'修改客户信息'
    doDelCustomer = u'删除客户'

    doCreateContact = u'新增外包'
    doEditContact = u'修改外包信息'
    doDelContact = u'删除外包'

    doCreateDepartment = u'新增部门'
    doDelDepartment = u'删除部门'

    doCreateCompany = u'新增公司'
    doDelCompany = u'删除公司'

    doEditHelpInfo = u'修改帮助信息'

    doCreateWorkClass = u'新增外包技能'
    doDelWorkClass = u'删除外包技能'

    doEditUser = u'修改用户信息'
    doDelUser = u'删除用户'

    doLookSummaryOrder = u'查看订单汇总'
    doDownloadTable = u'下载汇总表'
