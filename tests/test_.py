import pytest
import tempfile
import requests
from page_loader.loader import download


@pytest.mark.parametrize(
    'url, file_path',
    [('https://httpbin.org',
        'page_loader/var/temp/httpbin-org.html')]
)
def test_page_loader(url, file_path):
    my_string = download(url)
    response = requests.get(url)
    response.raise_for_status()
    with tempfile.TemporaryFile() as file_temp:
        file_temp.write(response.content)
        file_temp.seek(0)
        test_string = file_temp.read()
    assert test_string == my_string
