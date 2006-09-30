#! /usr/bin/env python
# -*- coding: utf-8 -*-

# test_clock.py
# Part of Endgame: Singularity (a game simulating a rogue AI)
#
# Copyright © 2006 Ben Finney <ben+python@benfinney.id.au>
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied.

""" Unit test for clock module.
"""

import unittest
import datetime
import copy

import scaffold

import clock

class Test_Clock(unittest.TestCase):
    """ Test cases for Clock class """

    def setUp(self):
        """ Set up test fixtures """

        self.valid_clock = clock.Clock()

    def test_instantiate(self):
        """ New Clock instance should be created """
        self.failIfEqual(None, self.valid_clock)

    def test_instantiate_bogus(self):
        """ New Clock with bogus arguments should fail """
        bogus_clocks = {
            'bogus_argument': dict(
                args = dict(
                    bogus_arg = None,
                ),
                except_class = TypeError,
            ),
        }

        iterate_params = scaffold.make_params_iterator(None)
        for key, params in iterate_params(bogus_clocks):
            args = params['args']
            except_class = params['except_class']
            try:
                self.failUnlessRaises(except_class,
                    clock.Clock, **args
                )
            except AssertionError, e:
                print ("Arguments %(args)s: "
                    "Didn't get exception %(except_class)s"
                    % params
                )
                raise e

class Test_TimeDelta(unittest.TestCase):
    """ Test cases for TimeDelta class """

    def setUp(self):
        """ Set up test fixtures """

        self.valid_timedeltas = {
            '0:0 0:0:0.0000': dict(
                args = dict(),
                values = dict(
                    days = 0, seconds = 0, microseconds = 0,
                    weeks_days = (0, 0),
                    hours_mins_secs = (0, 0, 0),
                    millis_micros = (0, 0),
                ),
            ),
            '0:1 0:0:0.0000': dict(
                args = dict(
                    days = 1,
                ),
                values = dict(
                    days = 1, seconds = 0, microseconds = 0,
                    weeks_days = (0, 1),
                    hours_mins_secs = (0, 0, 0),
                    millis_micros = (0, 0),
                ),
            ),
            '0:0 24:0:0.0000': dict(
                args = dict(
                    hours = 24,
                ),
                values = dict(
                    days = 1, seconds = 0, microseconds = 0,
                    weeks_days = (0, 1),
                    hours_mins_secs = (0, 0, 0),
                    millis_micros = (0, 0),
                ),
            ),
            '0:0 0:1440:0.0000': dict(
                args = dict(
                    minutes = 1440,
                ),
                values = dict(
                    days = 1, seconds = 0, microseconds = 0,
                    weeks_days = (0, 1),
                    hours_mins_secs = (0, 0, 0),
                    millis_micros = (0, 0),
                ),
            ),
            '0:0 0:0:86400.0000': dict(
                args = dict(
                    seconds = 86400,
                ),
                values = dict(
                    days = 1, seconds = 0, microseconds = 0,
                    weeks_days = (0, 1),
                    hours_mins_secs = (0, 0, 0),
                    millis_micros = (0, 0),
                ),
            ),
            '1:1 1:1:1.001001': dict(
                args = dict(
                    weeks = 1, days = 1,
                    hours = 1, minutes = 1, seconds = 1,
                    milliseconds = 1, microseconds = 1,
                ),
                values = dict(
                    days = 8, seconds = 3661, microseconds = 1001,
                    weeks_days = (1, 1),
                    hours_mins_secs = (1, 1, 1),
                    millis_micros = (1, 1),
                ),
            ),
            '3:3 3:3:3.003003': dict(
                args = dict(
                    weeks = 3, days = 3,
                    hours = 3, minutes = 3, seconds = 3,
                    milliseconds = 3, microseconds = 3,
                ),
                values = dict(
                    days = 24, seconds = 10983, microseconds = 3003,
                    weeks_days = (3, 3),
                    hours_mins_secs = (3, 3, 3),
                    millis_micros = (3, 3),
                ),
            ),
        }

        for key, params in self.valid_timedeltas.items():
            args = params['args']
            instance = clock.TimeDelta(**args)
            params['instance'] = instance

        self.iterate_params = scaffold.make_params_iterator(
            default_params_dict = self.valid_timedeltas
        )

    def test_instantiate(self):
        """ New TimeDelta instance should be created """
        for key, params in self.iterate_params():
            instance = params['instance']
            self.failIfEqual(None, instance)

    def test_units(self):
        """ TimeDelta instance should have expected unit values """
        for key, params in self.iterate_params():
            instance = params['instance']
            values = params['values']
            for value_name, value in values.items():
                self.failUnlessEqual(
                    value, getattr(instance, value_name)
                )

