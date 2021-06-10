import os
import os.path
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from page_loader.utils import get_project_root



# ! Проверка url-адресов, является ли переданный URL-адрес действительным:
def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def convert_url_to_name(url):
    if not is_valid(url):
        print('Not a valid URL')
        return
    _, urls = re.split('://', url)
    try:
        pos = urls.index('?')
        # ! нахождение индекса для '?'
        urls = urls[:pos]
        # ! срез по найденному индексу
    except ValueError:
        pass
    # ! убирает из url-адреса символы после ? (например, "/image.png?c=3.2.5")
    part, _ = os.path.splitext(urls)
    # ! разбивает путь на пару (root, ext), где ext начинается с точки
    # ! и содержит не более одной точки
    # >>  ru.hexlet.io/courses.html
    # >> ru.hexlet.io/courses
    name = re.sub(r'[\W_]', '-', part)
    # ! re.sub возвращает новую строку, полученную в результате замены
    # ! по шаблону. Использовал регулярные выражения,
    # ! https://proglib.io/p/regex-for-beginners/
    return name
# >> ru-hexlet-io-courses
# >> ru-hexlet-io-courses


# def is_extension(file):
#     suff = PurePosixPath(file).suffix
#     return bool(suff)


def add_extension(url, ext):
    file_name = convert_url_to_name(url) + '.' + ext
    return file_name
# >> ru-hexlet-io-courses.html


def get_dir_name(url):
    dir_name = convert_url_to_name(url) + '_files'
    return dir_name


def create_dir(path, url):
    dir_path = os.path.join(path, get_dir_name(url))
    try:
        os.makedirs(dir_path, exist_ok=True)
        # ! exist_ok=True - чтобы не возникало ошибок, если каталог существует
    except OSError:
        print(f'Failed to create a directory {dir_path}')
    return dir_path



def get_web_page(url, ext='html', path='page_loader/tmp'):
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
    domain_name = urlparse(url).scheme +"://" + urlparse(url).netloc
    with open(file_path, 'wb') as file:
        # ! Список режимов доступа к файлу, контекстный менеджер
        # ! http://pythonicway.com/python-fileio
        file.write(response.content)
    return file_path, domain_name


def change_src(dir_path, file_path, domain_name):
    html = open(file_path, 'r')
    soup = BeautifulSoup(html, "html.parser")
    html.close
    tags_img = soup.find_all('img', src=True)
    for tag in tags_img:
        src = tag.get('src')
        if not src.startswith('http'):
            tag['src'] = urljoin(domain_name, src)
        else:
            continue
        src_new = tag['src']
        # print(tag['src'])
        #     tag['src'] = download_web_link(dir_path, src)
        # # tag['src'] = src
        # if domain_name in src:
        tag['src'] = download_web_link(dir_path, src_new)
    new_html = soup.prettify(formatter='html5')
    name = os.path.basename(file_path)
    file_path_new_html = os.path.join(dir_path, name)
    with open(file_path_new_html, 'w') as file:
        file.write(new_html)
    return new_html


def download_web_link(path, url):
    response = requests.get(url, stream=True)
    # !  # download the body of response by chunk, not immediately
    response.raise_for_status()
    file_name = convert_url_to_name(url)
    file_path = os.path.join(path, file_name)
    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path


def download(path, url):
    ext = 'html'
    # path = os.path.abspath(path)
    # ! path.abspath выдает абсолютный путь
    dir_for_img = create_dir(path, url)
    web_page_path, domain_name = get_web_page(url, ext, 'page_loader/tmp')
    change_src(dir_for_img, web_page_path, domain_name)
    print(web_page_path)
    return dir_for_img
# >> возвращает путь: page_loader/data/ru-hexlet-io-courses_files

# todo Нужно: 1) заменять ссылки URL на ссылки на файлы из dir_for_img

# todo Тестирование:
# todo 1) все ли ссылки скачались
# todo 2) картинка сайта и скаченного сайта совпадает?
