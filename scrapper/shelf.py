from typing import List

import asyncio
from bs4 import BeautifulSoup, SoupStrainer
from concurrent.futures import ThreadPoolExecutor
import logging
import requests
import time
from functools import partial

from settings import GOODREADS_URL, SHELVES_LOAD_FIRST_PAGE_ONLY, SHELVES_PAGES_TO_READ
from utils import paginate, flatten, unique, user_agent_rotator

shelf_urls_only = SoupStrainer('a', {'class': 'mediumText actionLinkLite'})
book_titles_only = SoupStrainer('a', {'class': 'bookTitle'})
div_left_container = SoupStrainer('div', {'class': 'leftContainer'})

def parse_shelf_urls(text: str) -> List[str]:
    soup = BeautifulSoup(text, 'lxml', parse_only=shelf_urls_only)
    return [l.get('href') for l in soup.find_all('a')]

def parse_book_urls(text: str) -> List[str]:
    soup = BeautifulSoup(text, 'lxml', parse_only=book_titles_only)
    return [l.get('href') for l in soup.find_all('a')]

def parse_pages_number(text: str) -> str:
    soup = BeautifulSoup(text, 'lxml', parse_only=div_left_container)
    return soup.select('div.leftContainer > div > div > a')[-2].text

def prep_shelf_urls(urls: List[str]) -> List[str]:
    return [f"{GOODREADS_URL}{url.replace('genres', 'shelf/show')}" for url in urls]

async def parse_shelves_page(page_url: str, executor: ThreadPoolExecutor) -> List[str]:
    logging.debug(f"[SHLF] Requesting {page_url}")
    loop = asyncio.get_event_loop()
    page = await loop.run_in_executor(
        executor,
        partial(
            requests.get,
            page_url,
            headers={'User-Agent': user_agent_rotator.get_random_user_agent()}
        )
    )
    return parse_shelf_urls(page.text)

async def parse_books_from_shelf(shelf_url: str, executor: ThreadPoolExecutor) -> List[str]:
    logging.debug(f"[SHLF] Requesting {shelf_url}")
    loop = asyncio.get_event_loop()
    page = await loop.run_in_executor(
        executor,
        partial(
            requests.get,
            shelf_url,
            headers={'User-Agent': user_agent_rotator.get_random_user_agent()}
        )
    )
    return parse_book_urls(page.text)

def parse_books_from_shelf_non_async(shelf_url: str, executor: ThreadPoolExecutor) -> List[str]:
    logging.debug(f"[SHLF] Requesting {shelf_url}")
    page = requests.get(
        shelf_url,
        headers={'User-Agent': user_agent_rotator.get_random_user_agent()}
    )
    return parse_book_urls(page.text)


async def get_shelves(shelves_page_url: str, executor: ThreadPoolExecutor) -> List[str]:
    logging.debug(f"[SHLF] Requesting {shelves_page_url}")
    loop = asyncio.get_event_loop()
    shelves_page = await loop.run_in_executor(
        executor,
        partial(
            requests.get,
            shelves_page_url,
            headers={'User-Agent': user_agent_rotator.get_random_user_agent()}
        )
    )
    first_page_shelves = parse_shelf_urls(shelves_page.text)

    if SHELVES_LOAD_FIRST_PAGE_ONLY:
        return first_page_shelves, []
  
    try:
        pages = parse_pages_number(shelves_page.text)
        iterate_pages_count = min(int(pages), SHELVES_PAGES_TO_READ)
        logging.debug(f"[SHLF] Iterating over {iterate_pages_count} shelves pages")
        shelves_pages = paginate(shelves_page_url, iterate_pages_count)
        return first_page_shelves, shelves_pages
    except Exception:
        logging.error("[SHLF]", exc_info=True)
        return first_page_shelves, []


async def gather_shelves_urls(shelves_page_url: str, executor: ThreadPoolExecutor) -> List[str]:
    shelves, shelves_pages = await get_shelves(shelves_page_url, executor)
    if shelves_pages:
        done, _ = await asyncio.wait(
            [parse_shelves_page(p, executor) for p in shelves_pages],
            return_when=asyncio.ALL_COMPLETED
        )
        shelves.extend(flatten([t.result() for t in done]))
    return shelves


async def gather_books_from_shelves(shelves_urls: List[str], executor: ThreadPoolExecutor) -> List[str]:
    urls = prep_shelf_urls(shelves_urls)
    done, _ = await asyncio.wait(
        [parse_books_from_shelf(s, executor) for s in urls],
        return_when=asyncio.ALL_COMPLETED
    )
    return unique(flatten([t.result() for t in done]))
