import logging.config
from bs4 import BeautifulSoup
from tqdm import tqdm
from time import sleep
from page_loader.settings_logging import logger_config
from page_loader.web_requests import write_web_content
from page_loader.normalize_data import (convert_relativ_link,
                                        create_dir_from_web,
                                        get_domain_name)


logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')
logger_for_console = logging.getLogger('logger_for_console')


def get_soup(file_path):
    with open(file_path) as f:
        data = f.read()
        soup = BeautifulSoup(data, "html.parser")
    logger.debug(f'From {file_path} create object BeautifulSoup')
    return soup


def change_tags(dir_to_download, file_with_content, domain_name):
    cnt = 0
    soup = get_soup(file_with_content)
    tags = soup.find_all(['img', 'script', 'link'])

    for tag in tags:
        if 'src' in tag.attrs:
            link_src = convert_relativ_link(tag['src'], domain_name)
            if link_src.startswith(domain_name) and domain_name is not None:
                tag['src'] = link_src
                web_link_src, _ = write_web_content(dir_to_download,
                                                    link_src, flag='link')
                # >> web_link_src - относительный путь из папки dir_to_download
                tag['src'] = web_link_src
                cnt += 1
                logger.debug('Download ')
            else:
                logger.debug(f'{link_src} not in domain_name or repeated')

        if 'href' in tag.attrs:
            link_href = convert_relativ_link(tag['href'], domain_name)
            if link_href.startswith(domain_name) and domain_name is not None:
                tag['href'] = link_href
                web_link_href, _ = write_web_content(dir_to_download,
                                                     link_href, flag='link')
                tag['href'] = web_link_href
                cnt += 1
                logger.debug('Download ')
            else:
                logger.debug(f'{link_href} not in domain_name or repeated')

    logger.debug(f'Total tags changed: {cnt}')

    if cnt == 0:
        logger.debug(f'Tags not found in {file_with_content}')

    new_html = soup.prettify(formatter='html5')
    # try:
    with open(file_with_content, 'w') as file:
        file.write(new_html)
        for i in tqdm(new_html, 'File write... '):
            sleep(0.00001)
    logger.debug('New tags are written to the file, change_tags finished')
    print()
    return file_with_content
    # except OSError as error:
    #     logger.exception(f'Failed to write content in {file_with_content}')
    #     print(f'Failed to write content in {file_with_content}: {error}')


def download(path, url):
    domain_name = get_domain_name(url)
    dir_to_download = create_dir_from_web(path, url)
    _, web_page_path = write_web_content(dir_to_download, url, flag='web_page')
    result = change_tags(dir_to_download, web_page_path, domain_name)
    return result
