import pytest
from concurrent.futures import ThreadPoolExecutor

from recommender.book import extract_book_data


@pytest.mark.asyncio
async def test_book_data_extraction():
    book_url = "https://www.goodreads.com/book/show/3.Harry_Potter_and_the_Sorcerer_s_Stone"
    executor = ThreadPoolExecutor(max_workers=1)
    res = await extract_book_data(book_url, executor)
    assert res == {
        'url': 'https://www.goodreads.com/book/show/3.Harry_Potter_and_the_Sorcerer_s_Stone',
        'keywords': 'fantasy fiction young-adult books-i-own ya series magic childrens children middle-grade adventure classics audiobook childhood children-s j-k-rowling sci-fi-fantasy kids children-s-books favorite-books default favorite re-reads fantasy-sci-fi english ya-fantasy books read-more-than-once paranormal urban-fantasy witches childrens-books mystery faves british novel rereads favorite-series teen my-favorites childhood-favorites ya-fiction supernatural jk-rowling audio-books kids-books harry-potter-series audible bookshelf read-in-english classic on-my-shelf ebook re-reading scifi-fantasy juvenile favs my-bookshelf favourite children-s-literature youth all-time-favourites young-adult-fiction childhood-books wizards fantasia 5-star'
    }
