import logging.config
from bs4 import BeautifulSoup
from tqdm import tqdm
from time import sleep
from page_loader.settings_logging import logger_config
from page_loader.web_requests import write_web_content
from page_loader.normalize_data import (convert_relativ_link,
                                        create_dir_for_links,
                                        get_path_for_tags,
                                        get_domain_name, is_valid)


logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')


def get_soup(file_path):
    with open(file_path) as f:
        data = f.read()
        soup = BeautifulSoup(data, "html.parser")
    logger.debug(f'From {file_path} create object BeautifulSoup')
    return soup


def change_tags(path, dir_to_download, file_with_content, url):
    cnt = 0
    domain_name = get_domain_name(url)
    soup = get_soup(file_with_content)
    tags = soup.find_all(['img', 'script', 'link'])

    for tag in tags:
        href = tag.attrs.get('href')
        # if hasattr(tag, 'href'):
        #     href = getattr(tag, 'href')
        src = tag.attrs.get('src')

        if href:
            if href == '' or href is None:
                continue
            else:
                link_href = convert_relativ_link(href, domain_name)
                if link_href.startswith(domain_name) and is_valid(link_href):
                    tag['href'] = link_href
                    path_for_link = write_web_content(path, dir_to_download,
                                                      link_href, flag='link')
                    tag['href'] = get_path_for_tags(path_for_link)
                    cnt += 1
                    logger.debug('Download href')
                else:
                    continue
        elif src:
            if src == '' or src is None:
                continue
            else:
                link_src = convert_relativ_link(src, domain_name)
                if link_src.startswith(domain_name) and is_valid(link_src):
                    tag['src'] = link_src
                    path_for_link = write_web_content(path, dir_to_download,
                                                      link_src, flag='link')
                    tag['src'] = get_path_for_tags(path_for_link)
                    cnt += 1
                    logger.debug('Download src')
                else:
                    continue

    logger.debug(f'Total tags changed: {cnt}')

    if cnt == 0:
        logger.debug(f'Tags not found in {file_with_content}')

    new_html = soup.prettify(formatter='html5')
    with open(file_with_content, 'w') as file:
        file.write(new_html)
        for i in tqdm(new_html, 'File write... '):
            sleep(0.00001)
    logger.debug('New tags are written to the file, change_tags finished')
    print()
    return file_with_content


def download(url, path):
    # if check_url(url):
    dir_path = create_dir_for_links(path, url)
    web_page_path = write_web_content(path,
                                      dir_path,
                                      url, flag='web_page')
    result = change_tags(path, dir_path,
                         web_page_path, url)
    print('Page was successfully downloaded into -> ',
          result, end='\n\n')
    return result
    # else:
    #     print('Invalid URL')
