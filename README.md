# MiMeshHelper - 小米 Mesh 助手

一个帮助小米 Mesh 路由实现定时重启和定时调整信号强度的工具，支持多个子路由，支持通过企业微信群机器人发送执行结果。

理论上也能用于其他小米路由器，但我没测试过。

## 依赖安装

``` bash
pip3 install -r requirements.txt
```

## 配置

详见 config.yml 。其中，企业微信群机器人秘钥可参考 [这篇教程](https://jingyan.baidu.com/article/d45ad148cc79eb28552b80b5.html) 获取。

> 小技巧：可以偷偷拉两个人搞个小群，然后把他们踢了，留下只有你一个人的群，再添加这个机器人。这样就可以拥有一个不会打扰到别人的你的专属群机器人。

## 运行

``` bash
python3 helper.py
```

## 调整定时重启和定时调整信号强度的时间

自行 [helper.py](https://github.com/wzpan/MiMeshHelper/blob/main/helper.py#L107) 中的代码调整规则即可。小助手使用 apscheduler 来实现定时任务，详见 [apscheduler.triggers.cron](https://apscheduler.readthedocs.io/en/stable/modules/triggers/cron.html) 。

## 感谢

登录路由的代码基于 [pyMiWiFi](https://github.com/sbilly/pyMiWiFi) 实现。