import sys
import aiosonic
from utils.exceptions import UnknownDownloaderType


class Downloader:
    pass


class AiosonicDownloader(Downloader):
    def __init__(self) -> None:
        super().__init__()

    async def get(self, **kwargs):
        """
         Fetches response from server using GET method

        Args:
         kwargs: url, headers, timeout parameters to fetch request

        Returns:
         response: server response object containing status code and text
        """
        url = kwargs.get("url")
        client = aiosonic.HTTPClient()
        response = await client.get(url)
        return response


def create_downloader(downloader_name=None):
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
