#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/3/15 11:40
# @Author   : cancan
# @File     : Encrypt.py
# @Function : 加密类
import base64
import json
from Crypto.Cipher import AES

from config.EncryptConfig import EncryptConfig


class Encrypt(object):
    """
        加密类
    """

    @classmethod
    def password_encrypt(cls, text):
        """
            密码的加密
        """
        password_key = EncryptConfig.password_key

        text = json.dumps(text)  # json格式转为str格式
        encrypted_text = cls.encrypt_aes(text, password_key, AES.MODE_CBC)  # 加密
        result = base64.b64encode(encrypted_text)  # base64编码

        return result

    @classmethod
    def encrypt_aes(cls, text, key, mode):
        """
            加密(AES)
        """
        iv = key  # 为了方便，直接使用protocol_key做为iv的值
        obj = AES.new(key, mode, iv)
        pad_it = lambda s: s + (16 - len(s) % 16) * '\0'

        result = obj.encrypt(pad_it(text))
        return result
