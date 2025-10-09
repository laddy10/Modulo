import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--cuenta", action="store", default=None, help="Número de cuenta a probar"
    )
    parser.addoption(
        "--orden", action="store", default=None, help="Número de orden a probar"
    )

@pytest.fixture
def cuenta(request):
    return request.config.getoption("--cuenta")

@pytest.fixture
def orden(request):
    return request.config.getoption("--orden")

