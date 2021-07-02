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

EXTENSION_IMG = {'html', 'jpeg', 'jpg', 'png', 'gif', 'svg', 'webp'}


def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)
# ! Проверка url-адресов, является ли переданный URL-адрес действительным


def is_extension(file):
    suff = PurePosixPath(file).suffix
    return bool(suff)


def convert_path_name(path):
    if path.startswith('http'):
        _, path = re.split('://', path)
    return re.sub(r'[\W_]', '-', path)

# ! re.sub возвращает новую строку, полученную в результате замены
# ! по шаблону. Использовал регулярные выражения,
# ! https://proglib.io/p/regex-for-beginners/
# >> ru-hexlet-io-courses


def add_extension(path, ext):
    name = convert_path_name(path) + '.' + ext
    return name
# >> ru-hexlet-io-courses.html


def get_dir_name(path):
    return convert_path_name(path) + '_files'
# >> ru-hexlet-io-courses_files




def create_dir_from_web(path, url):
    dir_path = os.path.join(path, get_dir_name(url))
    try:
        os.makedirs(dir_path, exist_ok=True)
        # ! exist_ok=True - чтобы не возникало ошибок, если каталог существует
    except OSError:
        print(f'Failed to create a directory {dir_path}')
    return dir_path


def get_web_text(url, ext='html', path='page_loader/tmp'):  # use response.text
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    page_name = convert_path_name(url) + '.' + ext
    file_path = os.path.join(path, page_name)
    # domain_name = urlparse(url).scheme + "://" + urlparse(url).netloc
    with open(file_path, 'w') as file:
        file.write(response.text)
    return file_path

    # ! response.raise_for_status() нужна для того, чтобы проверить,
    # ! понял вас сервер или нет. Если сервер вернёт 404 «Ресурс не найден»,
    # ! то в response не будет странички сайта, а будет только “Ошибка 404”.
    # ! Если не вызвать raise_for_status, программа подумает, что всё в
    # !  порядке,что вы так и хотели: отправить запрос на страницу,
    # ! которой нет.
        # ! Список режимов доступа к файлу, контекстный менеджер
        # ! http://pythonicway.com/python-fileio


def get_web_content(url, ext='html', path='page_loader/tmp'):  # use response.content
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    page_name = convert_path_name(url) + '.' + ext
    file_path = os.path.join(path, page_name)
    # domain_name = urlparse(url).scheme + "://" + urlparse(url).netloc
    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path


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
    file = open(file_path, 'r')
    html = file.read()
    soup = BeautifulSoup(html, "html.parser")
    file.close
    list_tags_img_src = []
    list_tags_new_img_src = []
    tags_img = soup.find_all('img', src=True)
    for tag in tags_img:
        img_src = tag.get('src')
        suff = PurePosixPath(file).suffix
        if suff in EXTENSION_IMG:
            if domain_name in img_src:
                tag['src'] = img_src
            elif urlparse(domain_name).netloc in img_src:
                tag['src'] = urljoin(domain_name, img_src)
            img_src_new = tag['src']
            list_tags_img_src.append(img_src_new)
            tag['src'] = download_web_link(dir_path, img_src_new)
            list_tags_new_img_src.append(tag['src'])

    list_tags_href = []
    list_tags_new_href = []
    tags_link = soup.find_all('link', href=True)
    for tag in tags_link:
        href = tag.get('href')
        # if is_extension(href):
        if href.startswith(domain_name):
            continue
        else:
            tag['href'] = urljoin(domain_name, href)
        href_new = tag['href']
        list_tags_href.append(href_new)
        tag['href'] = download_web_link(dir_path, href_new)
        list_tags_new_href.append(tag['href'])

    list_tags_script_src = []
    list_tags_new_script_src = []
    tags_script = soup.find_all('script', src=True)
    for tag in tags_script:
        script_src = tag.get('src')
        # if is_extension(script_src):
        if script_src.startswith(domain_name):
            continue
        else:
            tag['src'] = urljoin(domain_name, script_src)
        script_src_new = tag['src']
        list_tags_script_src.append(script_src_new)
        tag['src'] = download_web_link(dir_path, script_src_new)
        list_tags_new_script_src.append(tag['src'])

    new_html = soup.prettify(formatter='html5')
    with open(file_path, 'w') as file:
        file.write(new_html)
    return (list_tags_img_src, list_tags_new_img_src,
            list_tags_script_src, list_tags_new_script_src,
            list_tags_href, list_tags_new_href)


def download_web_link(path, url):
    response = requests.get(url, headers=HEADERS)
    # !  # download the body of response by chunk, not immediately
    response.raise_for_status()
    file_name = convert_path_name(url)
    file_path = os.path.join(path, file_name)
    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_name


def download(path, url):
    ext = 'html'
    domain_name = urlparse(url).scheme + "://" + urlparse(url).netloc
    # domain_name = urlparse(url).netloc
    if not is_valid(url):
        print('Not a valid URL')

    # path = os.path.abspath(path)
    # ! path.abspath выдает абсолютный путь
    dir_to_download = create_dir_from_web(path, url)
    web_page_path = get_web_text(url, ext, dir_to_download)
    change_src(dir_to_download, web_page_path, domain_name)
    print('Page was successfully downloaded into -> ', web_page_path) # TODO поменять web_page_path
    return dir_to_download
# >> возвращает путь: page_loader/data/ru-hexlet-io-courses_files
