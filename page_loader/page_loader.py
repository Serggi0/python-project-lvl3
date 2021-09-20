from page_loader.web_data_processing import (edit_tags_with_relativ_link)
from page_loader.normalize_data import create_dir_for_links


def download(url, path):
    dir_for_links = create_dir_for_links(path, url)
    result = edit_tags_with_relativ_link(dir_for_links, path, url)
    return result
