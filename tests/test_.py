import pytest
import requests
from bs4 import BeautifulSoup # noqa
from PIL import Image, ImageChops
from requests.exceptions import HTTPError
from page_loader.page_loader import (change_tags, write_web_content)
from page_loader.normalize_data import (convert_path_name,
                                        convert_relativ_link,
                                        get_dir_name)


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
         'https://ru.hexlet.io/courses'),
        ('//test.com/courses',
         'https://ru.hexlet.io',
         '//test.com/courses')
    ]
)
def test_convert_relativ_link(link, domain_name, correct_value):
    assert convert_relativ_link(link, domain_name) == correct_value


@pytest.mark.parametrize(
    'url, flag, file_with_content',
    [
        ('http://test.com', 'web_page',
         'tests/fixtures/web_page.html')
    ]
)
def test_get_web_content(requests_mock,
                         file_with_content,
                         url, flag, tmp_path):
    dir_temp = tmp_path / 'sub'
    dir_temp.mkdir()
    with open(file_with_content) as f1:
        data1 = f1.read()
    requests_mock.get('http://test.com', text=data1)
    testing_file = write_web_content(tmp_path, dir_temp, url, flag)
    with open(testing_file) as f2:
        data2 = f2.read()
    assert data2 == requests.get('http://test.com').text


@pytest.mark.parametrize(
    'url, flag',
    [
        ('http://test.com/page', 'link')
    ]
)
def test_download_web_link(requests_mock, tmp_path, url, flag):
    dir_temp = tmp_path / 'sub'
    dir_temp.mkdir()
    requests_mock.get('http://test.com/page', text='<!DOCTYPE html>')
    testing_file = write_web_content(tmp_path, dir_temp, url, flag)
    with open(testing_file) as f:
        data = f.read()
    assert data == requests.get('http://test.com/page').text


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


@pytest.mark.parametrize(
    'file_result, file_with_content',
    [
        ('tests/fixtures/web_page_after.html',
         'tests/fixtures/web_page.html')
    ]
)
def diff(file_result, file_with_content):
    with open(file_result) as f1:
        data1 = f1.read()
    with open(file_with_content) as f2:
        data2 = f2.read()
    assert data1 == data2


@pytest.mark.parametrize(
    'page_before, page_after, domain_name',
    [
        ('tests/fixtures/web_page_link.html',
         'tests/fixtures/web_page_result.html',
         'https://ru.hexlet.io')
    ]
)
def test_change_tags(tmp_path, page_before, page_after, domain_name):
    dir_temp = tmp_path / 'sub'
    dir_temp.mkdir()

    try:
        res = change_tags(tmp_path, dir_temp, page_before, domain_name)
    except HTTPError:
        pass
    else:
        with open(res) as f:
            page_result = f.read()
        with open(page_after) as fa:
            page_tampl = fa.read()
        assert page_result == page_tampl


@pytest.mark.parametrize(
    'page_before, page_after, domain_name',
    [
        ('tests/fixtures/web_page_link.html',
         'tests/fixtures/web_page_result.html',
         'https://ru.hexlet.io')
    ]
)
def test_download(url, tmp_path):
    dir_temp = tmp_path / 'sub'
    dir_temp.mkdir()

