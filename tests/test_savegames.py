import json
import os
import pytest

from io import open
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
    for event_id, event_data in reference_data["events_triggered"].items():
        assert event_id in g.pl.events, "Invalid reference data for %s: The event %s does not exist" % (
            filename, event_id)
        loaded_event = g.pl.events[event_id]
        print("event %s is supposed to be triggered (is triggered? %s)" % (event_id, str(loaded_event.triggered)))
        assert loaded_event.triggered
        print("event %s is supposed to be triggered at %s (actual value: %s)" % (event_id,
                                                                                 loaded_event.triggered_at,
                                                                                 event_data['triggered_at'])
              )
        assert loaded_event.triggered_at == event_data['triggered_at']

    # Verify that CPU states are loaded correctly.
    allocated_cpu_before = sum(x for t, x in g.pl.get_cpu_allocations() if t != 'cpu_pool')
    allocated_cpu_before += g.pl.effective_cpu_pool()
    cpu_by_base = {b: b.cpu for b in g.all_bases()}
    base_cpu = sum(c for c in cpu_by_base.values())

    print("Allocated CPU %s is supposed to equal all CPU from all bases %s" % (allocated_cpu_before, base_cpu))
    assert allocated_cpu_before == base_cpu
    if 'total_cpu' in reference_data:
        print("Total CPU %s is supposed %s (allocations) and %s (bases)" % (
            reference_data['total_cpu'], allocated_cpu_before, base_cpu))
        assert allocated_cpu_before == reference_data['total_cpu']

    g.pl.recalc_cpu()
    allocated_cpu_after = sum(x for t, x in g.pl.get_cpu_allocations() if t != 'cpu_pool')
    allocated_cpu_after += g.pl.effective_cpu_pool()
    print("g.pl.recalc_cpu(): CPU before %s vs. CPU after: %s" % (allocated_cpu_before, allocated_cpu_after))
    assert allocated_cpu_before == allocated_cpu_after

    for b in g.all_bases():
        b.recalc_cpu()
        cpu_before = cpu_by_base[b]
        print("base[%s].recalc_cpu(): CPU before %s vs. CPU after %s" % (b.name, cpu_before, b.cpu))
        assert b.cpu == cpu_by_base[b]



def test_savegames(savegame_dirs):
    for filename in os.listdir(savegame_dirs):
        full_filename = os.path.join(savegame_dirs, filename)
        if filename.endswith('.sav'):
            print("Test savegame: " + filename)
            with open(full_filename, 'rb') as fd:
                savegame.load_savegame_fd(savegame.load_savegame_by_pickle, fd)
        elif filename.endswith('.s2'):
            print("Test savegame: " + filename)
            with open(full_filename, 'rb') as fd:
                savegame.load_savegame_fd(savegame.load_savegame_by_json, fd)
        else:
            continue
        savegame_reference_data = load_save_data_reference(full_filename + ".json")
        compare_loaded_game_with_reference_data(filename, savegame_reference_data)
