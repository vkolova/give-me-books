from typing import List

import asyncio
from bs4 import BeautifulSoup, SoupStrainer
from concurrent.futures import ThreadPoolExecutor
import logging
import requests
import re
from functools import partial
import sqlite3

from recommender.settings import (
    GOODREADS_URL,
    LISTS_PARSE_FIRST_PAGE_ONLY,
    LISTS_PARSE_PAGE_COUNT,
    PARSE_LIST_FIST_PAGE_ONLY,
    LIST_PAGES_TO_PARSE
)
from recommender.utils import paginate, flatten, unique

list_url_regex = re.compile(r"^(.*?)\..*")
list_titles_only = SoupStrainer('a', {'class': 'listTitle'})
div_left_container = SoupStrainer('div', {'class': 'leftContainer'})
book_titles_only = SoupStrainer('a', {'class': 'bookTitle'})
pagination_div = SoupStrainer('div', {'class': 'pagination'})


def parse_pages_number(text: str) -> List[str]:
    soup = BeautifulSoup(text, 'lxml', parse_only=div_left_container)
    try:
        return soup.select('div.leftContainer > div > a')[-2].text
    except IndexError:
        return '1'


def parse_list_pages_number(text: str) -> List[str]:
    soup = BeautifulSoup(text, 'lxml', parse_only=pagination_div)
    hrefs = soup.find_all('a')
    return hrefs[-2].text if len(hrefs) > 3 else None


def parse_list_urls(text: str) -> List[str]:
    soup = BeautifulSoup(text, 'lxml', parse_only=list_titles_only)
    return [l.get('href') for l in soup.find_all('a')]


def prep_lists_urls(urls: List[str]) -> List[str]:
    return [
        f"{GOODREADS_URL}{re.search(list_url_regex, url).group(1)}"
        for url in urls
    ]


def parse_book_urls(text: str) -> List[str]:
    soup = BeautifulSoup(text, 'lxml', parse_only=book_titles_only)
    return [l.get('href') for l in soup.find_all('a')]


async def parse_lists_page(
    page_url: str,
    executor: ThreadPoolExecutor
) -> List[str]:
    logging.debug(f"[LIST] Requesting {page_url}")
    loop = asyncio.get_event_loop()
    try:
        page = await loop.run_in_executor(
            executor,
            partial(
                requests.get,
                page_url
            )
        )
    except sqlite3.OperationalError:
        pass
    return parse_list_urls(page.text)


async def get_lists(
    lists_page_url: str,
    executor: ThreadPoolExecutor
) -> List[str]:
    logging.debug(f"[LIST] Requesting {lists_page_url}")
    loop = asyncio.get_event_loop()
    lists_page = await loop.run_in_executor(
        executor,
        partial(
            requests.get,
            lists_page_url
        )
    )
    first_page_lists = parse_list_urls(lists_page.text)

    if LISTS_PARSE_FIRST_PAGE_ONLY:
        return first_page_lists, []

    try:
        pages = parse_pages_number(lists_page.text)
        page_count = min(int(pages), LISTS_PARSE_PAGE_COUNT)
        logging.debug(f"[LIST] Iterating over {page_count} lists pages")
        lists_pages = paginate(lists_page_url, page_count)
        return first_page_lists, lists_pages
    except Exception:
        logging.error("[LIST]", exc_info=True)
        return first_page_lists, []


async def parse_list_first_page(
    list_url: str,
    executor: ThreadPoolExecutor
) -> List[str]:
    logging.debug(f"[LIST] Requesting {list_url}")
    loop = asyncio.get_event_loop()
    page = await loop.run_in_executor(
        executor,
        partial(
            requests.get,
            list_url
        )
    )
    first_page_books = parse_book_urls(page.text)
    if PARSE_LIST_FIST_PAGE_ONLY:
        return first_page_books, []

    pages = parse_list_pages_number(page.text)
    if pages:
        iterate_pages_count = min(int(pages), LIST_PAGES_TO_PARSE)
        return first_page_books, paginate(list_url, iterate_pages_count)
    return first_page_books, []


async def parse_book_urls_from_list_page(
    list_url: str,
    executor: ThreadPoolExecutor
) -> List[str]:
    logging.debug(f"[LIST] Requesting {list_url}")
    loop = asyncio.get_event_loop()
    page = await loop.run_in_executor(
        executor,
        partial(
            requests.get,
            list_url
        )
    )
    return parse_book_urls(page.text)


async def gather_lists_urls(
    lists_page_url: str,
    executor: ThreadPoolExecutor
) -> List[str]:
    lists, lists_pages = await get_lists(lists_page_url, executor)
    if lists_pages:
        done, _ = await asyncio.wait(
            [parse_lists_page(p, executor) for p in lists_pages],
            return_when=asyncio.ALL_COMPLETED
        )
        lists.extend(flatten([t.result() for t in done]))
    return lists


async def gather_books_from_lists(
    lists_urls: List[str],
    executor: ThreadPoolExecutor
) -> List[str]:
    urls = prep_lists_urls(lists_urls)
    done, _ = await asyncio.wait(
        [parse_list_first_page(s, executor) for s in urls],
        return_when=asyncio.ALL_COMPLETED
    )
    books, lists_pages = zip(*[t.result() for t in done])
    books = list(books)
    pages_urls = flatten(lists_pages)
    if pages_urls:
        done, _ = await asyncio.wait(
            [
                parse_book_urls_from_list_page(s, executor)
                for s in pages_urls
            ],
            return_when=asyncio.ALL_COMPLETED
        )
        books.extend([t.result() for t in done])
    return unique(flatten(books))
