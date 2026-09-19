import asyncio
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from .email_extractor import extract_emails


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; PublicBusinessLeadFinder/1.0)"
    )
}

MAX_PAGES = 5


async def fetch_page(
    client: httpx.AsyncClient,
    url: str
) -> str | None:

    try:
        response = await client.get(
            url,
            headers=HEADERS,
            timeout=10,
            follow_redirects=True,
        )

        if response.status_code != 200:
            return None

        content_type = response.headers.get("content-type", "")

        if "text/html" not in content_type:
            return None

        return response.text

    except (httpx.HTTPError, asyncio.TimeoutError):
        return None


def find_contact_links(base_url: str, html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")

    base_domain = urlparse(base_url).netloc

    useful_words = (
        "contact",
        "about",
        "location",
        "team",
    )

    links = []

    for anchor in soup.find_all("a", href=True):

        href = anchor["href"]
        text = anchor.get_text(" ", strip=True).lower()

        if not any(word in text or word in href.lower()
                   for word in useful_words):
            continue

        absolute_url = urljoin(base_url, href)

        if urlparse(absolute_url).netloc != base_domain:
            continue

        if absolute_url not in links:
            links.append(absolute_url)

    return links[:MAX_PAGES - 1]


async def crawl_website(url: str) -> list[str]:

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    async with httpx.AsyncClient() as client:

        homepage = await fetch_page(client, url)

        if not homepage:
            return []

        emails = set(extract_emails(homepage))

        contact_links = find_contact_links(url, homepage)

        for link in contact_links:

            await asyncio.sleep(0.5)

            html = await fetch_page(client, link)

            if html:
                emails.update(extract_emails(html))

        return sorted(emails)
