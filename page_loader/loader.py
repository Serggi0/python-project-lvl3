import os.path
import requests
import re


def get_filename(url):
    result = re.split('://', url)
    result2 = re.sub(r'[\W_]', '-', result[1])
    return result2


def download(url, path='page_loader/var/temp'):
    path = os.path.abspath(path)
    response = requests.get(url)
    response.raise_for_status()
    filename = get_filename(url) + '.html'
    file_path = os.path.join(path, filename)
    with open(file_path, 'wb') as file:
        file.write(response.content)
    with open(file_path, 'rb') as file:
        my_string = file.read()
    print(file_path)
    return my_string
