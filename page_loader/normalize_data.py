import os
import os.path
from page_loader.custom_exseptions import Error
import re
import logging.config
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse
from page_loader.settings_logging import logger_config


logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')


def is_extension(file):
    suff = PurePosixPath(file).suffix
    return bool(suff)


def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.scheme) and bool(parsed.netloc)


def convert_relativ_link(link, domain_name, url):
    parsed = urlparse(url)
    if urlparse(link).netloc == domain_name:
        if link.startswith('//', 0, 2):
            link = '{}{}{}'.format(parsed.scheme, ':', link)
        else:
            link = link

    else:
        if re.match(r'/\w', link):
            link = '{}{}{}{}'.format(parsed.scheme, '://', domain_name, link)

        elif link == '' or link is None:
            raise TypeError from None
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
    except FileExistsError as err:
        raise Error(f'Directory exists:\n'
                    f'{err.__class__.__name__}: {err}') from err
    except FileNotFoundError as error:
        raise Error(f'Directory or file not found:\n'
                    f'{error.__class__.__name__}: {error}') from error


def get_path_for_tags(path):
    parts = Path(path).parts
    path = Path(parts[-2]) / parts[-1]
    logger.debug(f'parts: {parts}, return path: {str(path)} ')
    return str(path)
