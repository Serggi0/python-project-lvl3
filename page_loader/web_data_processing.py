import os
import os.path
import requests
import logging.config
from urllib.parse import urlparse
from progress.bar import Bar
from bs4 import BeautifulSoup
from time import sleep
from page_loader.custom_exseptions import Error
from page_loader.settings_logging import logger_config
from page_loader.normalize_data import (get_file_name, convert_relativ_link,
                                        get_path_for_tags, is_valid)
from page_loader.colors import RED, WHITE


logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')
logger_for_console = logging.getLogger('logger_for_console')

CHUNK_SIZE = 1024


def check_url(url):
    try:
        requests.get(url).raise_for_status()
        return url
    except(
        requests.exceptions.ConnectionError,
        requests.exceptions.HTTPError,
        requests.exceptions.MissingSchema,
        requests.exceptions.InvalidSchema
    ) as error:
        logger.exception(error)
        raise Error(f'{RED}Error occurred:\n{WHITE}'
                    '{error.__class__.__name__}: {error}') from error


def get_response_server(url):
    check_url(url)
    logger.debug(f'Request to {url}')
    response = requests.get(url)
    logger.debug((response.status_code, url))
    return response


def load_web_page(path, url):
    response = get_response_server(url)
    assert type(response) is not None
    # ! https://www.rupython.com/63038-63038.html
    file_name = get_file_name(url)
    file_path = os.path.join(path, file_name)
    bar = Bar(f'Download {file_name}', suffix='%(percent)d%%', color='blue')

    with open(file_path, 'wb') as file:
        file.write(response.content)
        for data in bar.iter(response.iter_content(chunk_size=CHUNK_SIZE)):
            bar.next
            sleep(0.0001)
        bar.finish()
        logger.debug(f'Function download web-page and return'
                     f' {file_name} and {file_path}')
    return file_path


def get_link(dir_to_download, url):
    response = get_response_server(url)
    assert type(response) is not None
    # ! https://www.rupython.com/63038-63038.html
    file_name = get_file_name(url, flag='link')
    file_path = os.path.join(dir_to_download, file_name)

    with open(file_path, 'wb') as file:
        if response or response is not None:
            file.write(response.content)
            logger.debug(f'Function added content and return'
                         f' {file_name} and {file_path}')
        else:
            logger.debug('No response or is None')
    return file_path


def get_domain_name(url):
    parsed = urlparse(url)
    if parsed.scheme:
        domain_name = parsed.scheme + '://' + parsed.netloc
        return domain_name
    else:
        if parsed.netloc:
            domain_name = 'http://' + parsed.netloc
            return domain_name
        else:
            return None


def get_soup(file_path):
    with open(file_path) as f:
        data = f.read()
        soup = BeautifulSoup(data, "html.parser")
    logger.debug(f'From {file_path} create object BeautifulSoup')
    return soup


def get_page_with_local_links(dir_to_download, web_page, url):
    cnt = 0
    domain_name = get_domain_name(url)
    soup = get_soup(web_page)
    tags = soup.find_all(['img', 'script', 'link'])

    for tag in tags:
        href = tag.attrs.get('href')
        # if hasattr(tag, 'href'):
        #     href = getattr(tag, 'href')
        src = tag.attrs.get('src')

        if href:
            if href == '' or href is None:
                continue
            else:
                link_href = convert_relativ_link(href, domain_name)
                if link_href.startswith(domain_name) and is_valid(link_href):
                    tag['href'] = link_href
                    path_for_link = get_link(dir_to_download, link_href)
                    tag['href'] = get_path_for_tags(path_for_link)
                    cnt += 1
                    logger.debug('Download href')
                else:
                    continue
        elif src:
            if src == '' or src is None:
                continue
            else:
                link_src = convert_relativ_link(src, domain_name)
                if link_src.startswith(domain_name) and is_valid(link_src):
                    tag['src'] = link_src
                    path_for_link = get_link(dir_to_download, link_src)
                    tag['src'] = get_path_for_tags(path_for_link)
                    cnt += 1
                    logger.debug('Download src')
                else:
                    continue

    logger.debug(f'Total tags changed: {cnt}')
    if cnt == 0:
        logger.debug(f'Tags not found in {web_page}')

    new_html = soup.prettify(formatter='html5')
    with open(web_page, 'w') as file:
        file.write(new_html)
    logger.debug('New tags are written to the file, change_tags finished')
    print()
    return web_page
