import validators
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def validate(url):
    errors = {}
    if len(url) > 255:
        errors['big_len'] = 'URL привышает размер в 255 символов'
    if not validators.url(url):
        errors['invalid'] = 'Некорректный URL'
    if not url:
        errors['empty'] = 'URL не должен быть пустой'
    return errors


def normalize_url(url):
    parsed_url = urlparse(url)
    valid_url = parsed_url.scheme + '://' + parsed_url.netloc
    return valid_url


def get_site_data(url):
    soup = BeautifulSoup(url, 'html.parser')
    h1 = soup.find('h1').text if soup.find_all('h1') else ''
    title = soup.find('title').text if soup.find_all('title') else ''
    descr_search = soup.find('meta', {'name': 'description'})
    description = descr_search.get('content') if descr_search else ''
    return h1, title, description
