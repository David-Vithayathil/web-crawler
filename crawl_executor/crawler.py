import asyncio
from utils.downloader import create_downloader
from utils.url_queue import UrlQueue
from utils.logging_config import get_logger

logger = get_logger()

async def run():
    """
     Pushes URLs to queue and fetches response for each URL
    """

    url_queue = UrlQueue()
    logger.info("Created URL queue")
    push_urls(url_queue)
    await get_response(url_queue)


async def get_response(url_queue):
    """
     Creates downloader and downloads response for each URL from URL queue

    Args:
     url_queue: Queue from which URLs are fetched
    """
    downloader = create_downloader(downloader_name="AiosonicDownloader")
    while not url_queue.is_queue_empty():
        url = url_queue.get()
        response = await downloader.get(url=url.decode("utf-8"))
        logger.info(f"Downloaded response for {url}")


def push_urls(url_queue):
    """
     Pushes URLs to queue
    
     Args:
      url_queue: Queue to which URLs are being pushed
    """
    urls = [
        "http://www.example.com?get=1",
        "http://www.example.com?get=2",
        "http://www.example.com?get=3",
        "http://www.example.com?get=4",
        "http://www.example.com?get=5",
        "http://www.example.com?get=6",
    ]
    for url in urls:
        url_queue.push(url)
    logger.info("Finished pushing urls to queue")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
