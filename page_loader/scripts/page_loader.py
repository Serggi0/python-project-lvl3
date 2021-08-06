#!/usr/bin/env python
import logging.config
from page_loader.loader import download
from page_loader.cli import create_parser
from page_loader.settings_logging import logger_config


logging.config.dictConfig(logger_config)
# ! загрузка конфигурации из settings_logging


def main():
    logger = logging.getLogger('app_logger')
    my_parser = create_parser()
    args = my_parser.parse_args()
    # ! создал объект args для оперирования аргументами командной строки
    result = download(args.output, args.site)
    print('Page was successfully downloaded into -> ', result, end='\n\n')
    logger.debug('Finished')


if __name__ == '__main__':
    main()
