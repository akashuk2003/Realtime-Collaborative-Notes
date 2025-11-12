import redis
from django.conf import settings
import time

redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0, decode_responses=True)

#used for allowing lock and release for multi-user eidting
def acquire_lock(key, ttl=5):
    res = redis_client.set(name=key, value=1, nx=True, ex=ttl)
    return bool(res)

def release_lock(key):
    redis_client.delete(key)

#real-time "who is typing indicator"
def set_typing(note_id, user_id, ttl=3):
    key = f"note:{note_id}:typing:{user_id}"
    redis_client.set(key, 1, ex=ttl)

def get_typing_users(note_id):
    pattern = f"note:{note_id}:typing:*"
    keys = redis_client.keys(pattern)
    user_ids = [k.split(':')[-1] for k in keys]
    return user_ids
