'''
new Env('联通商店商品监听');
0 8 * * * UnicomStore.py 
'''

import requests
import time
from datetime import datetime
from sendNotify import pushplus_bot
import os

def send_requests_with_multiple_params(goodsIds):
    """
    发送HTTPS请求的函数，允许goodsId、cityCode和mode作为数组参数。
    
    :param goodsIds: 商品ID数组。
    :param cityCodes: 城市代码数组。
    :param modes: 模式参数数组。
    :return: 响应对象列表。
    """
    base_url = "https://card.10010.com/mall-order/qryStock/v2"
    responses = []  # 存储所有响应对象

    for goodsId in zip(goodsIds):
        params = {
            "goodsId": goodsId,
            "cityCode": "110",
            "mode": "1"
        }
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # 如果响应状态码不是200，将抛出异常
            responses.append(response)
        except requests.exceptions.HTTPError as errh:
            print(f"HTTP错误: {errh}")
        except requests.exceptions.ConnectionError as errc:
            print(f"连接错误: {errc}")
        except requests.exceptions.Timeout as errt:
            print(f"超时错误: {errt}")
        except requests.exceptions.RequestException as err:
            print(f"请求错误: {err}")

    return responses

# 使用示例
if __name__ == "__main__":
    while True:
        envdata = os.getenv("LT_ITEM","")
        if envdata:
            # 将字符串按逗号分割，并去除空白字符，然后转换成列表
            goodsIds = [item.strip() for item in envdata.split(",")]
        else:
            # 如果环境变量不存在，使用空列表
            goodsIds = []
        # goodsIds = ["994211139173","994210286035","994210179230","994210179233"]  # 商品ID数组
        current_time = datetime.now()
        if current_time.hour >= 23 and current_time.minute >= 30:
            break
        print("当前时间：", current_time.strftime("%Y-%m-%d %H:%M:%S"))
        responses = send_requests_with_multiple_params(goodsIds)
        notify = ""
        for i, response in enumerate(responses):
            if response:
                datas = response.json()
                if datas['data']['bareMetal']['modelsList'] is not None:
                    for data in datas['data']['bareMetal']['modelsList']:
                        if data['articleAmount'] == 0 & data['articleAmountNew'] == 0:
                            print(data['MODEL_DESC'] + ',当前库存为:0')
                        else:
                            if data['articleAmount'] > 1:
                                print(data['MODEL_DESC'] + ',当前库存为:' + str(data['articleAmount']))
                                notify += '{}-{}，当前库存为:{}   <a href="https://card.10010.com/terminal/hs?goodsId={}">点击购买</a>\n'.format(data['MODEL_DESC'], data.get('COLOR_DESC', ''), data['articleAmount'], goodsIds[i])
                                # pushplus_bot("联通商场有货通知", data['MODEL_DESC'] + ',当前库存为:' + str(data['articleAmount']))
                            elif data['articleAmountNew'] > 1:
                                print(data['MODEL_DESC']  + '-' + data['COLOR_DESC'] + ',当前库存为:' + str(data['articleAmountNew']))
                                notify += '{}-{}，当前库存为:{}   <a href="https://card.10010.com/terminal/hs?goodsId={}">点击购买</a>\n'.format(data['MODEL_DESC'], data.get('COLOR_DESC', ''), data['articleAmountNew'], goodsIds[i])
                                # pushplus_bot("联通商场有货通知", data['MODEL_DESC'] + ',当前库存为:' + str(data['articleAmountNew']))
                            else:
                                print(data['MODEL_DESC'] + ',当前库存为:' + str(data['articleAmount']))
        
        if notify:
            pushplus_bot("联通商场有货通知", notify)
        print('================================================================================')
        time.sleep(120)  # 等待120秒（2分钟）后再次执行
