import os
import os.path
from page_loader.custom_exseptions import ErrorSistem
import re
import logging.config
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse, urljoin
from page_loader.settings_logging import logger_config


logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')


def is_extension(file):
    suff = PurePosixPath(file).suffix
    return bool(suff)


def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.scheme) and bool(parsed.netloc)


def get_parts_url(url):
    parsed = urlparse(url)
    domain_name = parsed.netloc
    return domain_name


def check_domain_name(url, domain_name):
    url_netlock = get_parts_url(url)
    if url_netlock == domain_name:
        return True
    else:
        return False


def convert_relativ_link(link, url):
    domain_name = get_parts_url(url)
    if link.startswith('http'):
        pass
    elif urlparse(link).netloc == domain_name:
        link = urljoin(url, link)
    elif re.match(r'/\w', link):
        link = urljoin(url, link)
    elif link is None:
        raise TypeError from None
    else:
        pass
    return link


def convert_path_name(path):
    path = str(path)
    if path.startswith('http'):
        _, path = re.split('://', path)
    if path.endswith('/'):
        path = path[:-1]
    return re.sub(r'[\W_]', '-', path)


def get_name_page(name):
    return convert_path_name(name) + '.html'


def get_name_link(name):
    part, suff = os.path.splitext(name)
    if not is_extension(name):
        suff = '.html'
    # removes the characters after ? (for example, "/image.png?c=3.2.5")
    try:
        position = suff.index('?')
        suff = suff[:position]
    except ValueError:
        pass

    return convert_path_name(part) + suff


def create_dir_for_links(path, url):
    try:
        dir_name = convert_path_name(url) + '_files'
        dir_path = Path(path) / dir_name
        Path(dir_path).mkdir()
        logger.debug(f'Function return {dir_path}')
        return dir_path
    except OSError as err:
        raise ErrorSistem(f'Error occurred:\n'
                          f'{err.__class__.__name__}: {err}') from err


def get_path_for_tags(path):
    parts = Path(path).parts
    path = Path(parts[-2]) / parts[-1]
    logger.debug(f'parts: {parts}, return path: {str(path)} ')
    return str(path)
