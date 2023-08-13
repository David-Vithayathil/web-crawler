import aiosonic


class Downloader:
    pass


class AiosonicDownloader(Downloader):
    def __init__(self) -> None:
        super().__init__()

    async def get(self, **kwargs):
        url = kwargs.get("url")
        client = aiosonic.HTTPClient()
        response = await client.get(url)
        return response


def create_downloader(downloader_name=None):
    if not downloader_name:
        raise Exception("Downloader Name not mentioned")

    downloader_mapping = {"aiosonic": AiosonicDownloader()}
    return downloader_mapping[downloader_name]
