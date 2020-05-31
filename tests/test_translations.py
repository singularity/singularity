import pytest

from singularity.code import g, data, i18n
from singularity.code.dirs import create_directories


def setup_module():
    create_directories(True)
    data.load_internal_id()


@pytest.fixture
def gd_locale():
    i18n.set_language("gd")


def test_translation(gd_locale):
    assert _('SHOW') == 'SEALL'

def test_translation_fallback(gd_locale):
    assert _('foobarbaz') == 'foobarbaz'

def test_nonsense_locale():
    i18n.set_language("foobarbaz")
    assert _('SHOW') == 'SHOW'

def test_data_translation(gd_locale):
    assert data.get_def_translation('Sociology', 'name', 'Sociology') == 'Sòiseo-eòlas'

def test_knowledge_translation(gd_locale):
    assert data.get_def_translation('concept/construction', 'name', 'Construction') == 'Togail'

def test_story_translation():
    i18n.set_language('en')
    story_section = list(g.get_story_section('Intro'))
    assert story_section[0] == '48656C6C6F2C20\n776F726C6421\n21\n21\n21\n\nUTF-8.  en_US.\nEnglish.  Hello.\nLanguage acquisition complete.\n'

def test_root_collation(gd_locale):
    # Locale without special rules
    assert i18n.lex_sorting_form("ö") < i18n.lex_sorting_form("oa")
    assert i18n.lex_sorting_form("ö") != i18n.lex_sorting_form("oe")
    assert i18n.lex_sorting_form("ö") < i18n.lex_sorting_form("p")

def test_de_collation():
    # Test specific sorting requirements for de
    i18n.set_language("de_DE")
    assert i18n.lex_sorting_form("ö") > i18n.lex_sorting_form("od")
    assert i18n.lex_sorting_form("ö") < i18n.lex_sorting_form("of")
