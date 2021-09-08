from page_loader.web_data_processing import (check_url, load_web_page,
                                             get_page_with_local_links)
from page_loader.normalize_data import create_dir_for_links


def download(url, path):
    # try:
    # os.stat(path)  # checking if folder exist
    # https://github.com/python/cpython/blob/main/Lib/genericpath.py
    check_url(url)
    web_page = load_web_page(path, url)
    dir_for_links = create_dir_for_links(path, url)
    # get_link(dir_for_links, url)
    result = get_page_with_local_links(dir_for_links, web_page, url)
    return result
    # except OSError as err:
    #     raise Error(f'{RED}Directory not exists:\n{WHITE}'
    #                 '{err.__class__.__name__}: {err}') from err
