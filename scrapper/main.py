from sanic import Sanic
from sanic_cors import CORS, cross_origin
from sanic.response import json
import requests

from utils import extract_book_preview

app = Sanic("Book-Recommender")
CORS(app)

@app.route("/preview", methods=['GET'])
async def preview(request):
    print(request.args['url'][0])
    page = requests.get(request.args['url'][0])
    return json(extract_book_preview(page))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)