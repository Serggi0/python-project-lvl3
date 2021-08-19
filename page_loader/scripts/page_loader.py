#!/usr/bin/env python

import sys
import os
import requests
import logging.config
from page_loader.page_loader import download
from page_loader.cli import create_parser
from page_loader.settings_logging import logger_config


logging.config.dictConfig(logger_config)


def main():
    logger = logging.getLogger('app_logger')
    my_parser = create_parser()
    args = my_parser.parse_args()

    try:
        os.stat(args.output)
        # https://github.com/python/cpython/blob/
        # 286e1c15ceb28a76d8ef4fe7111718317c9ccaf5/Lib/genericpath.py#L14-L22
        requests.get(args.url).raise_for_status()
        download(args.url, args.output)

    except(
        requests.exceptions.ConnectionError,
        requests.exceptions.HTTPError,
        requests.exceptions.MissingSchema,
        requests.exceptions.InvalidSchema,
        requests.exceptions.Timeout,
        ConnectionAbortedError,
        OSError,
        Exception
    ) as error:
        logger.exception(error)
        sys.exit(f'Error occurred:\n{error}')

    except AttributeError:
        sys.exit('Unable to get content')
    except PermissionError:
        sys.exit('Permission denied')
    except FileNotFoundError:
        sys.exit('File or Directory not found')

    else:
        logger.debug('Finished')
        sys.exit(0)


if __name__ == '__main__':
    main()
