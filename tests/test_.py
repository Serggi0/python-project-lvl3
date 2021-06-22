import pytest
from bs4 import BeautifulSoup # noqa
from PIL import Image, ImageChops
from page_loader import loader
from page_loader.loader import change_src, get_web_page, get_img_src


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


@pytest.mark.parametrize(
    'url, ext, path',
    [
        ('https://ru.hexlet.io/courses', 'html', 'page_loader/data')
    ]
)
def test_get_web_page(url, ext, path):
    result = loader.get_web_page(url, ext, path)
    assert result == ('page_loader/data/ru-hexlet-io-courses.html',
                      'https://ru.hexlet.io')


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


@pytest.mark.parametrize(
    'dir_path, url',
    [
        ('page_loader/data/vospitatel-com-ua-zaniatia-rastenia-lopuh_files',
         'http://vospitatel.com.ua/zaniatia/rastenia/lopuh.html')
    ]
)
def test_change_src(dir_path, url):
    file_path, domain_name = get_web_page(url, ext='html', path=dir_path)
    list_tags_src, list_tags_new_src = change_src(dir_path,
                                                  file_path, domain_name)
    assert len(list_tags_src) == len(list_tags_new_src)


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
