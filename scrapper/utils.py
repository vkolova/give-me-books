from bs4 import BeautifulSoup


def extract_book_preview(page):
    soup = BeautifulSoup(page.content, 'html.parser')
    data = {}
    data['url'] = page.url
    data['title'] = soup.find(id='bookTitle').text.strip()
    data['authors'] = {a.text.strip(): a.attrs['href'] for a in soup.find_all('a', class_='authorName')}
    data['rating'] = soup.select('#bookMeta > span:nth-child(2)')[0].text.strip()
    data['cover'] = soup.find(id='coverImage').attrs['src']
    data['blurb'] = soup.select('#description span')[1].text.strip()
    return data