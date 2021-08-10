#!/usr/bin/env python
import logging.config
from page_loader.page_loader import download
from page_loader.cli import create_parser
from page_loader.settings_logging import logger_config


logging.config.dictConfig(logger_config)


def main():
    logger = logging.getLogger('app_logger')
    my_parser = create_parser()
    args = my_parser.parse_args()
    result = download(args.output, args.site)
    print('Page was successfully downloaded into -> ', result, end='\n\n')
    logger.debug('Finished')


if __name__ == '__main__':
    main()
