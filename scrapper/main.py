import asyncio
from sanic import Sanic
from sanic_cors import CORS, cross_origin
from sanic.response import json
import requests
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import csv
from functools import partial
import logging
from datetime import timedelta
import sqlite3

from typing import List, Dict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from utils import extract_book_preview, unique, get_book_id, user_agent_rotator
from book import gather_book_data
from lists import gather_lists_urls, gather_books_from_lists
from shelf import gather_books_from_shelves, gather_shelves_urls

from settings import GOODREADS_URL

logging.basicConfig(level=logging.DEBUG)

import requests_cache
expire_after = timedelta(days=1)
requests_cache.install_cache('app_cache', expire_after=expire_after)

executor = ThreadPoolExecutor(max_workers=300)
app = Sanic("Book-Recommender")
CORS(app)

def filter_out_dublicates(books: List[Dict[str, str]]) -> List[Dict[str, str]]:
    return list({v['title']:v for v in books}.values()) 

async def get_book_preview(link: str, executor) -> Dict[str, str]:
    loop = asyncio.get_event_loop()
    logging.debug(f"[MAIN] Requesting {link}")
    page = await loop.run_in_executor(
        executor,
        partial(
            requests.get,
            link,
            headers={'User-Agent': user_agent_rotator.get_random_user_agent()}
        )
    )
    return extract_book_preview(page)


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
        request.args['url'][0],
        headers={
            'User-Agent': user_agent_rotator.get_random_user_agent()
        }
    )
    return json(extract_book_preview(page))


@app.route("/recommendation", methods=['GET'])
async def recommendation(request):
    target_url = request.args['url'][0]
    book_id = get_book_id(target_url)
    books = []
    try:
        lists = await gather_lists_urls(f'https://www.goodreads.com/list/book/{book_id}', executor)
        if lists:
            books.extend(await gather_books_from_lists(lists[:3], executor))
        else:
            shelves = await gather_shelves_urls(f'https://www.goodreads.com/book/shelves/{book_id}', executor)
            if shelves:
                books.extend(await gather_books_from_shelves(shelves[:3], executor))
        books.append(f"/book/show/{target_url.split('/')[-1]}")
        books = unique(books)
    except sqlite3.OperationalError:
        logging.error(f"[MAIN] ", exc_info=True)
        pass

    if len(books) < 2:
        return json({'books': [] })

    book_data = await gather_book_data(books, executor)
    df = pd.json_normalize(book_data)
    df.to_csv('results.csv', index=False, encoding='utf-8')

    ds = pd.read_csv("results.csv")

    tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=0, stop_words='english')
    tfidf_matrix = tf.fit_transform(ds['keywords'])

    cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)
    results = {}
    for idx, row in ds.iterrows():
        similar_indices = cosine_similarities[idx].argsort()[:-100:-1] 
        # similar_items = [(cosine_similarities[idx][i], ds['url'][i]) for i in similar_indices] 
        similar_items = [ds['url'][i] for i in similar_indices] 
        results[row['url']] = similar_items[1:]
    
    book_reccomendations = await book_results_preview(results[target_url][:15], executor)
    import json as p_json

    with open("recommendations.json", "w+") as outfile:
        p_json.dump(book_reccomendations, outfile)

    return json({ 'books': book_reccomendations })



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)