from code import g
import code.data
from code.dirs import create_directories
import code.prerequisite
from code.buyable import cpu, cash
import code.savegame as savegame
import io

def setup_module():
    create_directories(True)
    code.data.reload_all()


def setup_function(func):
    code.data.reset_techs()
    code.data.reset_events()


def save_and_load_game():
    fd = io.BytesIO(b'')
    real_close = fd.close
    fd.close = lambda *args,**kwargs: None
    savegame.write_game_to_fd(fd, gzipped=False)
    fd = io.BytesIO(fd.getvalue())
    assert savegame.load_savegame_by_json_from_fd(io.BufferedReader(fd), 'test-save')
    real_close()


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

    stealth_tech = g.techs['Stealth']
    pl.set_allocated_cpu_for(stealth_tech.id, 1)

    pl.give_time(g.seconds_per_day)
    # Nothing should have appeared in the logs
    assert len(pl.log) == 0
    # We should have spent some money at this point
    assert pl.cash < starting_cash + 5
    assert stealth_tech.cost_left[cpu] < stealth_tech.total_cost[cpu]
    assert stealth_tech.cost_left[cash] < stealth_tech.total_cost[cash]

    # With a save + load
    time_raw_before_save = pl.raw_sec
    cash_before_save = pl.cash
    partial_cash_before_save = pl.partial_cash

    save_and_load_game()

    stealth_tech_after_load = g.techs['Stealth']
    # Ensure this is not a false-test
    assert stealth_tech is not stealth_tech_after_load
    assert stealth_tech.cost_paid[cpu] == stealth_tech_after_load.cost_paid[cpu]
    assert stealth_tech.cost_paid[cash] == stealth_tech_after_load.cost_paid[cash]

    pl_after_load = g.pl

    assert time_raw_before_save == pl_after_load.raw_sec
    assert cash_before_save == pl_after_load.cash
    assert partial_cash_before_save == pl_after_load.partial_cash
