from fastapi import FastAPI
from pydantic import BaseModel

from crawler.website import crawl_website


app = FastAPI(
    title="Public Lead Finder",
    version="0.1.0",
)


class CrawlRequest(BaseModel):
    website: str


@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "Public Lead Finder API is running"
    }


@app.post("/crawl")
async def crawl(request: CrawlRequest):

    emails = await crawl_website(request.website)

    return {
        "website": request.website,
        "emails": emails,
        "count": len(emails),
    }
