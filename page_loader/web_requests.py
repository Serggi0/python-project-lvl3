import sys
import os
import os.path
import requests
import logging.config
from progress.bar import Bar
from time import sleep
from page_loader.settings_logging import logger_config
from page_loader.normalize_data import get_file_name


logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')
logger_for_console = logging.getLogger('logger_for_console')


CHUNK_SIZE = 1024


def get_response_server(url):
    try:
        logger.debug(f'Request to {url}')
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        logger.debug((response.status_code, url))
        if response.ok and response is not None:
            print(f'{url}:  OK')
        else:
            raise TypeError
    except(
           requests.exceptions.ConnectionError,
           requests.exceptions.HTTPError,
           requests.exceptions.MissingSchema,
           requests.exceptions.Timeout,
           ConnectionAbortedError
    ) as error:
        logger.exception(error)
        sys.exit(f'Error occurred:\n{error}')

    else:
        return response


def write_web_content(dir_to_download, url, flag):
    assert type(url) is not None
    # ! https://www.rupython.com/63038-63038.html
    file_name = get_file_name(url, flag)
    file_path = os.path.join(dir_to_download, file_name)
    response = get_response_server(url)
    bar = Bar(f'Write {file_name}', suffix='%(percent)d%%', color='blue')
    with open(file_path, 'wb') as file:
        if response or response is not None:
            file.write(response.content)
            for data in bar.iter(response.
                                 iter_content(chunk_size=CHUNK_SIZE)):
                bar.next
                sleep(0.0001)
            bar.finish()
            logger.debug(f'Function added content and return'
                         f' {file_name} and {file_path}')
        else:
            logger.debug('No response or is None')
    return file_name, file_path
