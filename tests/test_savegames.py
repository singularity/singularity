import os
import pytest

from singularity.code import g, data, savegame
from singularity.code.dirs import create_directories


class MockObject(object):
    pass

def setup_module():
    create_directories(True)
    data.reload_all()

def setup_function(func):
    # Some operations (e.g. g.pl.recalc_cpu()) triggers a "needs_rebuild"
    # of the map screen.  Mock that bit for now to enable testing.
    g.map_screen = MockObject()
    g.map_screen.needs_rebuild = False


@pytest.fixture
def savegame_dirs():
    return os.path.dirname(__file__) + "/savegames"


def test_savegames(savegame_dirs):
    for filename in os.listdir(savegame_dirs):
        print("Test savegame: " + filename)
        with open(savegame_dirs + "/" + filename, 'rb') as fd:
            savegame.load_savegame_by_pickle(fd)
