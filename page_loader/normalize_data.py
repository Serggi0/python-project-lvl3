import sys
import os
import os.path
import re
import logging.config
from pathlib import PurePosixPath
from urllib.parse import urljoin, urlparse, urlunparse
from page_loader.settings_logging import logger_config


logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')
logger_for_console = logging.getLogger('logger_for_console')


def is_extension(file):
    suff = PurePosixPath(file).suffix
    return bool(suff)


def convert_relativ_link(link, domain_name):
    if link.startswith('//', 0, 2):
        if urlparse(link).netloc == urlparse(domain_name).netloc:
            return urljoin(domain_name, link)
        return link
    elif not link:
        return
    else:
        return urljoin(domain_name, link)


def convert_path_name(path):
    if path.startswith('http'):
        _, path = re.split('://', path)
    return re.sub(r'[\W_]', '-', path)


def get_dir_name(path):
    res = convert_path_name(path) + '_files'
    return res


def get_file_name(path, flag):
    if is_extension(path):
        if flag == 'link':
            part, suff = os.path.splitext(path)
            name = convert_path_name(part) + suff
            logger.debug('Extension is available')
        else:
            name = convert_path_name(path) + '.html'
            logger.debug('Added extension HTML')
    else:
        name = convert_path_name(path) + '.html'
        logger.debug('Added extension HTML')
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


def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc)


def normalize_url(url):
    if is_valid(url):
        parsed = urlparse(url)
        url_parts = list(parsed)
        if parsed.scheme:
            return url
        else:
            if parsed.netloc:
                url_parts = list(parsed._replace(scheme='http'))
                url = urlunparse(url_parts)
                return url
    print('Not a valid URL')
    sys.exit(1)
