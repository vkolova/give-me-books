import pytest
import requests

from recommender.lists import (
    parse_pages_number,
    parse_list_pages_number,
    parse_list_urls,
    parse_book_urls
)

def test_parse_pages_number():
    lists_url = "https://www.goodreads.com/list/book/22544764"
    page = requests.get(lists_url)
    res = parse_pages_number(page.text)
    try:
        int(res)
        assert True
    except Exception:
        assert False


def test_parse_list_pages_number():
    list_url = "https://www.goodreads.com/list/show/19106.MUST_READS_"
    page = requests.get(list_url)
    res = parse_list_pages_number(page.text)
    try:
        int(res)
        assert True
    except Exception:
        assert False


def test_parse_list_urls():
    lists_url = "https://www.goodreads.com/list/book/22544764"
    page = requests.get(lists_url)
    res = parse_list_urls(page.text)
    assert all([s.startswith('/list/show/') for s in res])


def test_parse_book_urls():
    list_url = "https://www.goodreads.com/list/show/19106.MUST_READS_"
    page = requests.get(list_url)
    res = parse_list_urls(page.text)
    assert all([s.startswith('/book/show/') for s in res])

