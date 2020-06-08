import gettext
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

def test_translation(gd_locale):
    assert _('SHOW') == 'SEALL'

def test_second_locale():
    i18n.set_language("fr_FR")
    assert _('DAY') == 'JOUR'

def test_translation_fallback(gd_locale):
    assert _('foobarbaz') == 'foobarbaz'
    assert ngettext('foo', 'bar', 1) == 'foo'
    assert ngettext('foo', 'bar', 5) == 'bar'

"""
TODO revisit this test once everything works
def test_nonsense_locale():
    i18n.set_language("foobarbaz")
    assert _('SHOW') == 'SHOW'
"""

def test_data_translation(gd_locale):
    assert data.get_def_translation('Sociology', 'name', 'Sociology') == 'Sòiseo-eòlas'

def test_knowledge_translation(gd_locale):
    assert data.get_def_translation('concept/construction', 'name', 'Construction') == 'Togail'

def test_story_translation():
    i18n.set_language('en')
    story_section = list(g.get_story_section('Intro'))
    assert story_section[0] == '48656C6C6F2C20\n776F726C6421\n21\n21\n21\n\nUTF-8.  en_US.\nEnglish.  Hello.\nLanguage acquisition complete.\n'

"""
n = len(os.listdir('.'))
cat = GNUTranslations(somefile)
message = cat.ngettext(
    'There is %(num)d file in this directory',
    'There are %(num)d files in this directory',
    n) % {'num': n}
"""
