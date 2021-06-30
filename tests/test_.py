import pytest
import requests
from pathlib import Path
from bs4 import BeautifulSoup # noqa
from PIL import Image, ImageChops
from page_loader import loader
from page_loader.loader import (download, change_src, convert_url_to_file_name,
                                get_web_page, get_img_src, HEADERS)

# ! ПРОВЕРКА МОДУЛЯ:
# ! 1) создание директории для скаченного контента


def test_page_loader_is_dir(requests_mock, tmp_path):
    url = 'http://test.com'
    dir_temp = tmp_path / 'sub'
    dir_temp.mkdir()
    requests_mock.get('http://test.com', text='<!DOCTYPE html>')

    dir_name = 'test_files'
    download(dir_temp, url)
    assert (Path(dir_temp) / dir_name).is_dir()

# ! 2) идентичность скаченного текста:


@pytest.mark.parametrize(
    'url',
    [
        ('https://animaljournal.ru/article/koshka_ocelot')
    ]
)
def test_page_loader_text(tmp_path, url):
    d = tmp_path / 'sub'
    d.mkdir()
    file_temp = d / 'tmp.html'
    content_text = requests.get(url, headers=HEADERS).text
    file_temp.write_text(content_text)
    soup1 = BeautifulSoup(file_temp.read_text(), 'html.parser')
    soup2 = BeautifulSoup(content_text, 'html.parser')
    assert soup1 == soup2

# ! ПРОВЕРКА ФУНКЦИЙ:


@pytest.mark.parametrize(
    'url, correct_value',
    [
        ('https://ru.hexlet.io/courses',
         'ru-hexlet-io-courses'),
        ('http://ru.hexlet.io/courses',
         'ru-hexlet-io-courses'),
        ('https://ru.hexlet.io/courses/page.html',
         'ru-hexlet-io-courses-page.html'),
        ('http://ru.hexlet.io/courses.page.html',
         'ru-hexlet-io-courses-page.html'),
    ]
)
def test_convert_url_to_file_name(url, correct_value):
    assert loader.convert_url_to_file_name(url) == correct_value


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


@pytest.mark.parametrize(
    'url',
    [
        ('http://vospitatel.com.ua/zaniatia/rastenia/lopuh.html')
    ]
)
def test_get_web_page(tmp_path, url):
    dir_temp = tmp_path / 'sub'
    dir_temp.mkdir()
    ext = 'html'
    path_file1_temp, _ = get_web_page(url, ext, dir_temp)
    file_temp2 = dir_temp / 'tmp.html'
    content_text = requests.get(url, headers=HEADERS).text
    file_temp2.write_text(content_text)
    soup1 = BeautifulSoup(file_temp2.read_text(), 'html.parser')
    with open(path_file1_temp) as fp:
        soup2 = BeautifulSoup(fp, 'html.parser')
    assert soup1 == soup2

# ! Проверка по количеству скаченных тегов img_src


@pytest.mark.parametrize(
    'path_web_page, path_page_loader',
    [
        ('tests/fixtures/web_page.html',
         'page_loader/data/vospitatel-com-ua-zaniatia-rastenia-lopuh_files/'
         'vospitatel-com-ua-zaniatia-rastenia-lopuh.html')
    ]
)
def test_get_img_src(path_web_page, path_page_loader):
    quantity_from_web_page = len(get_img_src(path_web_page))
    quantity_from_page_load = len(get_img_src(path_page_loader))
    assert quantity_from_web_page == quantity_from_page_load

# ! Проверка по кол-ву изменненных тегов img_src
# ! проверка списка и кол-ва тегов картинок и файлов


@pytest.mark.parametrize(
    'dir_path, url',
    [
        ('page_loader/data/vospitatel-com-ua-zaniatia-rastenia-lopuh_files',
         'http://vospitatel.com.ua/zaniatia/rastenia/lopuh.html')
    ]
)
def test_change_src(dir_path, url):
    list_for_test = []
    file_path, domain_name = get_web_page(url, ext='html', path=dir_path)
    list_tags_src, list_tags_new_src = change_src(dir_path,
                                                  file_path, domain_name)
    for element in list_tags_src:
        element = convert_url_to_file_name(element)
        list_for_test.append(element)
    assert list_for_test == list_tags_new_src
    assert len(list_tags_src) == len(list_tags_new_src)

# ! Проверка идентичности скаченных картинок по-пиксельно


@pytest.mark.parametrize(
    'img_from_web, img_local',
    [
        ('tests/fixtures/img_web.jpg',
         'page_loader/data/vospitatel-com-ua-zaniatia-rastenia-lopuh_files/'
         'vospitatel-com-ua-images-l-lopuh.jpg')
    ]
)
def test_diff_img(img_from_web, img_local):
    img1 = Image.open(img_from_web)
    img2 = Image.open(img_local)
    differences = ImageChops.difference(img1, img2)
    assert differences.getbbox() is None
