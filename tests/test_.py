import pytest
import tempfile
import requests


@pytest.mark.parametrize(
    'url, file_path',
    [('https://httpbin.org',
        'page_loader/var/temp/httpbin-org.html')]
)
def test_page_loader(url, file_path):
    response = requests.get(url)
    response.raise_for_status()
    file_temp = tempfile.TemporaryFile()
    file_temp.write(response.content)
    file_temp.seek(0)
    test_string = file_temp.read()
    with open(file_path, 'rb') as f:
        my_string = f.read()
    assert test_string == my_string
    file_temp.close()
