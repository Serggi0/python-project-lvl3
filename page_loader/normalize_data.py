import os
import os.path
from page_loader.custom_exseptions import BadFile, BadPath
import re
import logging.config
from pathlib import Path, PurePosixPath
from urllib.parse import urljoin, urlparse
from page_loader.settings_logging import logger_config
from page_loader.colors import RED, WHITE


logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')
logger_for_console = logging.getLogger('logger_for_console')


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
    if path.startswith('http'):
        _, path = re.split('://', path)
    if path.endswith('/'):
        path = path[:-1]
    return re.sub(r'[\W_]', '-', path)


def get_dir_name(path):
    res = convert_path_name(path) + '_files'
    return res


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
    logger.debug(f'Function return {name}')
    return name


def create_dir_for_links(path, url):
    try:
        dir_name = get_dir_name(url)
        dir_path = os.path.join(path, dir_name)
        os.makedirs(dir_path)
        logger.debug(f'Function create_dir_for_links '
                     f'return {dir_path}')
        return dir_path
    except OSError as err:
        raise BadPath(f'{RED}Directory exists:\n{WHITE}{err}') from err
    except FileNotFoundError as error:
        raise BadPath(f'{RED}Directory or file not found:'
                      '\n{WHITE}{error}') from error
    except FileExistsError as er:
        raise BadFile(f'{RED}File exists:'
                      '\n{WHITE}{er}') from er


def get_path_for_tags(path):
    parts = Path(path).parts
    return Path(parts[-2]) / parts[-1]


def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.scheme) and bool(parsed.netloc)
