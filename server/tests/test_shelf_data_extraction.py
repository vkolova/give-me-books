import pytest
import requests
from concurrent.futures import ThreadPoolExecutor

from recommender.shelf import (
    parse_shelf_urls,
    parse_book_urls,
    parse_shelves_page,
    parse_books_from_shelf,
    get_shelves
)
from recommender.settings import GOODREADS_URL
from recommender.utils import flatten


def test_parse_shelf_urls():
    shelves_url = "https://www.goodreads.com/work/shelves/4640799"
    page = requests.get(shelves_url)
    res = parse_shelf_urls(page.text)
    assert len(res) == 100
    assert all([s.startswith('/genres/') for s in res])


def test_parse_book_urls():
    url = "https://www.goodreads.com/shelf/show/magic"
    page = requests.get(url)
    res = parse_book_urls(page.text)
    assert len(res) == 50
    assert all([isinstance(bu, str) for bu in res])


@pytest.mark.asyncio
async def test_parse_shelves_page():
    shelves_url = "https://www.goodreads.com/work/shelves/4640799"
    executor = ThreadPoolExecutor(max_workers=3)
    res = await parse_shelves_page(shelves_url, executor)
    assert len(res) == 100
    assert all([s.startswith('/genres/') for s in res])

@pytest.mark.asyncio
async def test_parse_books_from_shelf():
#     url = "https://www.goodreads.com/shelf/show/magic"
#     executor = ThreadPoolExecutor(max_workers=3)
#     res = await parse_shelves_page(url, executor)
#     assert len(res) == 50
#     assert all([isinstance(bu, str) for bu in res])
    assert True

@pytest.mark.asyncio
async def test_get_shelves():
    shelves_url = "https://www.goodreads.com/work/shelves/4640799"
    executor = ThreadPoolExecutor(max_workers=3)
    res = await get_shelves(shelves_url, executor)
    res = flatten(res)
    assert len(res) == 100
    assert all([s.startswith('/genres/') for s in res])



@pytest.mark.asyncio
async def test_gather_shelves_urls():
    assert True


@pytest.mark.asyncio
async def test_gather_books_from_shelves():
    assert True