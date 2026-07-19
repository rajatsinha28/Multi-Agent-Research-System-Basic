"""
tools.py

Utility tools used by the Multi-Agent Research System.

This module provides:

1. Web Search
2. URL Scraping
3. Source Formatting
4. URL Cleaning
5. Utility Helpers
"""

from __future__ import annotations

import os
import re
import requests

from bs4 import BeautifulSoup
from dotenv import load_dotenv

from langchain.tools import tool
from tavily import TavilyClient

# ==========================================================
# ENVIRONMENT
# ==========================================================

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError(
        "TAVILY_API_KEY not found in .env"
    )

tavily = TavilyClient(
    api_key=TAVILY_API_KEY
)

# ==========================================================
# CONSTANTS
# ==========================================================

DEFAULT_HEADERS = {

    "User-Agent":
        (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/136.0 Safari/537.36"
        ),

    "Accept-Language":
        "en-US,en;q=0.9",

}

MAX_RESULTS = 5

MAX_CONTENT_LENGTH = 5000

# ==========================================================
# URL CLEANING
# ==========================================================


def clean_url(url: str) -> str:
    """
    Remove tracking parameters and
    trailing slashes.
    """

    if not url:
        return ""

    url = url.split("?")[0]

    url = url.rstrip("/")

    return url


def remove_duplicate_sources(results):

    seen = set()

    cleaned = []

    for item in results:

        url = clean_url(
            item.get("url", "")
        )

        if not url:
            continue

        if url in seen:
            continue

        seen.add(url)

        item["url"] = url

        cleaned.append(item)

    return cleaned


# ==========================================================
# SEARCH TOOL
# ==========================================================


@tool
def web_search(
    query: str,
) -> str:
    """
    Search the web using Tavily.

    Returns the top research sources
    with title, URL and summary.
    """

    try:

        response = tavily.search(

            query=query,

            max_results=MAX_RESULTS,

            search_depth="advanced",

            include_answer=True,

            include_raw_content=True,

            include_images=False,

        )

        results = response.get(
            "results",
            [],
        )

        results = remove_duplicate_sources(
            results
        )

        if not results:

            return (
                "No relevant search "
                "results were found."
            )

        output = []

        if response.get("answer"):

            output.append(
                "SEARCH SUMMARY\n"
            )

            output.append(
                response["answer"]
            )

            output.append(
                "\n"
            )

        output.append(
            "=" * 60
        )

        output.append(
            "TOP SOURCES"
        )

        output.append(
            "=" * 60
        )

        for index, result in enumerate(
            results,
            start=1,
        ):

            title = result.get(
                "title",
                "Unknown Title",
            )

            url = result.get(
                "url",
                "",
            )

            snippet = result.get(
                "content",
                "",
            )[:600]

            output.append(

                f"""
SOURCE {index}

Title:
{title}

URL:
{url}

Summary:
{snippet}

{'-' * 60}
"""

            )

        return "\n".join(output)

    except Exception as e:

        return (
            "Web Search Error:\n"
            f"{str(e)}"
        )

# ==========================================================
# PAGE CLEANING
# ==========================================================


