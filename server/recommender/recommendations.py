from typing import List

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


def generate_recommendations(
    target: str,
    file_name: str,
    rec_count: int = 10
) -> List[str]:
    ds = pd.read_csv(file_name)
    tf = TfidfVectorizer()
    tfidf_matrix = tf.fit_transform(ds['keywords'])

    cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)
    results = {}
    for idx, row in ds.iterrows():
        similar_indices = cosine_similarities[idx].argsort()[:-100:-1]
        similar_items = [ds['url'][i] for i in similar_indices]
        results[row['url']] = similar_items[1:]

    return [rec for rec in results[target][:rec_count] if rec != target]
