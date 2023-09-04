from utils.singleton import singleton
from requests_toolbelt import MultipartEncoder
import requests
import json
import os
from functools import wraps

# 发布前注释掉
# os.environ['ENV'] = 'dev'

# 我的user_id
# 68246782

chat_id_map = {
  'test': 'oc_1c4f83dec7cad937aec8a95b9e72edac',
  'APP 日报群': 'oc_a981c3d82d9b6e96483f02a3261a5cf5',
  'refund': 'oc_c741a0cbdd6542380fd99603c64763f2',
  'supply': 'oc_6f2d34eb70333708a754476574710a32',
  'APP 核心': 'oc_87816fdac9a7c40bf73726e798af287c',
  '广州供应链Team': 'oc_b88ef9cd4776e15ad2e1e94ad3528603',
  '运维技术支持群': 'oc_23d7d56df15f9d0e7e2a474582b2011b',
  '品类运营': 'oc_75ccbae1631d6a32e8fab0baf89de990',
  '机器人监控告警群': 'oc_806d08756ffbaba89f096a6478dd9f6c'
}

def retry_on_http_400(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        max_retries = 1
        retries = 0
        while retries <= max_retries:
            response = func(self, *args, **kwargs)
            if response.status_code != 400:
                return response
            if retries < max_retries:
                if self.refresh_token is None:
                   raise Exception('refresh_token function is not exist')
                self.refresh_token()
            retries += 1
        return response
    return wrapper


class Feishu:

  app_id: str
  app_secret: str

  def __init__(self):
    self.app_id = self.app_id
    self.app_secret = self.app_secret
    self.token = self.get_token()

  def reset_group_name_when_test(self, group_name):
    if os.getenv('ENV') == 'dev':
       return 'test'
    else:
       return group_name

  def get_token(self):
    # 调用机器人的地址 如有更改 可查看飞书文档
    # 2小时有效期，如果过期需要更新
    url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
    headers = {'content-type': 'application/json; charset=utf-8'}
    data = {'app_id': self.app_id,
            'app_secret': self.app_secret}
    token = requests.post(url, headers=headers, json=data).json()['tenant_access_token']
    print(token)
    return token

  def refresh_token(self):
    self.token = self.get_token()

  def upload_image(self, path):
    url = 'https://open.feishu.cn/open-apis/im/v1/images'
    headers = {'Authorization': 'Bearer {}'.format(self.token)}
    # print(headers)
    # path 图片路径
    with open(path, 'rb')as f:
        image = f.read()
    files = {
        "image": image
    }
    data = {
        "image_type": "message"
    }
    resp = requests.post(url, headers=headers, files=files, data=data).json()
    print('=======upload_feishu_image=======', resp)
    img_key = resp['data']['image_key']
    print(img_key)
    return img_key


  def upload_file(self, path, file_name):
    url = "https://open.feishu.cn/open-apis/im/v1/files"
    form = {'file_type': 'stream',
            'file_name': file_name,
            'file':  (file_name, open(path, 'rb'), 'application/x-tar')} # 需要替换具体的path  具体的格式参考  https://www.w3school.com.cn/media/media_mimeref.asp
    multi_form = MultipartEncoder(form)
    headers = {
        'Authorization': 'Bearer {}'.format(self.token)
    }
    headers['Content-Type'] = multi_form.content_type
    file_key = requests.request("POST", url, headers=headers, data=multi_form).json()['data']['file_key']
    return file_key

  @retry_on_http_400
  def send_card(self, card, receive_id, receive_id_type='chat_id'):
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    params = {"receive_id_type":receive_id_type}
    req = {
        "receive_id": receive_id, # chat id
        # "receive_id": self.prod_chat_id, # chat id
        "content": card,
        "msg_type": "interactive",
    }
    print(req)
    payload = json.dumps(req)
    headers = {
        'Authorization': 'Bearer {}'.format(self.token), # your access token
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, params=params, headers=headers, data=payload)
    print(response.content)
    return response

  @retry_on_http_400
  def send_message(self, message, receive_id, receive_id_type='chat_id'):
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    params = {"receive_id_type":receive_id_type}
    req = {
        "receive_id": receive_id, # chat id
        # "receive_id": self.prod_chat_id, # chat id
        "content": json.dumps({"text": message}),
        "msg_type": "text",
    }
    print(req)
    payload = json.dumps(req)
    headers = {
        'Authorization': 'Bearer {}'.format(self.token), # your access token
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, params=params, headers=headers, data=payload)
    print(response.content)
    return response

  @retry_on_http_400
  def send_img(self, img_key, receive_id, receive_id_type='user_id'):
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    params = {"receive_id_type": receive_id_type}
    req = {
        "receive_id": receive_id, # chat id
        # "receive_id": self.prod_chat_id, # chat id
        "content": "{\"image_key\":\""+img_key+"\"}",
        "msg_type": "image",
    }
    payload = json.dumps(req)
    headers = {
        'Authorization': 'Bearer {}'.format(self.token), # your access token
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, params=params, headers=headers, data=payload)
    print(response.content)
    return response

  @retry_on_http_400
  def _send_img_to_group(self, img_key, group_name):
    group_name = self.reset_group_name_when_test(group_name)
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    params = {"receive_id_type":"chat_id"}
    req = {
        "receive_id": chat_id_map[group_name], # chat id
        # "receive_id": self.prod_chat_id, # chat id
        "content": "{\"image_key\":\""+img_key+"\"}",
        "msg_type": "image",
    }
    payload = json.dumps(req)
    headers = {
        'Authorization': 'Bearer {}'.format(self.token), # your access token
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, params=params, headers=headers, data=payload)
    print(response.content)
    return response


  @retry_on_http_400
  def send_img_to_group(self, img_key, group_name = ('APP 日报群', 'APP 核心')):
    group_name = self.reset_group_name_when_test(group_name)
    if isinstance(group_name,str):
        self._send_img_to_group(img_key, group_name)
    elif isinstance(group_name,tuple):
        for group_name_i in group_name:
            self._send_img_to_group(img_key, group_name_i)

  @retry_on_http_400
  def _send_file(self, file_key, group_name = ('APP 日报群', 'APP 核心')):
    group_name = self.reset_group_name_when_test(group_name)
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    params = {"receive_id_type":"chat_id"}
    req = {
        "receive_id": chat_id_map[group_name], # chat id
        # "receive_id": self.prod_chat_id, # chat id
        "content": "{\"file_key\":\""+file_key+"\"}",
        "msg_type": "file",
    }
    payload = json.dumps(req)
    headers = {
        'Authorization': 'Bearer {}'.format(self.token), # your access token
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, params=params, headers=headers, data=payload)
    print(response.content) # Print Response
    return response

  @retry_on_http_400
  def send_file(self, file_key, receive_id, receive_id_type='user_id'):
      url = "https://open.feishu.cn/open-apis/im/v1/messages"
      params = {"receive_id_type": receive_id_type}
      req = {
          "receive_id": receive_id, # chat id
          # "receive_id": self.prod_chat_id, # chat id
          "content": "{\"file_key\":\""+file_key+"\"}",
          "msg_type": "file",
      }
      payload = json.dumps(req)
      headers = {
          'Authorization': 'Bearer {}'.format(self.token), # your access token
          'Content-Type': 'application/json'
      }
      response = requests.request("POST", url, params=params, headers=headers, data=payload)
      print(response.content) # Print Response
      return response

  def send_file_to_group(self, img_key, group_name = ('APP 日报群', 'APP 核心')):
    group_name = self.reset_group_name_when_test(group_name)
    if isinstance(group_name,str):
        self._send_file(img_key, group_name)
    elif isinstance(group_name,tuple):
        for group_name_i in group_name:
            self._send_file(img_key, group_name_i)

  @retry_on_http_400
  def get_ou(self):
    url = 'https://open.feishu.cn/open-apis/im/v1/chats'
    headers = {'Authorization': 'Bearer {}'.format(self.token)}
    response = requests.get(url, headers=headers).json()
    print(response)
    return response


  @retry_on_http_400
  def api_forward(self, url, payload, headers, method):
    default_headers = {'Authorization': 'Bearer {}'.format(self.token)}
    headers = {**default_headers, **headers}
    response = requests.request(method, url, headers=headers, data=payload)
    print(response.content)
    return response

  def get_group_chat_id(self, group_name):
     return chat_id_map[group_name]

  def urgent_app(self, msg_id, user_id_type='user_id'):
    url = f"https://open.feishu.cn/open-apis/im/v1/messages/{msg_id}/urgent_app?user_id_type={user_id_type}"
    req = {
        "user_id_list": [
           "68246782",
           "15gdf2bg",
           "d5979g91",
           "c3f15gcd",
        ]
    }
    payload = json.dumps(req)
    headers = {
        'Authorization': 'Bearer {}'.format(self.token), # your access token
        'Content-Type': 'application/json'
    }
    response = requests.request("PATCH", url, headers=headers, data=payload)
    print(response.content) # Print Response
    return response

# Feishu().get_ou()

@singleton
class DataFeishu(Feishu):
   def __init__(self):
    self.app_id = 'cli_a40c40d00778900b'
    self.app_secret = 'EMaO4jXIsULAn8EPyBCo4ejfyNTagOMl'
    super().__init__()

@singleton
class AlertFeishu(Feishu):
   def __init__(self):
    self.app_id = 'cli_a43e0ee76b19d00d'
    self.app_secret = 'ium9U2CUkG0vnC1G1uuOvP5AqDjMIi0a'
    super().__init__()

# 创建实例
feishu = DataFeishu()
alert_feishu = AlertFeishu()

# alert_feishu.get_ou()
