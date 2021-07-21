import os
import os.path
import requests
import re
import logging.config
from pathlib import PurePosixPath
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from page_loader.settings_logging import logger_config


# ! чтобы сайт не идентифицировал как бота
HEADERS = {
    'user-agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        'AppleWebKit/537.36 (KHTML, like Gecko)'
        'Chrome/91.0.4472.101 Safari/537.36'
}


logging.config.dictConfig(logger_config)  # загрузка словаря
logger = logging.getLogger('app_logger')  # получение логгера


def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)
# ! Проверка url-адресов, является ли переданный URL-адрес действительным


def is_extension(file):
    suff = PurePosixPath(file).suffix
    return bool(suff)


def convert_relativ_link(link, domain_name):
    if link.startswith('//', 0, 2):
        return link
    else:
        return urljoin(domain_name, link)
# конвертирует относительную ссылку на локальные ресурсы в абсолютную
# converts a relative reference to local resources to an absolute one


# def add_extension(path, ext):
#     name = convert_path_name(path) + '.' + ext
#     return name
# # >> ru-hexlet-io-courses.html


def convert_path_name(path):
    if path.startswith('http'):
        _, path = re.split('://', path)
    return re.sub(r'[\W_]', '-', path)
# ! re.sub возвращает новую строку, полученную в результате замены
# ! по шаблону. Использовал регулярные выражения,
# ! https://proglib.io/p/regex-for-beginners/
# >> ru-hexlet-io-courses


def get_dir_name(path):
    res = convert_path_name(path) + '_files'
    return res
# >> ru-hexlet-io-courses_files


def get_web_page_name(url, ext):
    if is_extension(url):
        part, suff = os.path.splitext(url)
        if suff == 'html':
            name = convert_path_name(part) + suff
        else:
            name = convert_path_name(url) + '.html'
        logger.debug('Extension is available')
    else:
        name = convert_path_name(url) + '.' + ext
        logger.debug('Added extension')
    logger.debug(f'Function return {name}')
    return name


def get_file_name(path, ext):
    if is_extension(path):
        part, suff = os.path.splitext(path)
        name = convert_path_name(part) + suff
        logger.debug('Extension is available')
    else:
        name = convert_path_name(path) + '.' + ext
        logger.debug('Added extension')
    logger.debug(f'Function return {name}')
    return name


def create_dir_from_web(path, url):
    dir_path = os.path.join(path, get_dir_name(url))
    try:
        os.makedirs(dir_path, exist_ok=True)
        # ! exist_ok=True - чтобы не возникало ошибок, если каталог существует
    except OSError:
        logger.exception(f'Failed to create a directory {dir_path}')
        # ! logger.exception или logger.debug(exc_info=True)
        # ! добавляет в лог Traceback - полное сообщение об ошибке
        # ! .exception автоматически включает уровень ERROR
    logger.debug(f'Function create_dir_from_web(path, url) return {dir_path}')
    return dir_path


def get_web_content(url, ext='html', path='page_loader/tmp'):
    # use response.content
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    # dir_path = create_dir_from_web(path, url)
    page_name = get_web_page_name(url, 'html')

    file_path = os.path.join(path, page_name)
    logger.debug(f'Function create {file_path}')
    # domain_name = urlparse(url).scheme + "://" + urlparse(url).netloc
    with open(file_path, 'wb') as file:
        file.write(response.content)
    logger.debug(f'Function added content in {file_path}')
    return file_path
    # ! response.raise_for_status() нужна для того, чтобы проверить,
    # ! понял вас сервер или нет. Если сервер вернёт 404 «Ресурс не найден»,
    # ! то в response не будет странички сайта, а будет только “Ошибка 404”.
    # ! Если не вызвать raise_for_status, программа подумает, что всё в
    # !  порядке,что вы так и хотели: отправить запрос на страницу,
    # ! которой нет.
    # ! Список режимов доступа к файлу, контекстный менеджер
    # ! http://pythonicway.com/python-fileio


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


def get_soup(file_path):
    with open(file_path) as f:
        data = f.read()
        soup = BeautifulSoup(data, "html.parser")
    logger.debug(f'From {file_path} create object BeautifulSoup')
    return soup


def download_web_link(dir_to_download, url, domain_name, ext='html'):
    if url.startswith(domain_name):
        response = requests.get(url, headers=HEADERS)
        # !  # download the body of response by chunk, not immediately
        response.raise_for_status()
        file_name = get_file_name(url, ext)
        file_path = os.path.join(dir_to_download, file_name)
        with open(file_path, 'wb') as file:
            file.write(response.content)
    logger.debug(f'Function return {file_name} and {file_path}')
    return file_name, file_path


def change_tags(dir_to_download, file_with_content, domain_name):
    dict_tags = {}
    list_tags = []
    soup = get_soup(file_with_content)

    tags_img = soup.find_all('img', src=True)
    tags_script = soup.find_all('script', src=True)
    tags_link = soup.find_all('link', href=True)

    for tag in tags_img:
        img_src = tag['src']
        list_tags.append(img_src)
        logger.debug(f'{img_src} added to list "list_tags"')
    for tag in tags_script:
        script_src = tag['src']
        list_tags.append(script_src)
        logger.debug(f'{script_src} added to list "list_tags"')
    for tag in tags_link:
        link_href = tag['href']
        list_tags.append(link_href)
        logger.debug(f'{link_href} added to list "list_tags"')
    cnt = len(list_tags)
    logger.debug(f'Total tags added: {cnt}')
    for i in list_tags:
        dict_tags[i] = convert_relativ_link(i, domain_name)
        logger.debug('Converted relativ link')

    for k, v in dict_tags.items():
        if v.startswith(domain_name):
            dict_tags[k] = download_web_link(dir_to_download, v, domain_name)
            logger.debug('Download ')
        else:
            logger.debug(f'{v} not in domain_name')

    for tag in tags_img:
        if tag['src'] in dict_tags.keys():
            tag['src'] = dict_tags[tag['src']]
            logger.debug('Change tag img_src')

    for tag in tags_script:
        if tag['src'] in dict_tags.keys():
            tag['src'] = dict_tags[tag['src']]
            logger.debug('Change tag script_src')

    for tag in tags_link:
        if tag['href'] in dict_tags.keys():
            tag['href'] = dict_tags[tag['href']]
            logger.debug('Change tag link_href')

    new_html = soup.prettify(formatter='html5')
    with open(file_with_content, 'w') as file:
        file.write(new_html)
    logger.debug('New tags are written to the file, change_tags finished')
    return file_with_content


def download(path, url):
    ext = 'html'
    domain_name = urlparse(url).scheme + "://" + urlparse(url).netloc
    # domain_name = urlparse(url).netloc
    if not is_valid(url):
        print('Not a valid URL')

    # path = os.path.abspath(path)
    # ! path.abspath выдает абсолютный путь
    dir_to_download = create_dir_from_web(path, url)
    web_page_path = get_web_content(url, ext, dir_to_download)
    change_tags(dir_to_download, web_page_path, domain_name)
    print('Page was successfully downloaded into -> ', web_page_path)
    return dir_to_download
# >> возвращает путь: page_loader/data/ru-hexlet-io-courses_files
