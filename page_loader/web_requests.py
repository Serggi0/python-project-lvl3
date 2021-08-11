import sys
import os
import os.path
import requests
import logging.config
from progress.bar import Bar
from time import sleep
from page_loader.settings_logging import logger_config
from page_loader.pathes import get_file_name


logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')
logger_for_console = logging.getLogger('logger_for_console')


CHUNK_SIZE = 1024


def get_response_server(url):
    logger.debug(f'Request to {url}')
    try:
        response = requests.get(url, stream=True)
        logger.debug((response.status_code, url))
        if response.ok:
            print(f'{url}:  OK')
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as http_error:
        logger.exception('HTTP Error occured')
        print(f'HTTP error occurred: {http_error}')
    except Exception as error:
        logger.exception('Other error occurred')
        print(f'Other error occurred: {error}')


def write_web_content(dir_to_download, url, ext='html'):
    response = get_response_server(url)
    file_name = get_file_name(url, ext)
    file_path = os.path.join(dir_to_download, file_name)
    bar = Bar(f'Write {file_name}', suffix='%(percent)d%%', color='blue')
    try:
        with open(file_path, 'wb') as file:
            file.write(response.content)
            for data in bar.iter(response.iter_content(chunk_size=CHUNK_SIZE)):
                bar.next
                sleep(0.0001)
            bar.finish()
        logger.debug(f'Function added content and return'
                     f' {file_name} and {file_path}')
        return file_name, file_path
    except OSError:
        logger.exception(f'Failed to write content in {file_name}')
        sys.exit(f'Failed to write content in {file_name}')