import pickle
import redis
# import os

from utils.singleton import singleton

# 创建 Redis 客户端
# os.environ['ENV'] = 'dev'


@singleton
class RedisClientClass:
    redis_client: redis.Redis
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379)
        return

    def del_key_from_redis(self, key):
        return self.redis_client.delete(key)

    # 传入的数据、对象、序列化后存入redis
    def set_data_to_redis(self, key, data):
        binary_data = pickle.dumps(data)
        self.redis_client.set(key, binary_data)

    def set_data_to_redis_expire(self, key, data, expire_time_seconds):
        binary_data = pickle.dumps(data)
        expire = expire_time_seconds
        self.redis_client.setex(key, expire, binary_data)

    def get_data_from_redis(self, key):
        # 从 Redis 中获取数据
        binary_data = self.redis_client.get(key)

        if binary_data:
            # 数据存在于 Redis 中
            restored_data = pickle.loads(binary_data)
            return restored_data
        else:
            # 数据不存在或已过期，重新查询并存储到 Redis
            return None


# 创建实例
redis_client_cls = RedisClientClass()


# DEMO

# from utils.singleton import singleton
# import uuid

# from service.db.postgres_engine import post_db
# from service.db.redshift_engine import red_db

# from service.text2data.redis_client import redis_client_cls
# import time

# @singleton
# class AnswerCacheClass:
#     db: dict
#     def __init__(self):
#         self.post_db = post_db
#         self.red_db = red_db
#         self.db = {
#             'redshift': self.red_db,
#             'report': self.post_db
#         }
#         return

#     def get_answer_from_answer_id(self, answer_id):
#         key = f"answer_id:{answer_id}"
#         restored_dict = redis_client_cls.get_dataset_from_redis(key)
#         if restored_dict is not None:
#             print('=======get_dataset_from_redis=====', restored_dict)
#             return restored_dict
#         else:
#             raise Exception('answer_id not found in redis')

#     def set_answer_to_redis_expire(self, answer, expire_time_seconds = 3600 * 24) -> str:
#         answer_id = str(uuid.uuid4())
#         key = f"answer_id:{answer_id}"
#         redis_client_cls.set_dataset_to_redis_expire(key, answer, expire_time_seconds)
#         return answer_id

#     def set_answer_to_redis(self, answer) -> str:
#         answer_id = str(uuid.uuid4())
#         key = f"answer_id:{answer_id}"
#         redis_client_cls.set_dataset_to_redis(key, answer)
#         return answer_id

# # 创建实例
# answer_cache_cls = AnswerCacheClass()

