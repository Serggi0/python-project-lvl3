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
    page = open(web_page, 'r', encoding='utf-8')
    data = page.read()
    soup = BeautifulSoup(data, "html.parser")
    tags = soup.find_all(tags_name)

    for tag in tags:
        for attribute in attr_tags:
            adrs_tag = tag.attrs.get(attribute)

            if adrs_tag:
                if adrs_tag == '' or adrs_tag is None:
                    continue
                else:
                    adrs_tag = convert_relativ_link(adrs_tag, domain_name)

                    if adrs_tag.startswith(domain_name) and is_valid(adrs_tag):
                        saved_link = load_link(dir_to_download,
                                               adrs_tag, flag='link')
                        tag[attribute] = get_path_for_tags(saved_link)
                        logger.debug(f'Change attribute tag {attribute} '
                                     f'to {adrs_tag}')
                    else:
                        continue
        else:
            logger.debug(f'{attribute} not found in {web_page}')
    page.close()
    visualize_loading(len(tags))

    new_html = soup.prettify(formatter='minimal')
    Path(web_page).write_text(str(new_html))
    # with open(web_page, 'w') as file:
    #     file.write(str(new_html))
    logger.debug(f'New tags are written to the file {web_page}')

    return web_page
