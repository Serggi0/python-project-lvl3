import os
import os.path
import re
import logging.config
from pathlib import Path, PurePosixPath
from urllib.parse import urljoin, urlparse
from page_loader.settings_logging import logger_config


logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')
logger_for_console = logging.getLogger('logger_for_console')


def is_extension(file):
    suff = PurePosixPath(file).suffix
    return bool(suff)


def prepare_url_b(url):
    if isinstance(url, bytes):
        url = url.decode('utf8')
    else:
        url = str(url)
    return url


def convert_relativ_link(link, domain_name):
    link = prepare_url_b(link)

    if link == '' or link is None:
        raise TypeError

    elif link.startswith('//', 0, 2):
        if urlparse(link).netloc == urlparse(domain_name).netloc:
            return urljoin(domain_name, link)
        return link

    elif link.startswith(domain_name):
        return link

    else:
        return urljoin(domain_name, link)


def convert_path_name(path):
    if path.startswith('http'):
        _, path = re.split('://', path)
    if path.endswith('/'):
        path = path[:-1]
    return re.sub(r'[\W_]', '-', path)


def get_dir_name(path):
    res = convert_path_name(path) + '_files'
    return res


def get_file_name(path, flag):
    if is_extension(path):
        if flag == 'link':
            part, suff = os.path.splitext(path)
            try:
                position = suff.index('?')
                suff = suff[:position]
            except ValueError:
                pass
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


def create_dir_for_links(path, url):
    url = prepare_url_b(url)
    if os.path.exists(path):
        dir_name = get_dir_name(url)
        dir_path = os.path.join(path, dir_name)
        os.makedirs(dir_path)
        logger.debug(f'Function create_dir_for_links '
                     f'return {dir_path}')
        return dir_path
    else:
        raise Exception('Directory not found')


def get_path_for_tags(path):
    parts = Path(path).parts
    return Path(parts[-2]) / parts[-1]


def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.scheme) and bool(parsed.netloc)


def get_domain_name(url):
    url = prepare_url_b(url)
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
