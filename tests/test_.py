import pytest
import tempfile
import requests
from page_loader import loader


@pytest.mark.parametrize(
    'url',
    [('https://httpbin.org')]
)
def test_page_loader(url):
    my_string = loader.download(url)
    response = requests.get(url)
    response.raise_for_status()
    with tempfile.TemporaryFile() as file_temp:
        file_temp.write(response.content)
        file_temp.seek(0)
        test_string = file_temp.read()
    assert test_string == my_string
