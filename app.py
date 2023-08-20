from uuid import uuid4
from pydantic import BaseModel
from urllib.parse import urlparse
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from crawl_executor.utils.logging_config import get_logger
from crawl_executor.utils.http import Request as HttpRequest
from crawl_executor.crawler import (
    push_urls,
    get_all_urls,
    get_response,
    parse_response,
    is_valid_response,
    retry_request,
)


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
logger = get_logger()


class CrawlerInput(BaseModel):
    urls: list
    crawlerDomain: str
    maxRetryCount: int


@app.get("/api/v1/home", response_class=HTMLResponse)
def get_crawl_details(request: Request):
    """Home page that accepts request urls and other attributes"""

    return templates.TemplateResponse("home.html", {"request": request})


@app.post("/api/v1/urls/")
async def execute_crawl(CrawlerInput: CrawlerInput):
    """PUT API to push input urls to URL queue"""

    try:
        crawler_id = str(uuid4())
        urls = CrawlerInput.urls
        domain = CrawlerInput.crawlerDomain.lower()
        are_urls_valid, validation_message = validate_urls(urls, domain)
        if not are_urls_valid:
            return {"status": 503, "crawler_id": None, "message": validation_message}
        max_retry_count = CrawlerInput.maxRetryCount
        requests = [HttpRequest(url, max_retry_count=max_retry_count) for url in urls]
        push_urls(requests=requests, queue_id=crawler_id)
        logger.info("Pushed urls to queue")
        return {"status": 200, "crawler_id": crawler_id}
    except Exception as err:
        logger.error(f"Error log message {err}")
        return {"status": 200, "crawler_id": crawler_id}


@app.get("/api/v1/urls/")
def get_crawl_details(crawler_id: str = Query(default=1000, description="Crawler ID")):
    """GET API to fetch URLs from URL queue"""

    urls = get_all_urls(queue_id=crawler_id)
    return {"status": 200, "urls": urls}


@app.get("/api/v1/crawl/", response_class=HTMLResponse)
def initiate_crawl(
    request: Request, crawler_id: str = Query(default=1000, description="Crawler ID")
):
    """GET API that renders crawler page"""

    return templates.TemplateResponse(
        "crawl.html", {"crawler_id": crawler_id, "request": request}
    )


@app.get("/api/v1/download/")
async def get_crawl_details(
    crawler_id: str = Query(default=1000, description="Crawler ID")
):
    """GET API that downloads a request, parses response and returns data"""

    response = await get_response(queue_id=crawler_id)
    if not response:
        # No more requests in queue
        return {"status": 200, "parsed_data": None, "has_finished": True}

    if not is_valid_response(response=response):
        request_object = response.request
        if retry_request(request_object, crawler_id):
            return {
                "status": 403,
                "is_blocked": True,
                "url": request_object.url,
                "is_retrying": True,
                "has_finished": False,
            }
        return {
            "status": 403,
            "is_blocked": True,
            "url": request_object.url,
            "is_retrying": False,
            "has_finished": False,
        }

    info = parse_response(response.text, parser_type="amazon")
    info["url"] = response.request.url
    return {"status": 200, "parsed_data": info, "has_finished": False}


def validate_urls(urls, domain):
    """Validates if urls belong to the particular domain
    TODO: Add validation for type of page too, product/search/category page etc

    Args:
     urls: list of urls to be validated,
     domain: domain of the url

    Returns:
     boolean: True if all urls are of the intended domain else returns False
    """
    for url in urls:
        parsed_url = urlparse(url)
        if domain not in parsed_url.netloc.lower():
            return False, "Invalid Url. Url does not belong to selected domain"
        # TODO: Handle this for domains other than amazon too.
        if domain == "amazon" and "/dp/" not in parsed_url.path.lower():
            return False, "Invalid Url. Not a product page"
    return True, "Success"
