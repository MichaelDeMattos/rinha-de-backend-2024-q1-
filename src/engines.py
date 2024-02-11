# -*- coding: utf-8 -*-

import redis.asyncio as redis

redis_pool = redis.ConnectionPool.from_url('redis://:@127.0.0.1:6379/0')
redis_pool.max_connections = 1000
redis_client = redis.Redis.from_pool(redis_pool)
