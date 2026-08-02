from decouple import config
import redis
from redis.sentinel import Sentinel

from utils.general.singleton import Singleton

redis_host = config("REDIS_HOST", "")
redis_password = config("REDIS_PASSWORD", "")
redis_port = config("REDIS_PORT", "6379")
redis_service_name = config("REDIS_SERVICE_NAME", "master")
redis_mode = config("REDIS_MODE", "default")

redis_sentinel = Sentinel(
    [(redis_host, redis_port)], sentinel_kwargs={"password": redis_password}
)


class RedisHelper(metaclass=Singleton):
    redis_client = None

    def __connect(self):
        if redis_mode == "sentinel":
            self.redis_client = redis_sentinel.master_for(
                redis_service_name, password=redis_password
            )
        else:
            self.redis_client = redis.Redis(
                redis_host, port=redis_port, password=redis_password
            )

    def client(self):
        if not self.redis_client:
            self.__connect()
        return self.redis_client
