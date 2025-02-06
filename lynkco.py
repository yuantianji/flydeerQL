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


app_secret = 'OTc1NTY3NjUxNDg4RjUzQ0UzMTUxRERDN0I5QzJBNDBEOTQ0MzlBNEE2RjVENEI5NzA4N0UxRTJDMDIxQzE3NUU3Q0REQkQzNzhDMUVCNjQ5NjQ0MzFBODAwOEMwNjdF'
token = os.getenv("lc_cookie","")

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

def send_request(method, uri, x_ca_key, data=None):
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
    string_to_sign = f"{method}#*/*##application/json##X-Ca-Key:{x_ca_key}#X-Ca-Nonce:{x_ca_nonce}#X-Ca-Signature-Method:HmacSHA256#X-Ca-Timestamp:{x_ca_timestamp}#{uri}"

    # 使用HmacSHA256生成签名
    signature = hmac.new(app_secret.encode(), string_to_sign.encode(), hashlib.sha256).digest()
    signature_base64 = base64.b64encode(signature).decode()

    # 构造请求头
    headers = {
        "X-Ca-Key": x_ca_key,
        "X-Ca-Nonce": x_ca_nonce,
        "X-Ca-Timestamp": x_ca_timestamp,
        "X-Ca-Signature": signature_base64,
        "X-Ca-Signature-Method": "HmacSHA256",
        "X-Ca-Signature-Headers": "X-Ca-Key,X-Ca-Timestamp,X-Ca-Nonce,X-Ca-Signature-Method"
        "Content-Type": "application/json",
        "APPSECRET": app_secret,
        "Token": token
    }

    # 构造请求URL
    url = f"{uri}"  # 替换为实际的API域名

    # 发送请求
    if method.upper() == "POST":
        response = requests.post(url, headers=headers, json=data)
    elif method.upper() == "GET":
        response = requests.get(url, headers=headers)
    else:
        raise ValueError("Unsupported HTTP method")

    return response

def sign():
  response = send_request("https://h5-api.lynkco.com/up/api/v1/user/sign", "POST", "204644386")
  print("Response Status Code:", response.status_code)
  print("Response Content:", response.json())
  print("========================================")
  
def share():
  response = send_request("https://app-services.lynkco.com.cn/app/v1/task/getShareCode", "GET", "203760416")
  print("Response Status Code:", response.status_code)
  print("Response Content:", response.json())
  print("========================================") 
  
if __name__ == "__main__":
  share()
