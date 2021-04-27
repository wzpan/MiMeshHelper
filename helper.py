from apscheduler.schedulers.blocking import BlockingScheduler
import MiWiFi
import yaml
import requests

CONFIG_PATH = './config.yml'

def reboot(config):
    """
    重启路由器
    """

    # 先重启子 mesh
    if 'slaves_deviceid' in config:
        for deviceid in config['slaves_deviceid']:        
            wifi1 = MiWiFi.MiWiFi()
            wifi1.login(deviceid, config['password'])
            reboot1 = wifi1.runAction('reboot?client=web')
            if reboot1['code'] == 0:
                notify('重启子 Mesh {} 指令已发送'.format(deviceid))
            else:
                notify('重启子 Mesh {} 失败！'.format(deviceid))

    # 再重启主路由
    wifi2 = MiWiFi.MiWiFi()
    wifi2.login(config['master_deviceid'], config['password'])
    reboot2 = wifi2.runAction('reboot?client=web')
    if reboot2['code'] == 0:
        notify('重启主路由指令已发送')
    else:
        notify('重启主路由失败！')

    
def switchMode(config, mode):
    """
    切换信号强度
    max: 穿墙
    mid: 标准
    min: 节能
    """

    wifi = MiWiFi.MiWiFi()
    wifi.login(config['master_deviceid'], config['password'])
    details = wifi.getNetworkAction('wifi_detail_all')
    if details['code'] != 0:
        notify('切换信号强度为 {} 失败！'.format(mode))
        return
    device_count = len(details['info'])
    data = {}
    for i in range(1, device_count+1):
        info = details['info'][i-1]
        data['bsd'] = details['bsd']
        data['on'+str(i)] = 1
        data['ssid'+str(i)] = info['ssid']
        data['encryption'+str(i)] = info['encryption']
        data['channel'+str(i)] = info['channel']
        data['bandwidth'+str(i)] = info['bandwidth']
        data['hidden'+str(i)] = info['hidden']
        data['txpwr'+str(i)] = mode
        data['pwd'+str(i)] = info['password']
    switch = wifi.postNetworkAction('set_all_wifi', data)
    if switch['code'] == 0:
        notify('切换信号强度为 {} 成功！'.format(mode))
    else:
        notify('切换信号强度为 {} 失败！'.format(mode))


def getConfig(config_path):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def rebootJob():
    notify("重启路由计划开始...")
    config = getConfig(CONFIG_PATH)
    reboot(config)

def switchToMax():
    notify("正在切换信号强度为穿墙强度...")
    config = getConfig(CONFIG_PATH)
    switchMode(config, 'max')

def switchToMin():
    notify("正在切换信号强度为节能强度...")
    config = getConfig(CONFIG_PATH)
    switchMode(config, 'min')

def notify(msg):
    config = getConfig(CONFIG_PATH)
    print(msg)
    if 'robot_key' not in config or config['robot_key'] == '':
        return
    url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=" + config['robot_key']
    params = {
        "msgtype": "text",
        "text": {
            "content": msg
        }
    }
    requests.post(url, json=params)

if __name__ == '__main__':
    notify("路由小助手启动")
    scheduler = BlockingScheduler()
    
    # 每周三晚上4点重启一次路由
    scheduler.add_job(rebootJob, 'cron', hour=4, day_of_week='wed')
    # 每晚 1 点调整为节能信号强度
    scheduler.add_job(switchToMin, 'cron', hour=1)
    # 每天凌晨 6 点调整为穿墙信号强度
    scheduler.add_job(switchToMax, 'cron', hour=6)

    scheduler.start()