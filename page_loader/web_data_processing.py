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


def get_response_server(url):
    try:
        requests.get(url).raise_for_status()
        response = requests.get(url)
        assert type(response) is not None
        # ! https://www.rupython.com/63038-63038.html
        return response
    except(
        requests.exceptions.ConnectionError,
        requests.exceptions.HTTPError,
        requests.exceptions.MissingSchema,
        requests.exceptions.InvalidSchema
    ) as error:
        logger.exception(error)
        raise Error(f'{RED}Error occurred:\n{WHITE}'
                    f'{error.__class__.__name__}: {error}') from error


def load_link(dir_to_download, url, flag=None):
    try:
        response = get_response_server(url)
        file_name = get_file_name(url, flag)
        file_path = Path(dir_to_download) / file_name

        if response or response is not None:
            with open(file_path, 'wb') as file:
                file.write(response.content)
                logger.debug(f'Function download link {url}, create file: '
                             f'{file_name} and return path: {file_path}')
                return str(file_path)
        else:
            logger.debug('No response or is None')

    except FileNotFoundError as error:
        logger.exception(error)
        raise Error(f'{RED}Directory {dir_to_download} not exists:\n{WHITE}'
                    f'{error.__class__.__name__}: {error}') from error


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


def edit_tags_with_relativ_link(dir_to_download, web_page,
                                tags_name: list, attr_tags: list, url):
    domain_name = get_domain_name(url)
    with open(web_page) as fp:
        soup = BeautifulSoup(fp, "html.parser")

    for link in soup.find_all(tags_name):
        for attribute in attr_tags:
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
    visualize_loading(len(attr_tags))
    new_html = soup.prettify()
    Path(web_page).write_text(new_html)
    logger.debug(f'New tags are written to the file {web_page}')

    return web_page
