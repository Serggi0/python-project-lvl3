import sys
import os
import os.path
import requests
import re
import logging.config
from pathlib import PurePosixPath
from bs4 import BeautifulSoup
from tqdm import tqdm
from progress.bar import Bar
from progress.spinner import MoonSpinner
from time import sleep
from urllib.parse import urljoin, urlparse
from page_loader.settings_logging import logger_config
from page_loader.response_status_codes import response_codes


logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')
logger_for_console = logging.getLogger('logger_for_console')


def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def is_extension(file):
    suff = PurePosixPath(file).suffix
    return bool(suff)


def get_response_server(url):
    try:
        response = requests.get(url, stream=True)
        code = response.status_code
        for k, v in response_codes.items():
            if code == k:
                print(f'{url}: ', v)
                logger.debug((code, v, url))
                if k >= 400:
                    return v
        return response
    except AttributeError:
        logger.exception('AttributeError')
        sys.exit('Unable to get content')
    except requests.exceptions.ConnectionError:
        logger.exception('Connection error occurred')
        sys.exit('Connection error occurred')
    except requests.exceptions.HTTPError:
        logger.exception('HTTP Error occured')
        sys.exit('HTTP Error occured')


def convert_relativ_link(link, domain_name):
    if link.startswith('//', 0, 2):
        return link
    else:
        return urljoin(domain_name, link)


def convert_path_name(path):
    if path.startswith('http'):
        _, path = re.split('://', path)
    return re.sub(r'[\W_]', '-', path)


def get_dir_name(path):
    res = convert_path_name(path) + '_files'
    return res


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
        logger.debug(
            f'Function create_dir_from_web(path, url) return {dir_path}'
            )
        return dir_path
    except OSError:
        logger_for_console.exception(
            f'Failed to create a directory {dir_path}'
            )


def get_web_content(url, ext='html', path='page_loader/tmp'):
    response = get_response_server(url)
    page_name = get_web_page_name(url, 'html')
    file_path = os.path.join(path, page_name)
    try:
        with open(file_path, 'wb') as file:
            file.write(response.content)
            with MoonSpinner(f'Load {page_name}  ') as bar:
                for data in bar.iter(response.iter_content()):
                    bar.next
                    sleep(0.0001)
                bar.finish()
        logger.debug(f'Function added content in {file_path}')
        return file_path
    except OSError:
        logger.exception(f'Failed to write content in {page_name}')
        sys.exit(f'Failed to write content in {page_name}')


def get_soup(file_path):
    with open(file_path) as f:
        data = f.read()
        soup = BeautifulSoup(data, "html.parser")
    logger.debug(f'From {file_path} create object BeautifulSoup')
    return soup


def download_web_link(dir_to_download, url, ext='html'):
    response = get_response_server(url)
    file_name = get_file_name(url, ext)
    file_path = os.path.join(dir_to_download, file_name)
    bar = Bar(f'Write {file_name}', suffix='%(percent)d%%', color='blue')
    try:
        with open(file_path, 'wb') as file:
            file.write(response.content)
            for data in bar.iter(response.iter_content(1024)):
                bar.next
                sleep(0.0001)
        logger.debug(f'Function return {file_name} and {file_path}')
        return file_name, file_path
    except OSError:
        logger.exception(f'Failed to write content in {file_name}')
        sys.exit(f'Failed to write content in {file_name}')


def change_tags(dir_to_download, file_with_content, domain_name):
    cnt = 0
    soup = get_soup(file_with_content)
    tags = soup.find_all(['img', 'script', 'link'])

    for tag in tags:
        if 'src' in tag.attrs:
            link_src = convert_relativ_link(tag['src'], domain_name)
            if link_src.startswith(domain_name):
                tag['src'] = link_src
                web_link_src, _ = download_web_link(dir_to_download, link_src)
                # >> web_link_src - относительный путь из папки dir_to_download
                tag['src'] = web_link_src
                cnt += 1
                logger.debug('Download ')
            else:
                logger.debug(f'{link_src} not in domain_name or repeated')

        if 'href' in tag.attrs:
            link_href = convert_relativ_link(tag['href'], domain_name)
            if link_href.startswith(domain_name):
                tag['href'] = link_href
                web_link_href, _ = download_web_link(dir_to_download,
                                                     link_href)
                tag['href'] = web_link_href
                cnt += 1
                logger.debug('Download ')
            else:
                logger.debug(f'{link_href} not in domain_name or repeated')

    logger.debug(f'Total tags changed: {cnt}')

    if cnt == 0:
        sys.exit(f'Tags not found in {file_with_content}')

    new_html = soup.prettify(formatter='html5')
    try:
        with open(file_with_content, 'w') as file:
            file.write(new_html)
            for i in tqdm(new_html, 'File write... '):
                sleep(0.00001)
        logger.debug('New tags are written to the file, change_tags finished')
        print()
        return file_with_content
    except OSError:
        logger.exception(f'Failed to write content in {file_with_content}')
        sys.exit(f'Failed to write content in {file_with_content}')


def download(path, url):
    ext = 'html'
    domain_name = urlparse(url).scheme + "://" + urlparse(url).netloc
    if not is_valid(url):
        print('Not a valid URL')
        # sys.exit('Not a valid URL')
    dir_to_download = create_dir_from_web(path, url)
    web_page_path = get_web_content(url, ext, dir_to_download)
    result = change_tags(dir_to_download, web_page_path, domain_name)
    return result
