import asyncio
from sanic import Sanic
from sanic_cors import CORS
from sanic.response import json
import requests
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import logging
from datetime import timedelta
import sqlite3
import uuid

from typing import List, Dict

import requests_cache
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from recommender.utils import (
    extract_book_preview,
    unique,
    get_book_id,
    filter_out_dublicates,
    get_book_preview
)
from recommender.book import gather_book_data, filter_out_irrelevant
from recommender.lists import gather_lists_urls, gather_books_from_lists
from recommender.shelf import gather_books_from_shelves, gather_shelves_urls
from recommender.emails import send_recommendations_to_email
from recommender.recommendations import generate_recommendations

logging.basicConfig(level=logging.DEBUG)

expire_after = timedelta(days=3)
requests_cache.install_cache('app_cache', expire_after=expire_after)

executor = ThreadPoolExecutor(max_workers=300)
app = Sanic("Book-Recommender")
searches = {}
CORS(app)


async def book_results_preview(urls: List[str], executor) -> List[Dict[str, str]]:
    done, _ = await asyncio.wait(
        [get_book_preview(url, executor) for url in urls],
        return_when=asyncio.ALL_COMPLETED
    )
    return filter_out_dublicates([t.result() for t in done])[:10]


@app.route("/preview", methods=['GET'])
async def preview(request):
    logging.debug(f"[MAIN] Requesting {request.args['url'][0]}")
    page = requests.get(
        request.args['url'][0]
    )
    return json(extract_book_preview(page))


@app.route("/shelves", methods=['GET'])
async def shelves(request):
    target_url = request.args['url'][0]
    book_id = get_book_id(target_url)
    shelves = await gather_shelves_urls(f'https://www.goodreads.com/book/shelves/{book_id}', executor)
    shelves = [s.split('/')[-1] for s in shelves]
    return json({'shelves': filter_out_irrelevant(shelves)})


@app.route("/recommendation", methods=['GET'])
async def recommendation(request):
    target_url = request.args['url'][0]
    target_shelves = request.args.get('shelves', None)
    book_id = get_book_id(target_url)
    books = []
    try:
        if target_shelves:
            shelves = [f"/genres/{s}" for s in target_shelves.split(',')] \
                if target_shelves \
                else await gather_shelves_urls(f'https://www.goodreads.com/book/shelves/{book_id}', executor)
            if shelves:
                books.extend(await gather_books_from_shelves(shelves[2:5], executor))
        books = unique(books)
        if not books:
            lists = await gather_lists_urls(f'https://www.goodreads.com/list/book/{book_id}', executor)
            if lists:
                books.extend(await gather_books_from_lists(lists[:3], executor))
        if len(books) < 1:
            return json({'books': []})

        book_data = await gather_book_data(books, executor)
        target_book_data = await gather_book_data(
            [f"/book/show/{target_url.split('/')[-1]}"],
            executor
        )
        target_book_data = target_book_data[0]
        if target_shelves:
            target_book_data["keywords"] = ' '.join(target_shelves.split(','))
        book_data.append(target_book_data)
        search_id = str(uuid.uuid4()).split('-')[0]

        df = pd.json_normalize(book_data)
        df.to_csv(f'{search_id}.csv', index=False, encoding='utf-8')

        recommentations = generate_recommendations(target_url, f'{search_id}.csv')
        book_reccomendations = await book_results_preview(
            recommentations,
            executor
        )
    except sqlite3.OperationalError:
        logging.error(f"[MAIN] DATABSE IS LOCKED", exc_info=True)

    searches[search_id] = {
        'target': target_book_data['url'],
        'books': book_reccomendations
    }
    return json({'books': book_reccomendations, 'search_id': search_id})


@app.route("/email", methods=['GET'])
async def email(request):
    search_id = request.args.get('search_id', None)
    email_address = request.args.get('email', None)

    if search_id and searches[search_id] and email_address:
        book_reccomendations = searches[search_id]['books']
        page = requests.get(
            searches[search_id]['target']
        )
        target_data = extract_book_preview(page)
        asyncio.wait(
            send_recommendations_to_email(
                target_data['title'],
                email_address, book_reccomendations
            )
        )
    return json({'status': 'ok'})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
