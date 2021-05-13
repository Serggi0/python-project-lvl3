import os.path
import requests
import re


def get_filename(url):
    result = re.split('://', url)
    result2 = re.sub('[\W_]', '-', result[1])
    return result2

def download(url, path='var/temp'):
    path = os.path.abspath(path)
    response = requests.get(url)
    response.raise_for_status()
    filename = get_filename(url) + '.html'

    file_path = os.path.join(path, filename)
    with open(file_path, 'w') as file:
        file.write(response.text)
    print(filename)

download('https://httpbin.org')
