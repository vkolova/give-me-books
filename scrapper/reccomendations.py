import asyncio
import concurrent
from concurrent.futures import ThreadPoolExecutor
import logging
import time
from typing import List, Dict

import requests
from requests.models import Response
from bs4 import BeautifulSoup, SoupStrainer
import nest_asyncio
from multiprocessing import Pool

from urllib.parse import urljoin, urlparse

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   

user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

logging.basicConfig(level=logging.WARNING)


only_a_tags = SoupStrainer("a")
only_list_titles = SoupStrainer("a", {'class': 'listTitle'})
shelf_urls_only = SoupStrainer('a', {'class': 'mediumText actionLinkLite'})
book_titles_only = SoupStrainer('a', {'class': 'bookTitle'})
similar_books_title = SoupStrainer('a', {'class': 'gr-h3 gr-h3--serif gr-h3--noMargin'})
shelf_stats = SoupStrainer('div', {'class': 'shelfStat'})

nest_asyncio.apply()

GOODREADS = 'https://www.goodreads.com'
LISTS_PAGE_URL = f'{GOODREADS}/list/book'

executor = ThreadPoolExecutor(max_workers=150)

flatten = lambda l: [item for sublist in l for item in sublist]
unique = lambda l: list(set(l))

def get_book_id(url: str) -> str:
    return url.split('-')[0].split('/')[-1].split('.')[0]  

def paginate(url: str, pages: str) -> List[str]:
    return [f"{url}?page={str(p)}" for p in range(2, int(pages) + 1)]


def parse_list_urls(list_url: str) -> List[str]:
    logging.info(f"Requesting {list_url}")
    soup = BeautifulSoup(requests.get(list_url).text, 'lxml', parse_only=only_list_titles)
    hrefs = [l.get('href') for l in soup if hasattr(l, 'href')]
    return [urljoin(url, urlparse(url).path) for url in hrefs]


async def lists_urls(lists_page_url: str) -> List[str]:
    logging.info(f"Requesting {lists_page_url}")
    loop = asyncio.get_event_loop()
    lists_page = await loop.run_in_executor(
        executor,
        requests.get,
        lists_page_url
    )
    soup = BeautifulSoup(lists_page.text, 'lxml')
    first_page_lists = [
        urljoin(l.get('href'), urlparse(l.get('href')).path)
        for l in soup.find_all('a', class_='listTitle')
    ]

    try:
        pages = soup.select('div.mainContentFloat > div.leftContainer > div > a')[-2].text
        tasks = [
            loop.run_in_executor(
                executor,
                parse_list_urls,
                page
            ) for page in paginate(lists_page_url, pages)[:10]
        ]
        return flatten(asyncio.run(asyncio.gather(*tasks))) + first_page_lists
    except IndexError:
        return first_page_lists


# ........ BOOKS FROM LISTS:

def parse_books_from_list(list_url: str) -> List[str]:
    logging.info(f"Requesting {list_url}")
    soup = BeautifulSoup(
        requests.get(list_url).text,
        'lxml',
        parse_only=book_titles_only
    )
    return [l.get('href') for l in soup if hasattr(l, 'href')]

def get_books_in_list(list_url: str, loop) -> List[str]:
    logging.info(f"Requesting {list_url}")
    soup = BeautifulSoup(
        requests.get(list_url).text,
        'lxml'
    )
    try:
        pages = soup.select('#all_votes > div.pagination > a')[-2].text
        lists_pages = paginate(list_url, pages)[:2]
    except IndexError:
        lists_pages = [list_url]
    tasks = [
        loop.run_in_executor(
            executor,
            parse_books_from_list,
            list_url
        ) for list_url in lists_pages
    ]
    return flatten(loop.run_until_complete(asyncio.gather(*tasks)))


async def books_from_lists(lists: List[str]) -> List[str]:
    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(
            executor,
            get_books_in_list,
            *(f"{GOODREADS}{list_url}", loop)
        ) for list_url in lists[:9]
    ]
    return unique(flatten(loop.run_until_complete(asyncio.gather(*tasks))))


def parse_shelves_urls(shelves_page_url: str) -> List[str]:
    logging.info(f"Requesting {shelves_page_url}")
    soup = BeautifulSoup(
        requests.get(shelves_page_url).text,
        'lxml',
        parse_only=shelf_urls_only
    )
    return [l.get('href') for l in soup if hasattr(l, 'href')]

