import asyncio
from utils.downloader import create_downloader
from utils.url_queue import UrlQueue


async def run():
    url_queue = UrlQueue()
    push_urls(url_queue)
    await get_response(url_queue)


async def get_response(url_queue):
    downloader = create_downloader(downloader_name="aiosonic")
    while not url_queue.is_queue_empty():
        url = url_queue.get()
        response = await downloader.get(url=url.decode("utf-8"))
        print("response", response.status_code, sep=" || ")


def push_urls(url_queue):
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
    print("Finished pushing urls to queue.... ")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
