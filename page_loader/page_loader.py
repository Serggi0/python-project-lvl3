from page_loader.web_data_processing import (load_web_page,
                                             get_page_with_local_links)
from page_loader.normalize_data import create_dir_for_links


def download(url, path):
    web_page = load_web_page(path, url)
    dir_for_links = create_dir_for_links(path, url)
    result = get_page_with_local_links(dir_for_links, web_page, url)
    return result
