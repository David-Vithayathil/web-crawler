import json
from copy import deepcopy
from urllib.parse import urlparse
from user_agent import generate_user_agent


class Request:
    def __init__(self, url: str = None, **kwargs):
        self.url = url
        self.method = kwargs.get("method", "GET")
        self.headers = self.get_headers(custom_headers=kwargs.get("headers"))
        self.proxy = kwargs.get("proxy")
        self.meta = kwargs.get("meta", {})
        self.cookies = kwargs.get("cookies", {})
        self.retry_count = 0
        self.max_retry_count = kwargs.get("max_retry_count", 3)
        self.serializable_keys = [
            "url",
            "method",
            "headers",
            "proxy",
            "cookies",
            "retry_count",
            "meta",
            "max_retry_count",
        ]
        self.__dict__.update(kwargs)

    def get_domain(self):
        """Returns domain of the url being hit

        This is to ensure that www.amazon.com/amazon.uk/amazon.in all relates to amazon
        TODO: Could add something like fuzzy mapping here and avoid multiple if conditions.

        Returns:
         domain: domain of the url being requested.
        """
        parsed_domain = urlparse(self.url).netloc
        if "amazon" in parsed_domain:
            return "amazon"
        if "walmart" in parsed_domain:
            return "walmart"

        # Default
        return parsed_domain

    def serialize(self):
        """Returns request class as json string"""
        data = {key: getattr(self, key) for key in self.serializable_keys}
        return json.dumps(data)

    @classmethod
    def deserialize(cls, json_string):
        """Returns request class object using json string

        Args:
         json_data: Json object containing url, method and other attributes
        """
        data = json.loads(json_string)
        return cls(**data)

    def get_headers(self, custom_headers=None):
        """"""
        user_agent = generate_user_agent()
        domain = self.get_domain()
        headers = getattr(self, f"{domain}_headers", self.default_headers)()
        if custom_headers:
            headers.update(custom_headers)
        headers["user-agent"] = user_agent
        return headers

    def amazon_headers(self):
        """Returns headers for amazon"""

        headers = {
            "authority": "www.amazon.com",
            "cache-control": "max-age=0",
            "rtt": "50",
            "downlink": "10",
            "ect": "4g",
            "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            "sec-ch-ua-mobile": "?0",
            "upgrade-insecure-requests": "1",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
            "*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "sec-fetch-site": "none",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        }
        return headers

    def default_headers(self):
        """Returns headers for default website"""
        headers = {
            "accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
            ),
            "accept-language": "en-US,en;q=0.5",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
        }
        return headers

    @classmethod
    def aiosonic_attributes(cls):
        attributes = ["url", "headers"]
        return attributes


class Response:
    def __init__(self, text: str, status: int, **kwargs):
        self.text = text
        self.status = status
        self.__dict__.update(kwargs)

    @property
    def meta(self):
        """returns request meta"""
        meta = getattr(self.request, "meta", None)
        if meta:
            return deepcopy(meta)
        return None
