from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/api/v1/amazon/product", response_class=HTMLResponse)
def read_item(request: Request):
    return templates.TemplateResponse("crawl.html", {"request": request})
