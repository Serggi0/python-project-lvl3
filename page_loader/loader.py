import os
import os.path
import requests
import re
from pathlib import PurePosixPath
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


# ! чтобы сайт не идентифицировал как бота
HEADERS = {
    'user-agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        'AppleWebKit/537.36 (KHTML, like Gecko)'
        'Chrome/91.0.4472.101 Safari/537.36'
}


def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)
# ! Проверка url-адресов, является ли переданный URL-адрес действительным


def is_extension(file):
    suff = PurePosixPath(file).suffix
    return bool(suff)


def convert_url_to_file_name(url):
    _, urls = re.split('://', url)
    part, ext = os.path.splitext(urls)
    # ! разбивает путь на пару (root, ext), где ext начинается с точки
    # ! и содержит не более одной точки
    # >>  ru.hexlet.io/courses.html
    # >> ru.hexlet.io/courses
    name = re.sub(r'[\W_]', '-', part) + ext
    # ! re.sub возвращает новую строку, полученную в результате замены
    # ! по шаблону. Использовал регулярные выражения,
    # ! https://proglib.io/p/regex-for-beginners/
    return name
# >> ru-hexlet-io-courses or ru-hexlet-io-courses.html


def get_dir_name(url):
    _, urls = re.split('://', url)
    try:
        pos = urls.index('?')
        # ! нахождение индекса для '?'
        urls = urls[:pos]
        # ! срез по найденному индексу
    except ValueError:
        pass
    # ! убирает из url-адреса символы после ? (например, "/image.png?c=3.2.5")
    if is_extension(urls):
        part, _ = os.path.splitext(urls)
    else:
        part = urls
    # ! разбивает путь на пару (root, ext), где ext начинается с точки
    # ! и содержит не более одной точки
    # >>  ru.hexlet.io/courses.html
    # >> ru.hexlet.io/courses
    dir_name = re.sub(r'[\W_]', '-', part) + '_files'
    # ! re.sub возвращает новую строку, полученную в результате замены
    # ! по шаблону. Использовал регулярные выражения,
    # ! https://proglib.io/p/regex-for-beginners/
    return dir_name
# >> ru-hexlet-io-courses


def add_extension(url, ext):
    file_name = convert_url_to_file_name(url)
    if not is_extension(file_name):
        file_name = file_name + '.' + ext
    else:
        print(f'extention {ext} is exit!')
    return file_name
# >> ru-hexlet-io-courses.html


def create_dir(path, url):
    dir_path = os.path.join(path, get_dir_name(url))
    try:
        os.makedirs(dir_path, exist_ok=True)
        # ! exist_ok=True - чтобы не возникало ошибок, если каталог существует
    except OSError:
        print(f'Failed to create a directory {dir_path}')
    return dir_path


def get_web_page(url, ext='html', path='page_loader/tmp'):
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    # ! response.raise_for_status() нужна для того, чтобы проверить,
    # ! понял вас сервер или нет. Если сервер вернёт 404 «Ресурс не найден»,
    # ! то в response не будет странички сайта, а будет только “Ошибка 404”.
    # ! Если не вызвать raise_for_status, программа подумает, что всё в
    # !  порядке,что вы так и хотели: отправить запрос на страницу,
    # ! которой нет.
    page_name = add_extension(url, ext)
    file_path = os.path.join(path, page_name)
    domain_name = urlparse(url).scheme + "://" + urlparse(url).netloc
    with open(file_path, 'w') as file:
        # ! Список режимов доступа к файлу, контекстный менеджер
        # ! http://pythonicway.com/python-fileio
        file.write(response.text)
    return file_path, domain_name


def get_img_src(path):
    tags_src = []
    with open(path) as my_string:
        soup = BeautifulSoup(my_string, "html.parser")
        tags_img = soup.find_all('img', src=True)
        for tag in tags_img:
            src = tag.get('src')
            if is_extension(src):
                tags_src.append(src)
    return tags_src


def change_src(dir_path, file_path, domain_name):
    list_tags_src = []
    list_tags_new_src = []
    file = open(file_path, 'r')
    html = file.read()
    soup = BeautifulSoup(html, "html.parser")
    file.close
    tags_img = soup.find_all('img', src=True)
    for tag in tags_img:
        src = tag.get('src')
        if is_extension(src):
            if src.startswith(domain_name):
                continue
            else:
                tag['src'] = urljoin(domain_name, src)
            src_new = tag['src']
            list_tags_src.append(src_new)

            tag['src'] = download_web_link(dir_path, src_new)
            list_tags_new_src.append(tag['src'])
    new_html = soup.prettify(formatter='html5')
    with open(file_path, 'w') as file:
        file.write(new_html)
    return list_tags_src, list_tags_new_src


def download_web_link(path, url):
    response = requests.get(url, headers=HEADERS)
    # !  # download the body of response by chunk, not immediately
    response.raise_for_status()
    file_name = convert_url_to_file_name(url)
    file_path = os.path.join(path, file_name)
    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_name


def download(path, url):
    ext = 'html'
    if not is_valid(url):
        print('Not a valid URL')
    # path = os.path.abspath(path)
    # ! path.abspath выдает абсолютный путь
    dir_for_img = create_dir(path, url)
    web_page_path, domain_name = get_web_page(url, ext, dir_for_img)
    change_src(dir_for_img, web_page_path, domain_name)
    print(web_page_path)
    return dir_for_img
# >> возвращает путь: page_loader/data/ru-hexlet-io-courses_files
