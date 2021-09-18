import os
import os.path
from page_loader.custom_exseptions import Error
import re
import logging.config
from progress.bar import Bar
from pathlib import Path, PurePosixPath
from urllib.parse import urljoin, urlparse
from page_loader.settings_logging import logger_config
from page_loader.colors import RED, WHITE


logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')


def is_extension(file):
    suff = PurePosixPath(file).suffix
    return bool(suff)


def convert_relativ_link(link, domain_name):
    if link == '' or link is None:
        raise TypeError from None

    elif link.startswith('//', 0, 2):
        if urlparse(link).netloc == urlparse(domain_name).netloc:
            return urljoin(domain_name, link)
        return link

    elif link.startswith(domain_name):
        return link

    else:
        return urljoin(domain_name, link)


def convert_path_name(path):
    path = str(path)
    if path.startswith('http'):
        _, path = re.split('://', path)
    if path.endswith('/'):
        path = path[:-1]
    return re.sub(r'[\W_]', '-', path)


def get_file_name(path, flag=None):
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
    logger.debug(f'Function return name: {name}')
    return name


def create_dir_for_links(path, url):
    dir_name = convert_path_name(url) + '_files'
    dir_path = Path(path) / dir_name
    try:
        Path(dir_path).mkdir()
        logger.debug(f'Function return {dir_path}')
        return dir_path
    except FileExistsError as err:
        raise Error(f'{RED}Directory exists:\n{WHITE}'
                    f'{err.__class__.__name__}: {err}') from err
    except FileNotFoundError as error:
        raise Error(f'{RED}Directory or file not found:\n{WHITE}'
                    f'{error.__class__.__name__}: {error}') from error


def get_path_for_tags(path):
    parts = Path(path).parts
    path = Path(parts[-2]) / parts[-1]
    logger.debug(f'parts: {parts}, return path: {str(path)} ')
    return path


def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.scheme) and bool(parsed.netloc)


def visualize_loading(number):
    bar = Bar('Download ...',
              max=number, suffix='%(percent)d%%', color='blue')
    for i in range(number):
        bar.next()
    bar.finish()
