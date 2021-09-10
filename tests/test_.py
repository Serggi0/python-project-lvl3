import os
import pytest
import requests
import requests_mock
import filecmp
from bs4 import BeautifulSoup # noqa
from page_loader.page_loader import download
from page_loader.normalize_data import (convert_path_name,
                                        convert_relativ_link)
from page_loader.web_data_processing import load_link
from page_loader.custom_exseptions import Error


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
    'img_from_web, img_local',
    [
        ('tests/fixtures/img_web.jpg',
         'tests/fixtures/img_from_page_loader.jpg')
    ]
)
def diff(img_from_web, img_local):  # image comparison
    assert filecmp(img_from_web, img_local) is True


def test_http_error(requests_mock, tmp_path):
    url = 'http://test404.com'
    dir_temp = tmp_path / 'sub'
    requests_mock.get(url, status_code=404)
    with pytest.raises(Error) as error_info:
        download(url, dir_temp)
        assert 'HTTPError' in str(error_info.value)


def test_dir_exist(requests_mock, tmp_path):
    url = 'http://test.com'
    dir_temp = tmp_path / 'sub'
    requests_mock.get('http://test.com')
    with pytest.raises(Error) as error_info:
        download(url, dir_temp)
        assert 'FileNotFoundError' in str(error_info.value)


def test_bad_url(tmp_path):
    url = 'hps://test.com'
    dir_temp = tmp_path / 'sub'
    with pytest.raises(Error) as error_info:
        download(url, dir_temp)
        assert 'InvalidSchema' in str(error_info.value)


@pytest.fixture
def get_internet_file():
    page_from_internet = open('tests/fixtures/web_page_link.html',
                              'r', encoding='utf-8')
    text = page_from_internet.read()
    yield text
    page_from_internet.close()


@pytest.fixture
def get_check_file():
    check_page = open('tests/fixtures/web_page_result.html',
                      'r', encoding='utf-8')
    text = check_page.read()
    yield text
    check_page.close()


@pytest.fixture
@requests_mock.Mocker(kw='mock')
def get_load_page(get_internet_file, tmp_path, **kwargs):
    # dir_temp = tmp_path / 'sub'
    # dir_temp.mkdir()
    kwargs['mock'].get('http://test.com', text=get_internet_file)
    kwargs['mock'].get('http://test.com/assets/application.css')
    kwargs['mock'].get('http://test.com/courses')
    kwargs['mock'].get('http://test.com/assets/professions/nodejs.png')
    kwargs['mock'].get('http://test.com/packs/js/runtime.js')
    result = download('http://test.com', tmp_path)
    link_count = sum(len(files) for _, _, files in os.walk(tmp_path))
    with open(result, 'r', encoding='utf-8') as file:
        page_result = file.read()
    return page_result, link_count


def test_download(get_load_page, get_check_file):
    res, _ = get_load_page
    assert res == get_check_file


def test_number_links(get_load_page):  # checking by the number of links
    _, numb = get_load_page
    assert numb == 5


@pytest.mark.parametrize(
    'data, url',
    [
        ('tests/fixtures/web_page.html',
         'http://test.com'),
        ('<!DOCTYPE html>',
         'http://test.com/page'),
        ('tests/fixtures/file_js.js',
         'http://test.com/page.js')
    ]
)
@requests_mock.Mocker(kw='mock')
def test_get_web_content(data, url, tmp_path, **kwargs):
    dir_temp = tmp_path / 'sub'
    dir_temp.mkdir()

    kwargs['mock'].get(url, text=data)
    testing_file = load_link(dir_temp, url)
    with open(testing_file) as f:
        data = f.read()

    assert data == requests.get(url).text
