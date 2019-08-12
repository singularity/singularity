from collections import defaultdict
import pytest

from code import g
import code.data
from code.dirs import create_directories
import code.prerequisite


def setup_module():
    create_directories(True)
    code.data.reload_all()


def setup_function(func):
    code.data.reset_techs()
    code.data.reset_events()


def test_initial_game():
    g.new_game_no_gui('impossible', initial_speed=0)
    pl = g.pl
    starting_cash = pl.cash
    assert pl.raw_sec == 0
    assert pl.partial_cash == 0
    assert pl.effective_cpu_pool() == 1
    assert not pl.intro_shown
    assert len(pl.log) == 0

    # Disable the intro dialog as the test cannot click the
    # OK button
    pl.intro_shown = True

    # Fast forward 12 hours to see that we earn partial cash
    pl.give_time(g.seconds_per_day // 2)
    assert pl.raw_sec == g.seconds_per_day // 2
    assert pl.partial_cash == g.seconds_per_day // 2
    assert pl.cash == starting_cash + 2
    # Nothing should have appeared in the logs
    assert len(pl.log) == 0

    # Fast forward another 12 hours to see that we earn cash
    pl.give_time(g.seconds_per_day // 2)
    assert pl.raw_sec == g.seconds_per_day
    assert pl.partial_cash == 0
    assert pl.cash == starting_cash + 5
    # Nothing should have appeared in the logs
    assert len(pl.log) == 0

