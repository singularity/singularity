import json
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


def load_save_data_reference(filename):
    with open(filename, 'rb') as fd:
        return json.load(fd)


def compare_loaded_game_with_reference_data(filename, reference_data):
    assert reference_data["raw_sec"] == g.pl.raw_sec
    assert reference_data["cash"] == g.pl.cash
    for cpu_allocation in reference_data["cpu_allocations"]:
        cpu_alloc = g.pl.get_allocated_cpu_for(cpu_allocation)
        # We just check that the allocation is non-zero for now to avoid being
        # too sensitive in the savegames (e.g. due to "minor" tweaks of techs
        # or events)
        print("cpu for %s was %s (expected > 0)" % (cpu_alloc, str(cpu_alloc)))
        assert cpu_alloc > 0
    for tech_id in reference_data["techs_done"]:
        assert tech_id in g.pl.techs, "Invalid reference data for %s: The tech %s does not exist" % (filename, tech_id)
        loaded_tech = g.pl.techs[tech_id]
        print("tech %s is supposed to be done (is done? %s)" % (tech_id, str(loaded_tech.done)))
        assert loaded_tech.done
    for event_id in reference_data["events_triggered"]:
        assert event_id in g.pl.events, "Invalid reference data for %s: The event %s does not exist" % (
            filename, event_id)
        loaded_event = g.pl.events[event_id]
        print("event %s is supposed to be triggered (is triggered? %s)" % (event_id, str(loaded_event.triggered)))
        assert loaded_event.triggered


def test_savegames(savegame_dirs):
    for filename in os.listdir(savegame_dirs):
        full_filename = os.path.join(savegame_dirs, filename)
        if filename.endswith('.sav'):
            print("Test savegame: " + filename)
            with open(full_filename, 'rb') as fd:
                savegame.load_savegame_by_pickle(fd)
        elif filename.endswith('.s2'):
            print("Test savegame: " + filename)
            with open(full_filename, 'rb') as fd:
                savegame.load_savegame_by_json(fd)
        else:
            continue
        savegame_reference_data = load_save_data_reference(full_filename + ".json")
        compare_loaded_game_with_reference_data(filename, savegame_reference_data)
