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

def extract_book_preview(page):
    soup = BeautifulSoup(page.text, 'html.parser')
    data = {}
    data['url'] = page.url
    data['title'] = soup.find(id='bookTitle').text.strip()
    data['authors'] = {a.text.strip(): a.attrs['href'] for a in soup.find_all('a', class_='authorName')}
    data['rating'] = soup.select('#bookMeta > span:nth-child(2)')[0].text.strip()
    data['cover'] = soup.find(id='coverImage').attrs['src']
    data['blurb'] = soup.select('#description span')[0].text.strip()
    return data

def paginate(url: str, pages: int) -> List[str]:
    return [f"{url}?page={str(p)}" for p in range(2, pages + 1)]


def get_book_id(url: str) -> str:
    # return url.split('-')[0].split('/')[-1].split('.')[0]
    return re.findall(book_id_regex, url)[3][0]


def get_proxy_servers():
    page = requests.get('https://free-proxy-list.net/')
    soup = BeautifulSoup(page.text, 'lxml')
    proxies = []
    for tr in soup.select('#proxylisttable > tbody > tr'):
        tds = tr.select('td')
        if tds[6].text == 'yes':
            proxies.append(f"{tds[0].text}:{tds[1].text}")
    return proxies

ip_addresses = get_proxy_servers()

def get_proxy():
    proxy_index = random.randint(0, len(ip_addresses) - 1)
    proxy = {
        # "http": ip_addresses[proxy_index],
        "https": f"https://{ip_addresses[proxy_index]}"
    }
    print(f"-- {proxy}")
    return proxy
