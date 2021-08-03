import pytest
import requests
from bs4 import BeautifulSoup # noqa
from PIL import Image, ImageChops
from page_loader.loader import (convert_path_name,
                                convert_relativ_link, get_dir_name,
                                download_web_link, get_web_content,
                                get_response_server)


# ! Проверка конверттации URL по заданному шаблону:


@pytest.mark.parametrize(
    'url, correct_value',
    [
        ('https://ru.hexlet.io/courses',
         'ru-hexlet-io-courses'),
        ('http://ru.hexlet.io/courses',
         'ru-hexlet-io-courses'),
        ('https://ru.hexlet.io/courses/page.html',
         'ru-hexlet-io-courses-page-html'),
        ('http://ru.hexlet.io/courses.page.html',
         'ru-hexlet-io-courses-page-html'),
        ('//ru.hexlet.io/courses',
         '--ru-hexlet-io-courses'),
    ]
)
def test_convert_path_name(url, correct_value):
    assert convert_path_name(url) == correct_value


@pytest.mark.parametrize(
    'url',
    [
        ('https://ru.hexlet.io/courses.html')
    ]
)
def test_get_dir_name(url):
    result = get_dir_name(url)
    assert result == 'ru-hexlet-io-courses-html_files'

# ! Проверка изменения относительной ссылки на локальные ресурсы в абсолютную:


@pytest.mark.parametrize(
    'link, domain_name, correct_value',
    [
        ('https://ru.hexlet.io/courses',
         'https://ru.hexlet.io',
         'https://ru.hexlet.io/courses'),
        ('/courses',
         'https://ru.hexlet.io',
         'https://ru.hexlet.io/courses'),
        ('./courses',
         'https://ru.hexlet.io',
         'https://ru.hexlet.io/courses'),
        ('//ru.hexlet.io/courses',
         'https://ru.hexlet.io',
         '//ru.hexlet.io/courses'),
    ]
)
def test_convert_relativ_link(link, domain_name, correct_value):
    assert convert_relativ_link(link, domain_name) == correct_value

# ! Проверка идентичности скаченного контента:


@pytest.mark.parametrize(
    'url, ext, file_with_content',
    [
        ('http://test.com', 'html',
         'tests/fixtures/web_page.html')
    ]
)
def test_get_web_content(requests_mock, file_with_content, url, ext, tmp_path):
    dir_temp = tmp_path / 'sub'
    dir_temp.mkdir()
    with open(file_with_content) as f1:
        data1 = f1.read()
    requests_mock.get('http://test.com', text=data1)
    testing_file = get_web_content(url, ext, dir_temp)
    with open(testing_file) as f2:
        data2 = f2.read()
    assert data2 == requests.get('http://test.com').text

# ! Проверка скачивания ссылки в документе:


@pytest.mark.parametrize(
    'url, ext',
    [
        ('http://test.com/page', 'html')
    ]
)
def test_download_web_link(requests_mock, tmp_path, url, ext):
    dir_temp = tmp_path / 'sub'
    dir_temp.mkdir()
    requests_mock.get('http://test.com/page', text='<!DOCTYPE html>')
    _, testing_file = download_web_link(dir_temp, url, ext)
    with open(testing_file) as f:
        data = f.read()
    assert data == requests.get('http://test.com/page').text


# ! Проверка идентичности скаченных картинок по-пиксельно:


@pytest.mark.parametrize(
    'img_from_web, img_local',
    [
        ('tests/fixtures/img_web.jpg',
         'tests/fixtures/img_from_page_loader.jpg')
    ]
)
def test_diff_img(img_from_web, img_local):
    img1 = Image.open(img_from_web)
    img2 = Image.open(img_local)
    differences = ImageChops.difference(img1, img2)
    assert differences.getbbox() is None

# ! Проверка по тестовой странице:


@pytest.mark.parametrize(
    'file_result, file_with_content, domain_name',
    [
        ('tests/fixtures/web_page.html',
         'page_loader/data/vospitatel-com-ua-zaniatia-rastenia-'
         'lopuh-html_files/vospitatel-com-ua-zaniatia-rastenia-'
         'lopuh-html.html',
         'http://vospitatel.com.ua')
    ]
)
def diff(file_result, file_with_content, domain_name):
    with open(file_result) as f1:
        data1 = f1.read()
    with open(file_with_content) as f2:
        data2 = f2.read()
    assert data1 == data2


@pytest.mark.parametrize(
    'url, text',
    [
        ('https://httpbin.org/status/404',
         'Not Found. The server cannot find the requested resource.'),
        ('https://httpbin.org/status/504', 'Gateway Timeout')
    ]
)
def test_get_response_server(url, text):
    assert get_response_server(url) == text
