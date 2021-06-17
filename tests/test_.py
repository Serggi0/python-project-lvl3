import pytest
import tempfile
import requests
from page_loader import loader
import page_loader


# @pytest.mark.parametrize(
#     'path', 'url',
#     [
#         ('page_loader/data',
#             'https://linzi-vsem.ru/karnavalnye/linzy-sharingan/')
#     ]
# )
# def test_page_loader(path, url):
#     my_string = loader.download(path, url)
#     response = requests.get(url)
#     response.raise_for_status()
#     with tempfile.TemporaryFile() as file_temp:
#         file_temp.write(response.content)
#         file_temp.seek(0)
#         test_string = file_temp.read()
#     assert test_string == my_string


@pytest.mark.parametrize(
    'url',
    [
        ('https://ru.hexlet.io/courses'),
        ('http://ru.hexlet.io/courses')
    ]
)
def test_1_convert_url_to_file_name(url):
    result = loader.convert_url_to_file_name(url)
    assert result == 'ru-hexlet-io-courses'


@pytest.mark.parametrize(
    'url',
    [
        ('https://ru.hexlet.io/courses/page.html'),
        ('http://ru.hexlet.io/courses.page.html')
    ]
)
def test_2_convert_url_to_file_name(url):
    result = loader.convert_url_to_file_name(url)
    assert result == 'ru-hexlet-io-courses-page.html'


@pytest.mark.parametrize(
    'url',
    [
        ('https://ru.hexlet.io/courses'),
        ('https://ru.hexlet.io/courses.html')
    ]
)
def test_get_dir_name(url):
    result = loader.get_dir_name(url)
    assert result == 'ru-hexlet-io-courses_files'


@pytest.mark.parametrize(
    'url, ext',
    [
        ('https://ru.hexlet.io/courses', 'html'),
        ('https://ru.hexlet.io/courses.html', 'html'),
    ]
)
def test_add_extension(url, ext):
    result = loader.add_extension(url, ext)
    assert result == 'ru-hexlet-io-courses.html'


# @pytest.mark.parametrize(
#     'url', 'ext', 'path'
#     [
#         ('https://ru.hexlet.io/courses', 'html', 'page_loader/data'),
#     ]
# )
# def test_get_web_page(url, ext, path):
#     result = loader.get_web_page(url, ext, path)
#     assert result == 'page_loader/data/ru-hexlet-io-courses_files/ru-hexlet-io-courses.html'