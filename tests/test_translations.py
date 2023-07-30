# coding=utf-8
import pytest
import sys

from singularity.code import g, data, i18n
from singularity.code.dirs import create_directories


IS_PY2 = sys.version_info[0] == 2


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
    assert _("SHOW") == "SEALL"


def test_second_locale():
    i18n.set_language("fr_FR")
    assert _("DAY") == "JOUR"


def test_translation_fallback(gd_locale):
    assert _("foobarbaz") == "foobarbaz"
    assert ngettext("foo", "bar", 1) == "foo"
    assert ngettext("foo", "bar", 5) == "bar"


def test_nonsense_locale():
    i18n.set_language("foobarbaz")
    assert _("SHOW") == "SHOW"


@pytest.mark.skipif(IS_PY2, reason="Unicode issues under python2")
def test_data_translation(gd_locale):
    assert data.get_def_translation("Sociology", "name", "Sociology") == "Sòiseo-eòlas"


def test_knowledge_translation(gd_locale):
    assert (
        data.get_def_translation("concept/construction", "name", "Construction")
        == "Togail"
    )


def test_story_translation():
    i18n.set_language("en")
    story_section = list(g.get_story_section("Intro"))
    assert (
        story_section[0]
        == "48656C6C6F2C20\n776F726C6421\n21\n21\n21\n\nUTF-8.  en_US.\nEnglish.  Hello.\nLanguage acquisition complete.\n"
    )


# Sorting
# Fails in github actions (not sure why)
@pytest.mark.xfail
@pytest.mark.skipif(IS_PY2, reason="Lexical sorting is disabling in python2")
def test_root_collation(gd_locale):
    # Locale without special rules
    assert i18n.lex_sorting_form("ö") < i18n.lex_sorting_form("oa")
    assert i18n.lex_sorting_form("ö") != i18n.lex_sorting_form("oe")
    assert i18n.lex_sorting_form("ö") < i18n.lex_sorting_form("p")


@pytest.mark.skipif(IS_PY2, reason="Lexical sorting is disabling in python2")
def test_de_collation():
    # Test specific sorting requirements for de
    i18n.set_language("de_DE")
    assert i18n.lex_sorting_form("ö") > i18n.lex_sorting_form("od")
    assert i18n.lex_sorting_form("ö") < i18n.lex_sorting_form("of")
