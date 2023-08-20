import sys
import json
import aiosonic
from crawl_executor.utils.http import Request, Response
from crawl_executor.utils.exceptions import UnknownDownloaderType


class Downloader:
    async def get(self, request_object: Request, **kwargs):
        raise NotImplementedError

    async def post(self, request_object: Request, **kwargs):
        raise NotImplementedError

    async def process_response(self, response):
        raise NotImplementedError


class AiosonicDownloader(Downloader):
    def __init__(self) -> None:
        super().__init__()
        self.client = aiosonic.HTTPClient()

    async def download(self, request_object: Request, **kwargs):
        """
        Calls corresponding aiosonic request method and returns response

        Args:
         request_object: Object of request class with url, headers etc as attributes

        Returns:
         response: response object with status code and text
        """
        serialized_request = request_object.serialize()
        request_args = json.loads(serialized_request)
        request_method = request_args["method"].lower()
        download_coroutine = getattr(self, request_method)
        modified_args = {
            key: request_args[key] for key in Request.aiosonic_attributes()
        }
        response = await download_coroutine(**modified_args)
        response_object = await self.process_response(response)
        response_object.request = request_object
        return response_object

    async def get(self, **kwargs):
        """
        Fetches response from server using GET method

        Args:
         kwargs: headers, url parameters to fetch request

        Returns:
         response: aiosonic response object
        """
        response = await self.client.get(**kwargs)
        return response

    async def process_response(self, response):
        """
        Processes the downloaders response object and returns http Response class object

        Args:
         response: Response object of the downloader class
        """
        text = await response.text()
        status_code = response.status_code
        return Response(text=text, status=status_code)


def create_downloader(downloader_name: str):
    """
    Creates and returns downloader object used for downloading response

    Args:
     downloader_name: name of the type of downloader to be created

    Returns:
     downloader: Downloader object used to download response

    Raises:
     ValueError: Error is raised if downloader name is not mentioned
     UnknownDownloaderType: Error is raised if an undefined downloader is requested
    """
    if not downloader_name:
        raise ValueError("Downloader name is required")

    try:
        downloader = getattr(sys.modules[__name__], downloader_name)()
        return downloader
    except AttributeError:
        raise UnknownDownloaderType()
