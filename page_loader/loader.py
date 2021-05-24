import os
import os.path
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path


# ! Проверка url-адресов, является ли переданный URL-адрес действительным:
def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def url_convert(url):
    if not is_valid(url):
        print('Not a valid URL')
    _, urls = re.split('://', url)
    try:
        pos = urls.index('?')
        # ! нахождение индекса для '?'
        urls = urls[:pos]
        # ! срез по найденному индексу
    except ValueError:
        pass
    # ! убирает из url-адреса символы после ? (например, "/image.png?c=3.2.5")
    part, ext = os.path.splitext(urls)
    # ! разбивает путь на пару (root, ext), где ext начинается с точки
    # ! и содержит не более одной точки
    # >>  ru.hexlet.io/courses.html
    # >> ru.hexlet.io/courses
    result2 = re.sub(r'[\W_]', '-', part) + ext
    # ! re.sub возвращает новую строку, полученную в результате замены
    # ! по шаблону. Использовал регулярные выражения,
    # ! https://proglib.io/p/regex-for-beginners/
    return result2
# >> ru-hexlet-io-courses.html
# >> ru-hexlet-io-courses


def is_extension(url):
    return bool(Path(url).suffix)


def add_extension(url, ext):
    if is_extension(url):
        file_name = url_convert(url)
    else:
        file_name = url_convert(url) + '.' + ext
        return file_name
# >> ru-hexlet-io-courses.html


def get_dir_name(url):
    dir_name = url_convert(url) + '_files'
    return dir_name


def create_dir(path, url):
    dir_path = os.path.join(path, get_dir_name(url))
    try:
        os.makedirs(dir_path, exist_ok=True)
        # ! exist_ok=True - чтобы не возникало ошибок, если каталог существует
    except OSError:
        print(f'Failed to create a directory {dir_path}')
    return dir_path


def download_web_page(url, ext='html', path='page_loader/tmp'):
    response = requests.get(url)
    response.raise_for_status()
    # ! response.raise_for_status() нужна для того, чтобы проверить,
    # ! понял вас сервер или нет. Если сервер вернёт 404 «Ресурс не найден»,
    # ! то в response не будет странички сайта, а будет только “Ошибка 404”.
    # ! Если не вызвать raise_for_status, программа подумает, что всё в
    # !  порядке,что вы так и хотели: отправить запрос на страницу,
    # ! которой нет.
    page_name = add_extension(url, ext)
    file_path = os.path.join(path, page_name)
    with open(file_path, 'wb') as file:
        # ! Список режимов доступа к файлу, контекстный менеджер
        # ! http://pythonicway.com/python-fileio
        file.write(response.content)
    return file_path


def download_web_link(path, url):
    response = requests.get(url, stream=True)
    # !  # download the body of response by chunk, not immediately
    response.raise_for_status()
    file_name = url_convert(url)
    file_path = os.path.join(path, file_name)
    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path


def download(path, url):
    ext = 'html'
    # path = os.path.abspath(path)
    # ! path.abspath выдает абсолютный путь
    dir_for_img = create_dir(path, url)
    web_page_path = download_web_page(url, ext, path)
    for element in get_images(url):
        download_web_link(dir_for_img, element)
    print(web_page_path)
    return dir_for_img
# >> возвращает путь: page_loader/data/ru-hexlet-io-courses_files

# todo Нужно: 1) заменять ссылки URL на ссылки на файлы из dir_for_img

# todo Тестирование:
# todo 1) все ли ссылки скачались
# todo 2) картинка сайта и скаченного сайта совпадает?


def get_images(url):
    domain_name = urlparse(url).netloc
    tags_src = []
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    tags_img = soup.find_all('img', src=True)
    for tag in tags_img:
        src = tag['src']
        if not src:
            continue
        src = urljoin(url, src)
        parsed_src = urlparse(src)
        src = parsed_src.scheme + "://" + parsed_src.netloc + parsed_src.path
        if domain_name in src:
            tags_src.append(src)
    return tags_src
