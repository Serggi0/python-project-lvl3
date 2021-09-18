from pathlib import Path
import requests
import logging.config
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from page_loader.custom_exseptions import Error
from page_loader.settings_logging import logger_config
from page_loader.normalize_data import (get_file_name, convert_relativ_link,
                                        get_path_for_tags, is_valid,
                                        visualize_loading)
from page_loader.colors import RED, WHITE


logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')

CHUNK_SIZE = 1024
TAGS_NAME = ['img', 'script', 'link']
ATTR_TAGS = ['href', 'src']


def get_response_server(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        # assert type(response) is not None
        # # ! https://www.rupython.com/63038-63038.html
        return response
    except requests.RequestException as error:
        logger.exception(error)
        raise Error(f'{RED}Error occurred:\n{WHITE}'
                    f'{error.__class__.__name__}: {error}') from error


def load_link(dir_to_download, url, flag=None):
    response = get_response_server(url)
    file_name = get_file_name(url, flag)
    file_path = Path(dir_to_download) / file_name

    if response or response is not None:
        try:
            with open(file_path, 'wb') as file:
                file.write(response.content)
                logger.debug(f'Function download link {url}, create file: '
                             f'{file_name} and return path: {file_path}')
                return str(file_path)
        except OSError as error:
            logger.exception(error)
            raise Error(f'{RED}Error occurred:\n{WHITE}'
                        f'{error.__class__.__name__}: {error}') from error
    else:
        logger.debug('No response or is None')


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


def edit_tags_with_relativ_link(dir_to_download, web_page, url):
    domain_name = get_domain_name(url)
    with open(web_page) as fp:
        soup = BeautifulSoup(fp, "html.parser")

    for link in soup.find_all(TAGS_NAME):
        for attribute in ATTR_TAGS:
            url_tag = link.attrs.get(attribute)

            if url_tag:
                if url_tag == '' or url_tag is None:
                    continue
                else:
                    url_tag = convert_relativ_link(url_tag, domain_name)

                    if url_tag.startswith(domain_name) and is_valid(url_tag):
                        saved_link = load_link(dir_to_download,
                                               url_tag, flag='link')
                        link[attribute] = get_path_for_tags(saved_link)
                        logger.debug(f'Change attribute tag {attribute} '
                                     f'to {url_tag}')
                    else:
                        continue
        else:
            logger.debug(f'{attribute} not found in {web_page}')
    visualize_loading(len(ATTR_TAGS))
    new_html = soup.prettify()
    Path(web_page).write_text(new_html)
    logger.debug(f'New tags are written to the file {web_page}')

    return web_page
