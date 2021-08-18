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
        is_valid(args.url)
        requests.get(args.url).ok
        download(args.url, args.output)

    except(
           requests.exceptions.ConnectionError,
           requests.exceptions.HTTPError,
           requests.exceptions.MissingSchema,
           requests.exceptions.Timeout,
           ConnectionAbortedError
    ) as error:
        logger.exception(error)
        sys.exit(f'Error occurred:\n{error}')

    except AttributeError:
        sys.exit('Unable to get content')
    except PermissionError:
        sys.exit('Permission denied')
    except FileNotFoundError:
        sys.exit('File not found')
    except Exception as error:
        logger.exception(error)
        sys.exit(error)

    else:
        logger.debug('Finished')
        sys.exit(0)


if __name__ == '__main__':
    main()