def clean_page_text(
    soup: BeautifulSoup,
) -> str:
    """
    Remove unwanted HTML.
    """

    for tag in soup(

        [
            "script",
            "style",
            "noscript",
            "footer",
            "header",
            "nav",
            "aside",
            "svg",
            "form",
        ]

    ):

        tag.decompose()

    text = soup.get_text(
        separator=" ",
        strip=True,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text
# ==========================================================
# URL SCRAPER
# ==========================================================


@tool
def scrape_url(url: str) -> str:
    """
    Scrape a webpage and return cleaned content.

    Returns:
        - Page title
        - URL
        - Main extracted text
    """

    try:

        response = requests.get(
            clean_url(url),
            headers=DEFAULT_HEADERS,
            timeout=15,
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        title = ""

        if soup.title:

            title = soup.title.get_text(
                strip=True
            )

        content = clean_page_text(soup)

        if len(content) > MAX_CONTENT_LENGTH:

            content = (
                content[:MAX_CONTENT_LENGTH]
                + "\n\n[Content Truncated]"
            )

        return f"""
============================================================
PAGE TITLE
============================================================

{title}

============================================================
URL
============================================================

{url}

============================================================
CONTENT
============================================================

{content}
"""

    except Exception as e:

        return (
            f"Failed to scrape {url}\n\n"
            f"Reason: {e}"
        )


# ==========================================================
# MULTI PAGE SCRAPER
# ==========================================================


def scrape_multiple_urls(
    urls: list[str],
) -> list[dict]:
    """
    Scrape multiple URLs.

    Returns:

    [
        {
            "url": "...",
            "content": "...",
            "success": True
        }
    ]
    """

    pages = []

    visited = set()

    for url in urls:

        url = clean_url(url)

        if not url:

            continue

        if url in visited:

            continue

        visited.add(url)

        content = scrape_url.invoke(url)

        pages.append(
            {
                "url": url,
                "content": content,
                "success": not content.startswith(
                    "Failed"
                ),
            }
        )

    return pages


# ==========================================================
# SOURCE EXTRACTION
# ==========================================================


def extract_urls(
    search_output: str,
) -> list[str]:
    """
    Extract every URL from the search tool output.
    """

    pattern = r"https?://[^\s]+"

    urls = re.findall(
        pattern,
        search_output,
    )

    cleaned = []

    seen = set()

    for url in urls:

        url = clean_url(url)

        if url in seen:

            continue

        seen.add(url)

        cleaned.append(url)

    return cleaned


# ==========================================================
# SOURCE FORMATTER
# ==========================================================


def format_sources(
    urls: list[str],
) -> str:
    """
    Create a numbered bibliography.
    """

    if not urls:

        return "No sources."

    lines = []

    for i, url in enumerate(
        urls,
        start=1,
    ):

        lines.append(
            f"[{i}] {url}"
        )

    return "\n".join(lines)


# ==========================================================
# DOMAIN EXTRACTION
# ==========================================================


def extract_domains(
    urls: list[str],
) -> list[str]:

    domains = []

    seen = set()

    for url in urls:

        try:

            domain = (
                url.replace(
                    "https://",
                    "",
                )
                .replace(
                    "http://",
                    "",
                )
                .split("/")[0]
            )

            if domain in seen:

                continue

            seen.add(domain)

            domains.append(domain)

        except Exception:

            continue

    return domains


# ==========================================================
# RESEARCH STATISTICS
# ==========================================================


def research_statistics(
    urls: list[str],
    pages: list[dict],
) -> dict:

    successful = sum(
        page["success"]
        for page in pages
    )

    total_words = 0

    for page in pages:

        total_words += len(
            page["content"].split()
        )

    return {

        "sources_found": len(urls),

        "pages_scraped": successful,

        "domains": extract_domains(
            urls
        ),

        "word_count": total_words,

    }


# ==========================================================
# RESEARCH MERGER
# ==========================================================


def merge_research(
    pages: list[dict],
) -> str:
    """
    Merge all scraped pages into one document.
    """

    sections = []

    for i, page in enumerate(
        pages,
        start=1,
    ):

        if not page["success"]:

            continue

        sections.append(
            f"""
============================================================
SOURCE {i}
============================================================

{page["content"]}
"""
        )

    return "\n".join(sections)


# ==========================================================
# PUBLIC HELPER
# ==========================================================


def collect_research(
    search_output: str,
) -> dict:
    """
    High-level helper.

    Used by pipeline.py.

    Returns:

    {
        "urls": [...],
        "pages": [...],
        "research": "...",
        "statistics": {...}
    }
    """

    urls = extract_urls(
        search_output
    )

    pages = scrape_multiple_urls(
        urls
    )

    merged = merge_research(
        pages
    )

    stats = research_statistics(
        urls,
        pages,
    )

    return {

        "urls": urls,

        "pages": pages,

        "research": merged,

        "statistics": stats,

    }