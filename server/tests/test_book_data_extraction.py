import pytest
from concurrent.futures import ThreadPoolExecutor

from recommender.book import extract_book_data


@pytest.mark.asyncio
async def test_book_data_extraction():
    book_url = "https://www.goodreads.com/book/show/3.Harry_Potter_and_the_Sorcerer_s_Stone"
    executor = ThreadPoolExecutor(max_workers=1)
    res = await extract_book_data(book_url, executor)

    assert res["url"] == "https://www.goodreads.com/book/show/3.Harry_Potter_and_the_Sorcerer_s_Stone"
    assert "fantasy" in res["keywords"]
    assert "young-adult" in res["keywords"]