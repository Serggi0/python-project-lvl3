from page_loader.web_data_processing import (edit_tags_with_relativ_link,
                                             load_link)
from page_loader.normalize_data import create_dir_for_links


def download(url, path):
    web_page = load_link(path, url)
    dir_for_links = create_dir_for_links(path, url)
    result = edit_tags_with_relativ_link(dir_for_links, web_page, url)
    return result
