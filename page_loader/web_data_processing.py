from pathlib import Path
import requests
import logging.config
from bs4 import BeautifulSoup
from page_loader.custom_exseptions import BadConnect, ErrorSistem
from progress.bar import Bar
from page_loader.settings_logging import logger_config
from page_loader.normalize_data import (get_parts_url, convert_relativ_link,
                                        get_path_for_tags, get_name_link,
                                        get_name_page, check_domain_name)


logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')

ATTR_TAGS = ['href', 'src']
TAGS = {
    'script': 'src',
    'link': 'href',
    'img': 'src'
}


def get_response_server(url):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        # assert type(response) is not None
        # # ! https://www.rupython.com/63038-63038.html
        return response
    except requests.RequestException as error:
        logger.exception(error)
        raise BadConnect(f'Error occurred:\n'
                         f'{error.__class__.__name__}: {error}') from error


def get_soup(url):
    html_doc = get_response_server(url).text
    soup = BeautifulSoup(html_doc, "html.parser")
    return soup


def edit_tags_with_relativ_link(dir_to_download, url, soup):
    domain_name = get_parts_url(url)
    links_to_load = {}

    for k, v in TAGS.items():
        for link in soup.find_all({k: v}):
            for attribute in ATTR_TAGS:
                url_tag = link.attrs.get(attribute)

                if url_tag == '' or url_tag is None:
                    continue
                else:
                    url_tag = convert_relativ_link(url_tag, url)

                    if check_domain_name(url_tag, domain_name):
                        link_path = str(
                            Path(dir_to_download) / get_name_link(url_tag)
                        )
                        link[attribute] = link_path
                        links_to_load[url_tag] = link[attribute]
                        # long path to save to the dictionary links_to_load
                        link[attribute] = get_path_for_tags(link_path)
                        # short path to save to the soup
                        logger.debug(f'Change attribute tag {attribute} '
                                     f'to {url_tag}')
                    else:
                        continue
            else:
                logger.debug(f'{attribute} not found in {url}')
    return soup, links_to_load


def load_link_in_local_dir(links_to_load):
    for link, path_for_link in links_to_load.items():
        bar = Bar(f'Download {link}...', suffix='%(percent)d%%', color='blue')
        response = get_response_server(link)
        if response or response is not None:
            try:
                with open(path_for_link, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=10000):
                        file.write(chunk)
                        file.flush()  # Cброс данных из буфера в файл
                        bar.next()
                bar.finish()
                logger.debug(f'Download link {link}')
            except OSError as error:
                logger.exception(error)
                raise ErrorSistem(f'Error occurred:\n'
                                  f'{error.__class__.__name__}:'
                                  f'{error}') from error
        else:
            logger.debug('No response or is None')
    logger.debug('Links saved in local directory')


def save_content(dir_for_links, url, soup):
    soup, links_to_load = edit_tags_with_relativ_link(dir_for_links, url, soup)

    new_html = soup.prettify()
    web_page = Path(dir_for_links.parent) / get_name_page(url)

    try:
        Path(web_page).write_text(new_html)
    except OSError as error:
        logger.exception(error)
        raise ErrorSistem(f'Error occurred:\n'
                          f'{error.__class__.__name__}: {error}') from error

    load_link_in_local_dir(links_to_load)

    return str(web_page)
