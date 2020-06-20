import requests
import functools
import operator
import re
import random

from typing import List
from bs4 import BeautifulSoup, SoupStrainer
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

book_id_regex = re.compile(r"/(\d*)?(-|.)")
tr_only = SoupStrainer('tr')

software_names = [SoftwareName.CHROME.value, SoftwareName.FIREFOX.value, SoftwareName.OPERA.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value, OperatingSystem.MAC.value]
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

flatten = lambda l: functools.reduce(operator.iconcat, l, [])
unique = lambda l: list(set(l))

def corr(s):
    return re.sub(r'\.(?! )', '. ', re.sub(r' +', ' ', s))

def extract_book_preview(page):
    soup = BeautifulSoup(page.text, 'html.parser')
    data = {}
    data['url'] = page.url
    data['title'] = soup.find(id='bookTitle').text.strip()
    data['authors'] = {a.text.strip(): a.attrs['href'] for a in soup.find_all('a', class_='authorName')}
    data['rating'] = soup.select('#bookMeta > span:nth-child(2)')[0].text.strip()
    data['cover'] = soup.find(id='coverImage').attrs['src']
    data['blurb'] = corr(soup.select('#description span')[0].text)
    return data

def paginate(url: str, pages: int) -> List[str]:
    return [f"{url}?page={str(p)}" for p in range(2, pages + 1)]


def get_book_id(url: str) -> str:
    return re.findall(book_id_regex, url)[3][0]