async def get_shelves(shelves_page_url: str) -> List[str]:
    logging.info(f"Requesting {shelves_page_url}")
    loop = asyncio.get_event_loop()
    shelves_page = await loop.run_in_executor(
        executor,
        requests.get,
        shelves_page_url
    )
    soup = BeautifulSoup(shelves_page.text, 'lxml', parse_only=shelf_urls_only)
    return [l.get('href') for l in soup if hasattr(l, 'href')]

    # soup = BeautifulSoup(shelves_page.text, 'lxml')
    # first_page_shelves = [
    #     l.get('href') for l in soup.select('a.mediumText.actionLinkLite')
    # ]
    # return first_page_shelves
  
    # try:
    #     pages = soup.select('div.mainContentContainer > div.mainContent > div.mainContentFloat > div.leftContainer > div > div > a')[-2].text
    #     shelves_page_pages = paginate(shelves_page_url, pages)[:1]
    #     tasks = [
    #         loop.run_in_executor(
    #             executor,
    #             parse_shelves_urls,
    #             page
    #         ) for page in shelves_page_pages
    #     ]
    #     return flatten(asyncio.run(asyncio.gather(*tasks))) + first_page_shelves
    # except IndexError:
    #     return first_page_shelves


async def get_shelves_from_shelves_page(urls: List[str], loop) -> List[str]:
    tasks = [
        loop.run_in_executor(
            executor,
            parse_shelves_urls,
            page
        ) for page in urls
    ]
    return flatten(asyncio.run(asyncio.gather(*tasks)))


async def get_similar_books(similar_books_url: str) -> List[str]:
    logging.info(f"Requesting {similar_books_url}")
    loop = asyncio.get_event_loop()
    similar_page = await loop.run_in_executor(
        executor,
        requests.get,
        similar_books_url
    )
    soup = BeautifulSoup(similar_page.text, 'lxml', parse_only=similar_books_title)
    return [l.get('href') for l in soup if hasattr(l, 'href')]


async def get_books_on_shelves(shelves_list: List[str]) -> List[str]:
    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(
            executor,
            parse_books_from_list,
            f"{GOODREADS}{shelf.replace('genres', 'shelf/show')}"
        ) for shelf in shelves_list[:10]
    ]
    return flatten(asyncio.run(asyncio.gather(*tasks)))


def extract_book_data(book_url: str) -> Dict[str, str]:
    book_id = get_book_id(book_url)
    shelves_page_url = f"{GOODREADS}/book/shelves/{book_id}"
    logging.info(f"Requesting {shelves_page_url}")
    soup = BeautifulSoup(
        requests.get(shelves_page_url).text,
        'lxml',
        parse_only=shelf_urls_only
    )
    return {
        'url': book_url,
        'keywords': [l.text for l in soup if hasattr(l, 'text')]
    }


async def gather_book_data(book_urls: List[str]) -> List[Dict[str, str]]:
    large_executor = ThreadPoolExecutor(max_workers=500)
    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(
            large_executor,
            extract_book_data,
            f"{GOODREADS}{url}"
        ) for url in book_urls
    ]
    return asyncio.run(asyncio.gather(*tasks))


def main():
    s = time.perf_counter()
    book_url = ''
    book_id = get_book_id(book_url)

    logging.info(f"Requesting {book_url}")
    shelves_page_url = f"{GOODREADS}/book/shelves/{book_id}"
    similar_books_url = f"{GOODREADS}/book/similar/{book_id}"
    lists_page_url = f"{LISTS_PAGE_URL}/{book_id}"

    similar_books, shelves_list = asyncio.run(
        asyncio.gather(
            get_similar_books(similar_books_url),
            get_shelves(shelves_page_url)
        )
    )

    print(len(similar_books), len(shelves_list))
    books_from_same_shelves, lists = asyncio.run(
        asyncio.gather(
            get_books_on_shelves(shelves_list),
            lists_urls(lists_page_url)
        )
    )
    print("books_from_same_shelves:", len(books_from_same_shelves), "LISTS:", len(lists))
    books_collected_from_lists = asyncio.run(books_from_lists(lists))
    print(f"books_collected_from_lists: {len(books_collected_from_lists)}")

    books = unique(similar_books + books_from_same_shelves + books_collected_from_lists)
    print("BOOKS:", len(books))

    del lists
    del shelves_list
    del similar_books
    del books_from_same_shelves
    del books_collected_from_lists

    book_details = asyncio.run(gather_book_data(books))
    print("????", book_details)

    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")

try:
    main()
except Exception as e:
    logging.error(f"FUUUUUUUUUUUUUUCK", exc_info=True)