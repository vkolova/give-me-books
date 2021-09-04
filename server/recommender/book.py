from typing import List, Dict

import asyncio
from bs4 import BeautifulSoup, SoupStrainer
from concurrent.futures import ThreadPoolExecutor
import logging
import requests
from functools import partial
import sqlite3

from recommender.settings import GOODREADS_URL
from recommender.utils import get_book_id

shelf_urls_only = SoupStrainer('a', {'class': 'mediumText actionLinkLite'})

filtered_keywords = [
    'to-read', 'tbr', 'currently-reading', 'favorites', 'to-re-read', 'reread',
    're-read', 'own-unread', 'arc', 'arcs',
    'dnf', 'did-not-finish', 'nope', 'lost-interest', 'maybe',
    'kindle-unlimited', 'ku', 'audio', 'ebooks', 'kindle', 'unlimited',
    'wishlist', 'to-buy', 'my-books', 'my-ebooks', 'my-library', 'library',
    'owned-books', 'own-it', 'i-own', 'all-time-favorites', 'library',
    'debut', 'novels',
    'favourites',
    '5-stars', '4-stars', '3-stars', '2-stars',
    '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018',
    '2019', '2020',
    'read-in-2010', 'read-in-2011', 'read-in-2012', 'read-in-2013',
    'read-in-2014', 'read-in-2015', 'read-in-2016', 'read-in-2017',
    'read-in-2018', 'read-in-2019', 'read-in-2020',
    'read-2010', 'read-2011', 'read-2012', 'read-2013', 'read-2014',
    'read-2015', 'read-2016', 'read-2017', 'read-2018', 'read-2019',
    'read-2020',
    '2020-books', '2019-books', '2018-books', '2017-books', '2016-books',
    '2015-books'
]


def filter_out_irrelevant(keywords: List[str]) -> List[str]:
    return [
        k
        for k in keywords
        if k not in filtered_keywords
    ]


async def extract_book_data(
    book_url: str,
    executor: ThreadPoolExecutor
) -> Dict[str, str]:
    loop = asyncio.get_event_loop()
    book_id = get_book_id(book_url)
    shelves_page_url = f"{GOODREADS_URL}/book/shelves/{book_id}"
    logging.debug(f"[BOOK] Requesting {shelves_page_url}")

    try:
        page = await loop.run_in_executor(
            executor,
            partial(
                requests.get,
                shelves_page_url
            )
        )
        soup = BeautifulSoup(page.text, 'lxml', parse_only=shelf_urls_only)
        return {
            'url': book_url,
            'keywords': ' '.join(
                filter_out_irrelevant([l.text for l in soup if hasattr(l, 'text')])
                or ['none']
            )
        }
    except sqlite3.OperationalError:
        pass

    return {'url': book_url, 'keywords': ['none']}


async def gather_book_data(
    book_urls: List[str],
    executor: ThreadPoolExecutor
) -> List[Dict[str, str]]:
    done, _ = await asyncio.wait(
        [
            extract_book_data(f"{GOODREADS_URL}{url}", executor)
            for url in book_urls
        ],
        return_when=asyncio.ALL_COMPLETED
    )
    return [t.result() for t in done]
