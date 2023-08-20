from redis import Redis
from os import environ


class UrlQueue:
    def __init__(self, host: str = "localhost", queue_id: str = "10001") -> None:
        host = "redis" if environ.get("DOCKER_ENV", False) else host
        self.redis_client = Redis(host=host)
        self.queue_name = f"url_queue:{queue_id}"

    def get(self):
        """Fetch a URL from queue"""
        return self.redis_client.rpop(self.queue_name)

    def push(self, url: str):
        """Push a URL from queue"""
        self.redis_client.lpush(self.queue_name, url)

    def is_queue_empty(self):
        """Check if URL queue is empty"""
        return self.redis_client.llen(self.queue_name) == 0

    def get_all_urls(self):
        return self.redis_client.lrange(self.queue_name, 0, -1)
