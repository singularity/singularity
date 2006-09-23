#! /usr/bin/env python
# -*- coding: utf-8 -*-

# test_tech.py
# Part of Endgame: Singularity (a game simulating a rogue AI)
#
# Copyright © 2006 Ben Finney <ben+python@benfinney.id.au>
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied.

""" Unit test for tech module.
"""

import unittest

import scaffold

import tech


class Test_Tech(unittest.TestCase):
    """ Test cases for Tech class """

    def setUp(self):
        """ Set up test fixtures """

        self.valid_techs = {
            'null': dict(
                args = dict(),
            ),
            'cheap': dict(
                args = dict(),
                cost = (2, 2, 2),
            ),
        }

        for key, params in self.valid_techs.items():
            args = params['args']
            args.update(dict(
                tech_id = None,
                descript = None,
                known = None,
                cost = params.get('cost'),
                prereq = None,
                danger = None,
                tech_type = None,
                secondary_data = None,
            ))
            instance = tech.tech(**args)
            params['instance'] = instance

        self.iterate_params = scaffold.make_params_iterator(
            default_params_dict = self.valid_techs
        )

    def test_instantiate(self):
        """ New Tech instance should be created """
        for key, params in self.iterate_params():
            instance = params['instance']
            self.failIfEqual(None, instance)

    def test_instantiate_bogus(self):
        """ New Tech with bogus params should fail to instantiate """
        bogus_techs = {
            'bogus_arg': dict(
                args = dict(
                    bogus_arg = None,
                ),
                except_class = TypeError,
            ),
            'args_0': dict(
                args = dict(),
                except_class = TypeError,
            ),
            'args_1': dict(
                args = dict(
                    tech_id = None,
                ),
                except_class = TypeError,
            ),
            'args_2': dict(
                args = dict(
                    tech_id = None,
                    descript = None,
                ),
                except_class = TypeError,
            ),
            'args_3': dict(
                args = dict(
                    tech_id = None,
                    descript = None,
                    known = None,
                ),
                except_class = TypeError,
            ),
            'args_4': dict(
                args = dict(
                    tech_id = None,
                    descript = None,
                    known = None,
                    cost = None,
                ),
                except_class = TypeError,
            ),
            'args_5': dict(
                args = dict(
                    tech_id = None,
                    descript = None,
                    known = None,
                    cost = None,
                    prereq = None,
                ),
                except_class = TypeError,
            ),
            'args_6': dict(
                args = dict(
                    tech_id = None,
                    descript = None,
                    known = None,
                    cost = None,
                    prereq = None,
                    danger = None,
                ),
                except_class = TypeError,
            ),
            'args_7': dict(
                args = dict(
                    tech_id = None,
                    descript = None,
                    known = None,
                    cost = None,
                    prereq = None,
                    danger = None,
                    tech_type = None,
                ),
                except_class = TypeError,
            ),
            'args_9': dict(
                args = dict(
                    tech_id = None,
                    descript = None,
                    known = None,
                    cost = None,
                    prereq = None,
                    danger = None,
                    tech_type = None,
                    secondary_data = None,
                    bogus_arg = None,
                ),
                except_class = TypeError,
            ),
        }
        for key, params in self.iterate_params(bogus_techs):
            args = params['args']
            except_class = params['except_class']
            try:
                self.failUnlessRaises(except_class,
                    tech.tech, **args
                )
            except AssertionError, e:
                print ("Arguments %(args)s: "
                    "Didn't get exception %(except_class)s"
                    % params
                )
                raise e

    def test_study_pay_zero(self):
        """ Tech.study of zero should not decrement costs """
        params = self.valid_techs['cheap']
        instance = params['instance']
        cost_towards = (0, 0, 0)
        existing_cost = instance.cost
        result = instance.study(cost_towards)
        self.failIf(result)
        self.failUnlessEqual(existing_cost, instance.cost)

    def test_study_pay_part(self):
        """ Tech.study of part cost should decrement but not complete """
        params = self.valid_techs['cheap']
        instance = params['instance']
        cost_towards = (1, 1, 1)
        existing_cost = instance.cost
        result = instance.study(cost_towards)
        self.failIf(result)
        self.failIfEqual(existing_cost, instance.cost)

    def test_study_pay_full(self):
        """ Tech.study of part cost should decrement but not complete """
        params = self.valid_techs['cheap']
        instance = params['instance']
        cost_towards = instance.cost
        existing_cost = instance.cost
        result = instance.study(cost_towards)
        self.failUnless(result)
        self.failUnlessEqual((0, 0, 0), instance.cost)

    def test_gain_tech(self):
        """ Tech.gain_tech should make technology known """
        for key, params in self.iterate_params():
            instance = params['instance']
            instance.gain_tech()
            self.failUnless(instance.known)


def suite():
    """ Get the test suite for this module """
    return scaffold.suite(__name__)


__main__ = scaffold.unittest_main

if __name__ == '__main__':
    import sys
    exitcode = __main__(sys.argv)
    sys.exit(exitcode)
