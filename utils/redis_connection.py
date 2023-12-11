from aioredis import Redis, from_url

redis: Redis = None

redis = from_url("redis://localhost:6379")