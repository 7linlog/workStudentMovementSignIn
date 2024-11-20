import requests
import time
import json
import hashlib
from Crypto.Cipher import AES
from binascii import b2a_hex
import smtplib
from email.mime.text import MIMEText

def AES_encrypt(data):
    BLOCK_SIZE = 16  # Bytes
    secret_key = "23DbtQHR2UMbH6mJ"
    pad = lambda s: (s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE))
    cipher = AES.new(secret_key.encode(), AES.MODE_ECB)
    encrypted_text = cipher.encrypt(bytes(pad(str(data)), encoding='utf-8'))
    encrypted_text_hex = str(b2a_hex(encrypted_text), encoding='utf-8')
    return encrypted_text_hex


loginUrl = 'https://api.moguding.net:9000/session/user/v3/login'
saveUrl = "https://api.moguding.net:9000/attendence/clock/v2/save"


def getToken():
    data = {
        "password": AES_encrypt(""),  # 密码
        "t": AES_encrypt(int(time.time() * 1000)),
        "phone": AES_encrypt(""),  # 账号
        "loginType": "android",
        "uuid": ""
    }
    resp = postUrl(loginUrl, data=data, headers={'content-type': 'application/json; charset=UTF-8',
                                                 'User-Agent': 'Mozilla/5.0 (Linux; U; Android 10; zh-cn; MIX 3 Build/QKQ1.190828.002) '
                                                               'AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1',
                                                 })
    return resp['data']['token']


def postUrl(url, headers, data):
    # requests.packages.urllib3.disable_warnings()
    resp = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
    return resp.json()


def go():
    mail_host = "smtp.qq.com"  # 设置qq服务器
    mail_user = ""  # 发送人邮箱
    mail_pass = "nxpkpuuquwcjdied"  # 授权码
    sender = ''  # 发件人邮箱,注意和mail_user一致
    receivers = ['']  # 批量

    # 转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S"

    timeArray = time.localtime(int(time.time()))
    otherStyleTime = time.strftime("%H:%M:%S", timeArray)

    data = {
        "country": "中国",
        "address": "中国广西壮族自治区桂林市七星区穿山街道G357(七里店路)",  # 签到地址
        "province": "广西壮族自治区",  # 签到省份
        "city": "桂林市",  # 签到城市
        "description": "打卡下班",  # 签到文本
        "planId": "169dea675fba3b92187a5880ac99f4b2",  # 通过抓包获得
        "type": "START",  # START 上班 END 下班
        "device": "Android",
        "latitude": "25.24169878",  # 签到维度
        "longitude": "110.18619487",  # 签到经度
        "t": AES_encrypt(int(time.time() * 1000)),
    }
    text = data["device"] + data["type"] + data["planId"] + "104117995" + data["address"] + "3478cbbc33f84bd00d75d7dfa69e0daa"
    hl = hashlib.md5()
    hl.update(text.encode(encoding='utf8'))
    md5 = hl.hexdigest()
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Linux; U; Android 10; zh-cn; MIX 3 Build/QKQ1.190828.002) AppleWebKit/533.1 (KHTML, like Gecko) '
                      'Version/5.0 Mobile Safari/533.1',
        'roleKey': 'student',
        'Authorization': getToken(),
        'sign': md5,  # 填sign参数
    }
    resp = postUrl(saveUrl, headers, data)
    try:
        print(resp)
        message = MIMEText('工学云签到成功\n---{上班}', 'plain', 'utf-8')
        message['Subject'] = '今日签到'
        message['From'] = '工学云签到提示!'
        message['To'] = ','.join(receivers)
        smtpObj = smtplib.SMTP_SSL(mail_host)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        smtpObj.quit()
        print('success', otherStyleTime)
        time.sleep(10)
    except smtplib.SMTPException as e:
        print('error', e)
        time.sleep(10)


go()
