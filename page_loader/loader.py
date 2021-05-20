import os
import os.path
import requests
import re
from bs4 import BeautifulSoup
from lxml import etree as et


def get_format_url(url):
    result = re.split('://', url)
    result2 = re.sub(r'[\W_]', '-', result[1])
# ! использовал регулярные выражения, https://proglib.io/p/regex-for-beginners/
    return result2
# >> ru-hexlet-io-courses


def add_extension(url, ext):
    file_name = get_format_url(url) + '.' + ext
    return file_name
# >> ru-hexlet-io-courses.html


def get_dir_name(url):
    dir_name = get_format_url(url) + '_files'
    return dir_name


def create_dir(path, url):
    dir_path = os.path.join(path, get_dir_name(url))
    try:
        os.makedirs(dir_path, exist_ok=True)
        # ! exist_ok=True - чтобы не возникало ошибок, если каталог существует
    except OSError:
        print(f'Failed to create a directory {dir_path}')
    return dir_path


def download_web_file(url, ext, path='page_loader/tmp'):
    response = requests.get(url)
    response.raise_for_status()
    # ! response.raise_for_status() нужна для того, чтобы проверить, понял вас сервер или нет. Если сервер вернёт 404 «Ресурс не найден», то в response не будет странички сайта, а будет только “Ошибка 404”. Если не вызвать raise_for_status, программа подумает, что всё в порядке, что вы так и хотели: отправить запрос на страницу, которой нет.
    file_name = add_extension(url, ext)
    file_path = os.path.join(path, file_name)
    with open(file_path, 'wb') as file:
        # ! Список режимов доступа к файлу, контекстный менеджер
        # ! http://pythonicway.com/python-fileio
        file.write(response.content)
    return file_path


def download(path, url):
    ext = 'html'
    # path = os.path.abspath(path)
    # ! path.abspath выдает абсолютный путь
    dir_for_img = create_dir(path, url)
    result = download_web_file(url, ext, path)
    print(result)
    return dir_for_img





# def download_img(file_path, dir_path):
#     with open(file_path) as fp:
#     soup = BeautifulSoup(fp, "html.parser")
#     tags_src = soup.find_all('img', src=True)
#     for tag in tags_src:
#         download()



# def get_path_img(file_path):
#     with open(file_path, 'rb') as file:
#         contents = file.read()
#         soup = BeautifulSoup(contents, "html.parser")
#         images_path = soup.find_all(('img')['src'])
#         for images_path 

#     file_path = download(url, path)
#     path_dir = os.path.join(path, get_dirname(url))
#     create_dir(path_dir)



