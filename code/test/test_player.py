#! /usr/bin/env python
# -*- coding: utf-8 -*-

# test_player.py
# Part of Endgame: Singularity (a game simulating a rogue AI)
#
# Copyright © 2006 Ben Finney <ben+python@benfinney.id.au>
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied.

""" Unit test for player module.
"""

import unittest
import datetime
import copy

import scaffold

import player
import clock

class Test_Player(unittest.TestCase):
    """ Test cases for Player class """

    def setUp(self):
        """ Set up test fixtures """

        self.valid_players = {
            'default': dict(
                args = dict(),
            ),
        }

        for key, params in self.valid_players.items():
            args = params['args']
            args.update(dict(
                cash = 0,
            ))
            instance = player.player_class(**args)
            params['instance'] = instance

        self.iterate_params = scaffold.make_params_iterator(
            default_params_dict = self.valid_players
        )

    def test_instantiate(self):
        """ New Player instance should be created """
        for key, params in self.iterate_params():
            instance = params['instance']
            self.failIfEqual(None, instance)

    def test_instantiate_bogus(self):
        """ New Player with bogus arguments should fail """
        bogus_players = {
            'bogus_argument': dict(
                args = dict(
                    bogus_arg = None,
                ),
                except_class = TypeError,
            ),
            'args_0': dict(
                args = dict(),
                except_class = TypeError,
            ),
            'args_2': dict(
                args = dict(
                    cash = None,
                    bogus_arg = None,
                ),
                except_class = TypeError,
            ),
        }

        for key, params in self.iterate_params(bogus_players):
            args = params['args']
            except_class = params['except_class']
            try:
                self.failUnlessRaises(except_class,
                    player.player_class, **args
                )
            except AssertionError, e:
                print ("Arguments %(args)s: "
                    "Didn't get exception %(except_class)s"
                    % params
                )
                raise e

    def test_give_time_advances_clock(self):
        """ Player.give_time should advance clock by a time delta """
        valid_timedeltas = [
            datetime.timedelta(seconds=0),
            datetime.timedelta(seconds=1),
            datetime.timedelta(seconds=20),
            datetime.timedelta(seconds=61),
            datetime.timedelta(seconds=3601),
            datetime.timedelta(days=1),
            datetime.timedelta(days=1, seconds=20),
            datetime.timedelta(days=30),
        ]
        for key, params in self.iterate_params():
            orig_instance = params['instance']
            for td in valid_timedeltas:
                time_add = clock.TimeDelta(
                    days=td.days, seconds=td.seconds,
                    microseconds=td.microseconds
                )
                mod_instance = copy.deepcopy(orig_instance)
                mod_instance.give_time(time_add)
                time_diff = (
                    mod_instance.clock.time - orig_instance.clock.time
                )
                self.failUnlessEqual(time_add, time_diff)

def suite():
    """ Get the test suite for this module """
    return scaffold.suite(__name__)

__main__ = scaffold.unittest_main

if __name__ == '__main__':
    import sys
    exitcode = __main__(sys.argv)
    sys.exit(exitcode)
