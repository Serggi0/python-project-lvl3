#!/usr/bin/env python
from page_loader.loader import download
from page_loader.cli import create_parser


def main():
    my_parser = create_parser()
    args = my_parser.parse_args()
    # ! создал объект args для оперирования аргументами командной строки
    download(args.output, args.site)


if __name__ == '__main__':
    main()
