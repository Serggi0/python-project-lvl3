from pathlib import Path
import requests
import logging.config
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from page_loader.custom_exseptions import Error
from progress.bar import Bar
from page_loader.settings_logging import logger_config
from page_loader.normalize_data import (convert_relativ_link,
                                        get_path_for_tags,
                                        get_name_link, get_name_page)


logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')

CHUNK_SIZE = 1024
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
        raise Error(f'Error occurred:\n'
                    f'{error.__class__.__name__}: {error}') from error


def load_link(dir_to_download, url):
    response = get_response_server(url)
    file_name = get_name_link(url)
    file_path = Path(dir_to_download) / file_name

    if response or response is not None:
        try:
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=10000):
                    file.write(chunk)
                logger.debug(f'Function download link {url}, create file: '
                             f'{file_name} and return path: {file_path}')
                return str(file_path)
        except OSError as error:
            logger.exception(error)
            raise Error(f'Error occurred:\n'
                        f'{error.__class__.__name__}: {error}') from error
    else:
        logger.debug('No response or is None')


def get_domain_name(url):
    parsed = urlparse(url)
    if parsed.scheme or parsed.netloc:
        domain_name = parsed.netloc
        return domain_name
    else:
        return None


def check_domain_name(url, domain_name):
    url_netlock = get_domain_name(url)
    if url_netlock == domain_name:
        return True
    else:
        return False


def get_soup(url):
    bar = Bar('Download ...',
              max=20, suffix='%(percent)d%%', color='blue')
    for i in range(20):
        html_doc = get_response_server(url).text
        bar.next()
    bar.finish()
    soup = BeautifulSoup(html_doc, "html.parser")
    return soup


def edit_tags_with_relativ_link(dir_to_download, path, url):
    domain_name = get_domain_name(url)
    soup = get_soup(url)

    for k, v in TAGS.items():
        for link in soup.find_all({k: v}):
            for attribute in ATTR_TAGS:
                url_tag = link.attrs.get(attribute)

                if url_tag == '' or url_tag is None:
                    continue
                else:
                    url_tag = convert_relativ_link(url_tag, domain_name)

                    if check_domain_name(url_tag, domain_name):
                        saved_link = load_link(dir_to_download, url_tag)
                        link[attribute] = get_path_for_tags(saved_link)
                        logger.debug(f'Change attribute tag {attribute} '
                                     f'to {url_tag}')
                    else:
                        continue
            else:
                logger.debug(f'{attribute} not found in {url}')
    new_html = soup.prettify()
    web_page = Path(path) / get_name_page(url)
    Path(web_page).write_text(new_html)
    logger.debug(f'New tags are written to the file {web_page}')

    return web_page