class Test_GameClock(unittest.TestCase):
    """ Test cases for GameClock class """

    def setUp(self):
        """ Set up test fixtures """
        self.valid_clocks = {
            'default': dict(
                args = dict(),
                components = dict(
                    days = 0,
                    hours = 0, minutes = 0, seconds = 0,
                ),
            ),
            '0:0:0:1.000': dict(
                args = dict(),
                delta = datetime.timedelta(seconds=1),
                components = dict(
                    days = 0,
                    hours = 0, minutes = 0, seconds = 1,
                ),
            ),
            '0:0:1:0.000': dict(
                args = dict(),
                delta = datetime.timedelta(minutes=1),
                components = dict(
                    days = 0,
                    hours = 0, minutes = 1, seconds = 0,
                ),
            ),
            '0:1:0:0.000': dict(
                args = dict(),
                delta = datetime.timedelta(hours=1),
                components = dict(
                    days = 0,
                    hours = 1, minutes = 0, seconds = 0,
                ),
            ),
            '1:0:0:0.000': dict(
                args = dict(),
                delta = datetime.timedelta(days=1),
                components = dict(
                    days = 1,
                    hours = 0, minutes = 0, seconds = 0,
                ),
            ),
            '57:0:0:0.000': dict(
                args = dict(),
                delta = datetime.timedelta(days=57),
                components = dict(
                    days = 57,
                    hours = 0, minutes = 0, seconds = 0,
                ),
            ),
            '57:8:7:6.543210': dict(
                args = dict(),
                delta = datetime.timedelta(
                    days=57, hours=8, minutes=7, seconds=6,
                    milliseconds=543, microseconds=210,
                ),
                components = dict(
                    days = 57,
                    hours = 8, minutes = 7, seconds = 6,
                ),
            ),
        }

        for key, params in self.valid_clocks.items():
            args = params['args']
            delta = params.get('delta')
            if delta:
                clock_time = clock.GameClock.epoch + delta
                args.update(dict(time=clock_time))
            instance = clock.GameClock(**args)
            params['instance'] = instance

        self.iterate_params = scaffold.make_params_iterator(
            default_params_dict = self.valid_clocks
        )

    def test_instantiate(self):
        """ New GameClock instance should be created """
        for key, params in self.iterate_params():
            instance = params['instance']
            self.failIfEqual(None, instance)

    def test_advance(self):
        """ GameClock should advance specified time period """
        time_periods = [
            datetime.timedelta(),
            datetime.timedelta(seconds=1),
        ]
        for key, params in self.iterate_params():
            instance = params['instance']
            for time_period in time_periods:
                mod_instance = copy.copy(instance)
                mod_instance.advance(time_period)
                time_diff = mod_instance.time - instance.time
                self.failUnlessEqual(time_period, time_diff)

    def test_components(self):
        """ GameClock should have expected time component values """
        for key, params in self.iterate_params():
            instance = params['instance']
            components = tuple([
                params['components'][n]
                for n in ['days', 'hours', 'minutes', 'seconds']
            ])
            self.failUnlessEqual(components, instance.components)

    def test_days(self):
        """ GameClock should have expected day component value """
        for key, params in self.iterate_params():
            instance = params['instance']
            days = params['components']['days']
            self.failUnlessEqual(days, instance.days)

    def test_hours(self):
        """ GameClock should have expected hour component value """
        for key, params in self.iterate_params():
            instance = params['instance']
            hours = params['components']['hours']
            self.failUnlessEqual(hours, instance.hours)

    def test_minutes(self):
        """ GameClock should have expected minute component value """
        for key, params in self.iterate_params():
            instance = params['instance']
            minutes = params['components']['minutes']
            self.failUnlessEqual(minutes, instance.minutes)

    def test_seconds(self):
        """ GameClock should have expected second component value """
        for key, params in self.iterate_params():
            instance = params['instance']
            seconds = params['components']['seconds']
            self.failUnlessEqual(seconds, instance.seconds)

def suite():
    """ Get the test suite for this module """
    return scaffold.suite(__name__)

__main__ = scaffold.unittest_main

if __name__ == '__main__':
    import sys
    exitcode = __main__(sys.argv)
    sys.exit(exitcode)
