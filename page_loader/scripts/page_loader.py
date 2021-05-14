#!/usr/bin/env python
from page_loader.loader import download


def main():
    download('https://httpbin.org')


if __name__ == '__main__':
    main()
