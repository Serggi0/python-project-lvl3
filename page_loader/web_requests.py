import os
import os.path
import requests
import logging.config
from progress.bar import Bar
from time import sleep
from page_loader.settings_logging import logger_config
from page_loader.normalize_data import check_url, get_file_name


logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')
logger_for_console = logging.getLogger('logger_for_console')

# HEADERS = {
#     'user-agent':
#         'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
#         'AppleWebKit/537.36 (KHTML, like Gecko)'
#         'Chrome/91.0.4472.101 Safari/537.36'
# }
CHUNK_SIZE = 1024


def get_response_server(url):
    # try:
    check_url(url)
    logger.debug(f'Request to {url}')
    response = requests.get(url)
    # response.raise_for_status()
    logger.debug((response.status_code, url))
    return response

    # except(
    #        requests.exceptions.ConnectionError,
    #        requests.exceptions.HTTPError,
    #        requests.exceptions.MissingSchema,
    #        requests.exceptions.InvalidSchema,
    #        requests.exceptions.Timeout,
    #        ConnectionAbortedError
    # ) as error:
    #     logger.exception(error)
    #     print(f'! Error occurred:\n{error}')
    #     raise

    # else:


def write_web_content(path, dir_to_download, url, flag):
    response = get_response_server(url)
    assert type(response) is not None
    # ! https://www.rupython.com/63038-63038.html
    file_name = get_file_name(url, flag)
    bar = Bar(f'Write {file_name}', suffix='%(percent)d%%', color='blue')

    if flag == 'web_page':
        file_path = os.path.join(path, file_name)
    else:
        file_path = os.path.join(dir_to_download, file_name)

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
    return file_path
