import requests
import functools
import operator
import re
import asyncio
import logging
from functools import partial

from typing import Dict, List
from bs4 import BeautifulSoup, SoupStrainer
from recommender.settings import GOODREADS_URL

book_id_regex = re.compile(r"/(\d*)?(-|.)")
tr_only = SoupStrainer('tr')

flatten = lambda l: functools.reduce(operator.iconcat, l, [])  # noqa: E731
unique = lambda l: list(set(l))  # noqa: E731


def corr(s):
    return re.sub(r'\.(?! )', '. ', re.sub(r' +', ' ', s))


def extract_book_preview(page):
    try:
        soup = BeautifulSoup(page.text, 'lxml')
        series = soup.select('#bookSeries > a')
        return {
            'url': page.url,
            'title': soup.find(id='bookTitle').text.strip(),
            'series': {
                'title': series[0].text.strip(),
                'url': f"{GOODREADS_URL}{series[0].attrs['href']}"
            } if len(series) else None,
            'authors': {
                a.text.strip(): a.attrs['href']
                for a in soup.find_all('a', class_='authorName')
            },
            'cover':  soup.find(id='coverImage').attrs['src'],
            'blurb': corr(soup.select('#description span')[0].text)
        }
    except AttributeError:
        return None


def paginate(url: str, pages: int) -> List[str]:
    return [f"{url}?page={str(p)}" for p in range(2, pages + 1)]


def get_book_id(url: str) -> str:
    return re.findall(book_id_regex, url)[3][0]


def filter_out_dublicates(books: List[Dict[str, str]]) -> List[Dict[str, str]]:
    return list({v['title']: v for v in books}.values())


async def get_book_preview(link: str, executor) -> Dict[str, str]:
    loop = asyncio.get_event_loop()
    logging.debug(f"[MAIN] Requesting {link}")
    page = await loop.run_in_executor(
        executor,
        partial(
            requests.get,
            link
        )
    )
    return extract_book_preview(page)
