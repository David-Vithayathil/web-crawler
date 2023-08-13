from redis import Redis


class UrlQueue:
    def __init__(self, host="localhost", queue_name="url_queue") -> None:
        self.redis_client = Redis(host=host)
        self.queue_name = queue_name

    def get(self):
        return self.redis_client.rpop(self.queue_name)

    def push(self, url):
        self.redis_client.lpush(self.queue_name, url)

    def is_queue_empty(self):
        return self.redis_client.llen(self.queue_name) == 0
