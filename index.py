import calendar
import datetime
import hashlib
import random
import time

import requests
import json5
import json

url = "http://sxbaapp.zcj.jyt.henan.gov.cn/"

token = ""

# 读取user.json
def readJsonInfo():
    with open('user.json', "r", encoding='utf-8') as json_file:
        data = json5.load(json_file)
    json_file.close()
    return data


# 设置请求头
def getHeader():
    return {
        'os': 'android',
        'phone': 'Redmi|M2104K10AC|7.1.2',
        'appVersion': '38',
        'Host': 'sxbaapp.zcj.jyt.henan.gov.cn',
        'Connection': 'Keep-Alive',
        'cl_ip': '10.249.6.168',
        'Content-Type': 'application/json;charset=UTF-8',
        'User-Agent': 'okhttp/3.14.9',
        'Accept-Encoding': 'gzip'
    }


def da(userInfo):
    date = datetime.date.today()
    weekend = calendar.weekday(date.year, date.month, date.day)
    if weekend > 5:
        # 今天是周末
        if userInfo['weekend'] == 1:
            # 不打卡
            return
    uid = login(userInfo['token'])
    if uid == 'error':
        return
    location = userInfo['location']
    data = {
        'dtype': 1,
        'uid': uid,
        'address': location['address'],
        'phonetype': 'Redmi|M2104K10AC|7.1.2',
        'probability': 1,
        'longitude': location['longitude'],
        'latitude': location['latitude']
    }
    sign = str2md5(json.dumps(data, separators=(',', ':')) + token)
    headers = getHeader()
    headers['Sign'] = sign
    response = requests.post(url + 'interface/clockindaily20220827.ashx', data=json.dumps(data, separators=(',', ':')), headers=headers)
    if response.status_code == 200:
        json1 = json5.loads(response.text)
        print(json1)
        if json1['code'] == 1001:
            print(userInfo['token']['username'] + '打卡成功！')
        elif json1['code'] == 1003:
            print(json1['msg'])
        elif json1['code'] == 1002:
            print("已打卡")
    else:
        print("打卡请求失败！")


# 登录账号--获取账号的UID
def login(user):
    dToken = generate_random_str(36)
    data = {
        "phone": user['username'],
        "password": str2md5(user['password']),
        "dtype": 6,
        "dToken": dToken
    }
    sign = str2md5(json.dumps(data, separators=(',', ':')) + token)
    headers = getHeader()
    headers['Sign'] = sign
    response = requests.post(url + 'interface/relog.ashx', data=json.dumps(data, separators=(',', ':')), headers=headers)
    if response.status_code == 200:
        json1 = json5.loads(response.text)
        if json1['code'] == 1001:
            return json1['data']['uid']
        else:
            print("登录失败！" + json1['msg'])
            return 'error'
    else:
        print("登录请求失败！")


# 获取token
def getToken():
    global token
    response = requests.post(url + 'interface/token.ashx', headers=getHeader())
    if response.status_code == 200:
        json1 = json5.loads(response.text)
        if json1['code'] == 1001:
            token = json1['data']['token']
        else:
            print("获取token失败！" + json1['msg'])
    else:
        print("获取token请求发送失败")


# md5加密
def str2md5(string):
    return hashlib.md5(string.encode("utf-8")).hexdigest()

# 随机生成
def generate_random_str(lengths=36):
    random_str = ''
    base_str = '0123456789abcdefg'
    length = len(base_str) - 1
    for i in range(lengths):
        random_str += base_str[random.randint(0, length)]
    return random_str


# 入口
if __name__ == '__main__':
    # 读取账号
    users = readJsonInfo()
    getToken()
    # 循环遍历账号
    for user in users['user']:
        da(user)
        print("准备下个账号")
        time.sleep(1.5)
    print("没有账号了")
