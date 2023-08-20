from json import loads
from typing import List
from crawl_executor.utils.http import Request
from crawl_executor.utils.url_queue import UrlQueue
from crawl_executor.utils.parser import parser_classes
from crawl_executor.utils.logging_config import get_logger
from crawl_executor.utils.downloader import create_downloader

logger = get_logger()


async def get_response(queue_id: str):
    downloader = create_downloader(downloader_name="AiosonicDownloader")
    url_queue = UrlQueue(queue_id=queue_id)
    if not url_queue.is_queue_empty():
        url_as_string = url_queue.get()
        request_object = Request.deserialize(url_as_string)
        response = await downloader.download(request_object)
        logger.info(f"Downloaded response for {request_object.url}")
        return response
    return None


def push_urls(requests: List[Request], queue_id: str = "1000"):
    """
    Pushes URLs to queue

    Args:
     urls: List of URLs to be pushed ot queue
     queue_id: ID of the queue to which the URLs are pushed
    """
    url_queue = UrlQueue(queue_id=queue_id)
    for request in requests:
        deserialized_request = request.serialize()
        url_queue.push(deserialized_request)
    logger.info("Finished pushing urls to queue")


def get_all_urls(queue_id: str = "1000"):
    """
    Fetches all URLs from redis queue

    Args:
     queue_id: ID of the queue from which URLs are fetched
    """
    url_queue = UrlQueue(queue_id=queue_id)
    requests_as_string = url_queue.get_all_urls()
    urls = [loads(request)["url"] for request in requests_as_string]
    return urls


def parse_response(response_text: str, parser_type: str = "amazon"):
    """Parse response and return data

    Args:
     response_text: response text for data to be extracted
     parser_type: indicates the site for which parser object is created

    Returns:
     data: Parsed response for a specific site
    """
    if not parser_classes.get(parser_type):
        raise Exception(f"Parser for {parser_type} does not exist")
    parser = parser_classes[parser_type]()
    data = parser.get_product_data(response_text=response_text)
    return data


def is_valid_response(response):
    """Validates response

    Args:
     response: Response object which has status and text attributes

    Returns:
     boolean: Indicating whether the response is valid or not
    """
    status_code = str(response.status)
    if status_code.startswith(("2", "3")) and len(response.text) > 10000:
        # 2xx, 3xx responses
        return True
    if status_code == "404":
        return True
    return False


def retry_request(request_object: Request, queue_id: str):
    """Retries request

    Args:
     request_object: request to be retried
     queue_id: id of the url queue to which request is being put to be retried

    Returns:
     boolean: True if request is retried else False
    """
    if request_object.retry_count > request_object.max_retry_count:
        return False
    request_object.retry_count += 1
    # Puts back request to queue to be retried
    push_urls(requests=[request_object], queue_id=queue_id)
    return True
