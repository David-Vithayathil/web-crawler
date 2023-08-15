class CustomException(Exception):
    name = "Custom Exception"

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class UndefinedLogHandler(CustomException):
    name = "Handler for this logger is undefined"


class UnknownDownloaderType(CustomException):
    name = "Failed to create downloader as downloader does not exist"
