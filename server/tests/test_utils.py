import requests
from recommender.utils import (
    extract_book_preview,
    flatten,
    unique,
    paginate,
    get_book_id,
    filter_out_dublicates
)


def test_flatten():
    assert ['one', 'two'] == flatten([['one'], ['two']])


def test_unique():
    assert [1, 2, 3] == unique([1, 2, 2, 2, 3, 1, 3])


def test_extract_book_preview():
    book_url = "https://www.goodreads.com/book/show/3.Harry_Potter_and_the_Sorcerer_s_Stone"
    page = requests.get(book_url)
    res = extract_book_preview(page)
    assert res['title'] == "Harry Potter and the Sorcerer's Stone"
    assert res['url'] == book_url
    assert res['series']['title'] == "(Harry Potter #1)"


def test_paginate():
    assert paginate('http://example.com', 5) == [
        'http://example.com?page=2',
        'http://example.com?page=3',
        'http://example.com?page=4',
        'http://example.com?page=5'
    ]


def test_get_book_id():
    assert get_book_id("https://www.goodreads.com/book/show/3.Harry_Potter_and_the_Sorcerer_s_Stone") == "3"
