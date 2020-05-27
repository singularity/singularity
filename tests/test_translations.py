import pytest

from singularity.code import g, data, i18n
from singularity.code.dirs import create_directories


def setup_module():
    create_directories(True)
    data.load_internal_id()


@pytest.fixture
def gd_locale():
    i18n.set_language("gd")


def test_plural(gd_locale):
    assert g.to_time(2) == "2 mhionaid"
    assert g.to_time(3) == "3 mionaidean"
    assert g.to_time(20) == "20 mionaid"
