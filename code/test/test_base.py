#! /usr/bin/env python
# -*- coding: utf-8 -*-

# test_base.py
# Part of Endgame: Singularity (a game simulating a rogue AI)
#
# Copyright © 2006 Ben Finney <ben+python@benfinney.id.au>
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied.

""" Unit test for base module.
"""

import unittest

import scaffold

import base


class Test_BaseType(unittest.TestCase):
    """ Test cases for BaseType class """

    def setUp(self):
        """ Set up test fixtures """

        self.valid_base_types = {
            'simple': dict(
                args = dict(),
            ),
        }

        for key, params in self.valid_base_types.items():
            args = params['args']
            args.update(dict(
                name = None,
                descript = None,
                size = None,
                regions = None,
                d_chance = None,
                cost = None,
                prereq = None,
                mainten = None,
            ))
            instance = base.base_type(**args)
            params['instance'] = instance

        self.iterate_params = scaffold.make_params_iterator(
            default_params_dict = self.valid_base_types
        )

    def test_instantiate(self):
        """ New BaseType instance should be created """
        for key, params in self.iterate_params():
            instance = params['instance']
            self.failIfEqual(None, instance)

    def test_instantiate_bogus(self):
        """ New BaseType with bogus arguments should fail """
        bogus_base_types = {
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
            'args_1': dict(
                args = dict(
                    name = None,
                ),
                except_class = TypeError,
            ),
            'args_2': dict(
                args = dict(
                    name = None,
                    descript = None,
                ),
                except_class = TypeError,
            ),
            'args_3': dict(
                args = dict(
                    name = None,
                    descript = None,
                    size = None,
                ),
                except_class = TypeError,
            ),
            'args_4': dict(
                args = dict(
                    name = None,
                    descript = None,
                    size = None,
                    regions = None,
                ),
                except_class = TypeError,
            ),
            'args_5': dict(
                args = dict(
                    name = None,
                    descript = None,
                    size = None,
                    regions = None,
                    d_chance = None,
                ),
                except_class = TypeError,
            ),
            'args_6': dict(
                args = dict(
                    name = None,
                    descript = None,
                    size = None,
                    regions = None,
                    d_chance = None,
                    cost = None,
                ),
                except_class = TypeError,
            ),
            'args_7': dict(
                args = dict(
                    name = None,
                    descript = None,
                    size = None,
                    regions = None,
                    d_chance = None,
                    cost = None,
                    prereq = None,
                ),
                except_class = TypeError,
            ),
            'args_9': dict(
                args = dict(
                    name = None,
                    descript = None,
                    size = None,
                    regions = None,
                    d_chance = None,
                    cost = None,
                    prereq = None,
                    mainten = None,
                    bogus_arg = None,
                ),
                except_class = TypeError,
            ),
        }

        for key, params in self.iterate_params(bogus_base_types):
            args = params['args']
            except_class = params['except_class']
            try:
                self.failUnlessRaises(except_class,
                    base.base_type, **args
                )
            except AssertionError, e:
                print ("Arguments %(args)s: "
                    "Didn't get exception %(except_class)s"
                    % params
                )
                raise e


class Stub_BaseType(object):
    """ Stub class for BaseType """

    def __init__(self, *args, **kwargs):
        """ Set up a new instance """
        self.base_id = None
        self.base_name = None
        self.descript = None
        self.size = kwargs.get('size', 0)
        self.regions = None
        self.d_chance = None
        self.cost = kwargs.get('cost', (0, 0, 0))
        self.prereq = None
        self.mainten = None
        self.flavor = None
        self.count = None

class Test_Base(unittest.TestCase):
    """ Test cases for Base class """

    def setUp(self):
        """ Set up test fixtures """

        self.valid_bases = {
            'simple': dict(
                args = dict(),
            ),
            'cheap': dict(
                args = dict(),
                base_type = Stub_BaseType(
                    cost=(2, 2, 2)
                ),
            ),
        }

        for key, params in self.valid_bases.items():
            args = params['args']
            base_type = params.get('base_type')
            if base_type is None:
                base_type = Stub_BaseType()
            args.update(dict(
                ID = None,
                name = None,
                base_type = base_type,
                built = 0,
            ))
            instance = base.base(**args)
            params['instance'] = instance

        self.iterate_params = scaffold.make_params_iterator(
            default_params_dict = self.valid_bases
        )

    def test_instantiate(self):
        """ New Base instance should be created """
        for key, params in self.iterate_params():
            instance = params['instance']
            self.failIfEqual(None, instance)

    def test_instantiate_bogus(self):
        """ New Base with bogus arguments should fail """
        bogus_bases = {
            'args_0': dict(
                args = dict(),
                except_class = TypeError,
            ),
            'args_1': dict(
                args = dict(
                    ID = None,
                ),
                except_class = TypeError,
            ),
            'args_2': dict(
                args = dict(
                    ID = None,
                    name = None,
                ),
                except_class = TypeError,
            ),
            'args_3': dict(
                args = dict(
                    ID = None,
                    name = None,
                    base_type = None,
                ),
                except_class = TypeError,
            ),
            'args_5': dict(
                args = dict(
                    ID = None,
                    name = None,
                    base_type = None,
                    built = None,
                    bogus_arg = None,
                ),
                except_class = TypeError,
            ),
            'bad_base_type': dict(
                args = dict(
                    ID = None,
                    name = None,
                    base_type = None,
                    built = None,
                ),
                except_class = AttributeError,
            ),
        }

        for key, params in self.iterate_params(bogus_bases):
            args = params['args']
            except_class = params['except_class']
            try:
                self.failUnlessRaises(except_class,
                    base.base, **args
                )
            except AssertionError, e:
                print ("Arguments %(args)s: "
                    "Didn't get exception %(except_class)s"
                    % params
                )
                raise e

    def test_study_pay_zero(self):
        """ Base.study of zero should not decrement costs """
        params = self.valid_bases['cheap']
        instance = params['instance']
        cost_towards = (0, 0, 0)
        existing_cost = instance.cost
        result = instance.study(cost_towards)
        self.failIf(result)
        self.failUnlessEqual(existing_cost, instance.cost)

    def test_study_pay_part(self):
        """ Base.study of part cost should decrement but not complete """
        params = self.valid_bases['cheap']
        instance = params['instance']
        cost_towards = (1, 1, 1)
        existing_cost = instance.cost
        result = instance.study(cost_towards)
        self.failIf(result)
        self.failIfEqual(existing_cost, instance.cost)

    def test_study_pay_full(self):
        """ Base.study of part cost should decrement but not complete """
        params = self.valid_bases['cheap']
        instance = params['instance']
        cost_towards = instance.cost
        existing_cost = instance.cost
        result = instance.study(cost_towards)
        self.failUnless(result)
        self.failUnlessEqual((0, 0, 0), instance.cost)


def suite():
    """ Get the test suite for this module """
    return scaffold.suite(__name__)


__main__ = scaffold.unittest_main

if __name__ == '__main__':
    import sys
    exitcode = __main__(sys.argv)
    sys.exit(exitcode)
