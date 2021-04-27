#!/usr/bin/env python
#coding=utf-8
#-*- coding: utf-8 -*-

# 小米路由器远程管理 API

import random
import math
import time
import hashlib
import json
import re
import requests

class MiWiFi(object):
    """
    docstring for MiWiFi
    """
    def __init__(self):
        super(MiWiFi, self).__init__()

        self.deviceId = None
        self.type = '0'
        self.nonce = None
        self.password = None
        self.stok = None
        self.key = None
        self.cookies = None

        # 小米路由器首页
        self.URL_ROOT = "http://miwifi.com"
        # 小米路由器登录页面
        self.URL_LOGIN = "%s/cgi-bin/luci/api/xqsystem/login" % self.URL_ROOT
        # 小米路由器当前设备清单页面，登录后取得 stok 值才能完成拼接
        self.URL_ACTION = None
        self.URL_DeviceListDaemon = None        
    
    def getKey(self):
        if self.key is None:
            homeRequest = requests.get('%s/cgi-bin/luci/web/home' % self.URL_ROOT)
            key = re.findall(r'key: \'(.*)\',', homeRequest.text)[0]
            self.key = key
        return self.key

    def nonceCreat(self, miwifi_deviceId):
        """
        docstring for nonceCreat()
        模仿小米路由器的登录页面，计算 hash 所需的 nonce 值
        """
        self.deviceId = miwifi_deviceId
        miwifi_type = self.type
        miwifi_time = str(int(math.floor(time.time())))
        miwifi_random = str(int(math.floor(random.random() * 10000)))
        self.nonce = '_'.join([miwifi_type, miwifi_deviceId, miwifi_time, miwifi_random])

        return self.nonce

    def oldPwd(self, password):
        """
        docstring for oldPwd()
        模仿小米路由器的登录页面，计算密码的 hash
        """
        self.password = hashlib.sha1((self.nonce + hashlib.sha1((password + self.getKey()).encode('utf-8')).hexdigest()).encode('utf-8')).hexdigest()

        return self.password

    def login(self, deviceId, password):
        """
        docstring for login()
        登录小米路由器，并取得对应的 cookie 和用于拼接 URL 所需的 stok
        """
        nonce = self.nonceCreat(deviceId)
        password = self.oldPwd(password)
        payload = {'username': 'admin', 'logtype': '2', 'password': password, 'nonce': nonce}
        # print(payload)
 
        try:
            r = requests.post(self.URL_LOGIN, data = payload)            
            # print(r.text)
            stok = json.loads(r.text).get('url').split('=')[1].split('/')[0]
        except Exception as e:
            raise e

        self.stok = stok
        self.cookies = r.cookies
        self.URL_ACTION =  "%s/cgi-bin/luci/;stok=%s/api" % (self.URL_ROOT, self.stok)
        self.URL_DeviceListDaemon = "%s/xqsystem/device_list" % self.URL_ACTION
        return stok, r.cookies

    def listDevice(self):
        """
        docstring for listDevice()
        列出小米路由器上当前的设备清单
        """
        if self.URL_DeviceListDaemon != None and self.cookies != None:
            try:
                r = requests.get(self.URL_DeviceListDaemon, cookies = self.cookies)
                # print(json.dumps(json.loads(r.text), indent=4))
                return json.loads(r.text).get('list')
            except Exception as e:
                raise e
                return None
        else:
            raise e
            return None

    def getNetworkAction(self, action):
        """
        docstring for getAction()
        run a custom network action with GET method
        """
        if self.URL_DeviceListDaemon != None and self.cookies != None:
            try:
                r = requests.get('%s/xqnetwork/%s' % (self.URL_ACTION, action), cookies = self.cookies)
                return json.loads(r.text)
            except Exception as e:
                raise e
                return None
        else:
            raise e
            return None

    def postNetworkAction(self, action, data):
        """
        docstring for postAction()
        run a custom action with POST method
        """
        if self.URL_DeviceListDaemon != None and self.cookies != None:
            try:
                r = requests.get('%s/xqnetwork/%s' % (self.URL_ACTION, action), cookies = self.cookies, params=data)
                # print(r.text)
                return json.loads(r.text)
            except Exception as e:
                raise e
                return None
        else:
            raise e
            return None

    def runAction(self, action):
        """
        docstring for runAction()
        run a custom action like "pppoe_status", "pppoe_stop", "pppoe_start" ...
        """
        if self.URL_DeviceListDaemon != None and self.cookies != None:
            try:
                r = requests.get('%s/xqsystem/%s' % (self.URL_ACTION, action), cookies = self.cookies)
                # print(r.text)
                return json.loads(r.text)
            except Exception as e:
                raise e
                return None
        else:
            raise e
            return None

