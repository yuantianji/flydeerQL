'''
new Env('领克APP每日任务');
0 8 * * * lynkco.py 
'''

import random
import hmac
import hashlib
import base64
import time
import requests
import os
from sendNotify import wecom_key

app_secret = 'QCl7udM3PB9cOIOwquwPglikFQnzJRsX'
token = os.getenv("lc_token","")
refreshToken = os.getenv("lc_refreshToken","")

def generate_x_ca_nonce():
    """
    生成符合要求的 X-Ca-Nonce 字符串
    """
    template = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"
    nonce = ""

    for char in template:
        if char == 'x':
            # 随机生成一个16进制数字（0-15）
            nonce += f"{random.randint(0, 15):x}"
        elif char == 'y':
            # 随机生成一个16进制数字，范围为8到B（即8、9、A、B）
            nonce += f"{random.randint(8, 11):x}"
        else:
            nonce += char

    return nonce

def send_request(uri, method, x_ca_key, data=None, headers_data=None):
    """
    发送HTTP请求函数

    :param method: 请求方法（如POST、GET等）
    :param uri: 请求路径
    :param x_ca_key: X-Ca-Key
    :param data: 请求正文（可选，默认为None）
    :return: HTTP响应对象
    """
    # 生成X-Ca-Nonce
    x_ca_nonce = generate_x_ca_nonce()
    # 生成X-Ca-Timestamp
    x_ca_timestamp = str(int(time.time() * 1000))
    # 构造签名字符串
    string_to_sign = (
        f"{method}\n"
        f"*/*\n\n"
        f"application/json\n\n"
        f"X-Ca-Key:{x_ca_key}\n"
        f"X-Ca-Nonce:{x_ca_nonce}\n"
        f"X-Ca-Signature-Method:HmacSHA256\n"
        f"X-Ca-Timestamp:{x_ca_timestamp}\n"
        f"{uri}"
    )
    # 使用HmacSHA256生成签名
    signature = hmac.new(app_secret.encode(), string_to_sign.encode(), hashlib.sha256).digest()
    signature_base64 = base64.b64encode(signature).decode()
    # 构造请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 x-cordova-platform/ios cordova-6",
        "X-Ca-Key": x_ca_key,
        "X-Ca-Nonce": x_ca_nonce,
        "X-Ca-Timestamp": x_ca_timestamp,
        "X-Ca-Signature": signature_base64,
        "X-Ca-Signature-Method": "HmacSHA256",
        "X-Ca-Signature-Headers": "X-Ca-Key,X-Ca-Timestamp,X-Ca-Nonce,X-Ca-Signature-Method",
        "Content-Type": "application/json",
        "token": token
    }
    if headers_data != None:
        headers[headers_data['head']] = headers_data['data']

    # 构造请求URL
    url = f"https://h5-api.lynkco.com{uri}"  # 替换为实际的API域名

    # 发送请求
    try:
        if method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method.upper() == "GET":
            if data != None:
                response = requests.get(f"{url}?{data}", headers=headers)
            else:
                response = requests.get(url, headers=headers)
        else:
            raise ValueError("Unsupported HTTP method")

        # 打印响应状态码和内容
        if response.status_code != 200:
            print("Response Status Code:", response.status_code)
            print("Response Headers:", response.headers)
            print("Response Content:", response.text)

        # 尝试解析JSON
        try:
            response_json = response.json()
            print("Response JSON:", response_json)
            return response_json
        except ValueError as e:
            print("Response is not JSON:", e)

    except requests.exceptions.RequestException as e:
        print("Request failed:", e)

    return None

def send_request2(uri, method, data=None):
    """
    发送HTTP请求函数

    :param uri: 请求路径
    :param method: 请求方法（如POST、GET等）
    :param data: 请求正文（可选，默认为None）
    :return: HTTP响应对象
    """
    # 构造请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1 Edg/128.0.0.0",
        "Content-Type": "application/json"
    }

    # 构造请求URL
    url = f"https://h5.lynkco.com{uri}"  # 替换为实际的API域名

    # 发送请求
    try:
        if method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method.upper() == "GET":
            response = requests.get(url, headers=headers)
        else:
            raise ValueError("Unsupported HTTP method")

        # 打印响应状态码和内容
        if response.status_code != 200:
            print("Response Status Code:", response.status_code)
            print("Response Headers:", response.headers)
            print("Response Content:", response.text)

        # 尝试解析JSON
        try:
            response_json = response.json()
            print("Response JSON:", response_json)
            return response_json
        except ValueError as e:
            print("Response is not JSON:", e)

    except requests.exceptions.RequestException as e:
        print("Request failed:", e)

    return None

notify = "========================================\n"

def sign():
  response = send_request("/up/api/v1/user/sign", "POST", "204644386")
  global notify
  notify = notify + "签到:" + response['message'] + '\n'
  print("========================================")
  
def share():
  response = send_request("/app/v1/task/getShareCode", "GET", "204644386",None,{"head":"risk_request_info","data":'{"openTimeStamp":"2025-02-07 15:29:24","shareContentType":1,"shareContentURL":"https://h5.lynkco.com/app-h5/dist/web/pages/exploration/article/index.html?id=1881101031748870144"}'})
  shareCode = response['data']
  print("========================================") 
  shareReporting(shareCode)
  
def shareReporting(shareCode):
  response = send_request2(f"/app/v1/task/shareReporting?shareCode={shareCode}", "POST", {"businessNo":"1881101031748870144","eventData":{"firstClassification":"文章","secondClassification":""}})
  global notify
  notify = notify + "分享:" + response['data'] + '\n'
  print("========================================") 

def refreshToken():
  response = send_request(f"/auth/login/refresh?deviceId&deviceType=Web&refreshToken={refreshToken}", "GET", "204644386")
  print("========================================") 

def getPointBalance():
  response = send_request("/app/energy/myEnergy", "GET", "204644386")
  global notify
  notify = notify + "Co积分:" + response['data']['point'] + '\n' + "过期Co积分:" + response['data']['expirePoint'] + '\n' + "能量体:" + str(response['data']['incomePoint']) + '\n'
  print("========================================")

if __name__ == "__main__":
  sign()
  time.sleep(1)
  share()
  time.sleep(1)
  getPointBalance()
  if notify:
      wecom_key("领克日常任务",notify)
