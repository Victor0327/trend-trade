from utils.singleton import singleton
import requests
import json
import os
from functools import wraps

# 发布前注释掉
# os.environ['ENV'] = 'dev'

user_id_map = {
  'ShengLi': 'ShengLi',
}

def retry_on_http_400(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        max_retries = 1
        retries = 0
        while retries <= max_retries:
            response = func(self, *args, **kwargs)
            if response.status_code != 400 and (response.status_code == 200 and response.json()['errcode'] != 40014):
                return response
            if retries < max_retries:
                if self.refresh_token is None:
                   raise Exception('refresh_token function is not exist')
                self.refresh_token()
            retries += 1
        return response
    return wrapper


@singleton
class QyWeixin:

  agent_id: str
  corp_id: str
  agent_secret: str

  def __init__(self):
    self.agent_id = 3010041
    self.corp_id = 'ww83d59dd61f8e0827'
    self.agent_secret = 'JP-2V6xJi0FMQBdvI2g92CNIMSO0Cfdpo7_Qirwhmck'
    self.token = self.get_token()

  def get_token(self):
    url = f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.corp_id}&corpsecret={self.agent_secret}'
    headers = {'content-type': 'application/json; charset=utf-8'}
    token = requests.get(url, headers=headers).json()['access_token']
    return token

  def refresh_token(self):
    self.token = self.get_token()

  @retry_on_http_400
  def send_message(self, message, user_id='ShengLi'):
    url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.token}"

    req = {
      "touser": user_id_map[user_id],
      "msgtype": "text",
      "agentid": self.agent_id,
      "text": {
        "content": message
      },
      "safe": 0,
      "enable_id_trans": 0,
      "enable_duplicate_check": 0
    }
    print(req)
    payload = json.dumps(req)
    # headers = {
    #     'Authorization': 'Bearer {}'.format(self.token), # your access token
    #     'Content-Type': 'application/json'
    # }
    response = requests.request("POST", url, data=payload)
    print(response.content)
    return response

# 创建实例
qy_weixin = QyWeixin()