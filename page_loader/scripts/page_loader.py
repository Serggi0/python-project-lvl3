#!/usr/bin/env python

import sys
import requests
import logging.config
from page_loader.page_loader import download
from page_loader.cli import create_parser
from page_loader.normalize_data import is_valid
from page_loader.settings_logging import logger_config


logging.config.dictConfig(logger_config)


def main():
    logger = logging.getLogger('app_logger')
    my_parser = create_parser()
    args = my_parser.parse_args()
    try:
        if is_valid(args.url):
            result = download(args.output, args.url)
            print('Page was successfully downloaded into -> ',
                  result, end='\n\n')
        print(f'Not a valid URL: {args.url}')
    except AttributeError:
        logger.exception('AttributeError')
        sys.exit('Unable to get content')
    except requests.exceptions.ConnectionError:
        logger.exception('Connection error occurred')
        sys.exit('Connection error occurred')
    except requests.exceptions.HTTPError:
        logger.exception('HTTP Error occured')
        sys.exit('HTTP Error occured')
    except PermissionError:
        sys.exit('Permission denied')
    except ConnectionAbortedError:
        sys.exit('Connection was aborted')
    except FileNotFoundError:
        sys.exit('File not found')
    except FileExistsError:
        sys.exit('Attempt to create a file or directory that already exists')
    except Exception as error:
        logger.exception(error)
        sys.exit(1)
    else:
        logger.debug('Finished')
        sys.exit(0)


if __name__ == '__main__':
    main()
