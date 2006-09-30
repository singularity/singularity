#! /usr/bin/env python
# -*- coding: utf-8 -*-

# test_item.py
# Part of Endgame: Singularity (a game simulating a rogue AI)
#
# Copyright © 2006 Ben Finney <ben+python@benfinney.id.au>
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied.

""" Unit test for item module.
"""

import unittest

import scaffold

import item

class Test_ItemClass(unittest.TestCase):
    """ Test cases for ItemClass class """

    def setUp(self):
        """ Set up test fixtures """

        self.valid_item_classes = {
            'simple': dict(
                args = dict(),
            ),
        }

        for key, params in self.valid_item_classes.items():
            args = params['args']
            args.update(dict(
                name = None,
                descript = None,
                cost = None,
                prereq = None,
                item_type = None,
                item_qual = None,
                buildable = None,
            ))
            instance = item.item_class(**args)
            params['instance'] = instance

        self.iterate_params = scaffold.make_params_iterator(
            default_params_dict = self.valid_item_classes
        )

    def test_instantiate(self):
        """ New ItemClass instance should be created """
        for key, params in self.iterate_params():
            instance = params['instance']
            self.failIfEqual(None, instance)

    def test_instantiate_bogus(self):
        """ New ItemClass with bogus arguments should fail """
        bogus_item_classes = {
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
                    cost = None,
                ),
                except_class = TypeError,
            ),
            'args_4': dict(
                args = dict(
                    name = None,
                    descript = None,
                    cost = None,
                    prereq = None,
                ),
                except_class = TypeError,
            ),
            'args_5': dict(
                args = dict(
                    name = None,
                    descript = None,
                    cost = None,
                    prereq = None,
                    item_type = None,
                ),
                except_class = TypeError,
            ),
            'args_6': dict(
                args = dict(
                    name = None,
                    descript = None,
                    cost = None,
                    prereq = None,
                    item_type = None,
                    item_qual = None,
                ),
                except_class = TypeError,
            ),
            'args_8': dict(
                args = dict(
                    name = None,
                    descript = None,
                    cost = None,
                    prereq = None,
                    item_type = None,
                    item_qual = None,
                    buildable = None,
                    bogus_arg = None,
                ),
                except_class = TypeError,
            ),
        }

        for key, params in self.iterate_params(bogus_item_classes):
            args = params['args']
            except_class = params['except_class']
            try:
                self.failUnlessRaises(except_class,
                    item.item_class, **args
                )
            except AssertionError, e:
                print ("Arguments %(args)s: "
                    "Didn't get exception %(except_class)s"
                    % params
                )
                raise e

class Stub_ItemClass(object):
    """ Stub class for ItemClass """

    def __init__(self, *args, **kwargs):
        """ Set up a new instance """
        self.name = None
        self.descript = None
        self.cost = kwargs.get('cost', (0, 0, 0))
        self.prereq = None
        self.item_type = None
        self.item_qual = None
        self.buildable = None

class Test_Item(unittest.TestCase):
    """ Test cases for Item class """

    def setUp(self):
        """ Set up test fixtures """

        self.valid_items = {
            'simple': dict(
                args = dict(),
            ),
            'cheap': dict(
                args = dict(),
                item_type = Stub_ItemClass(
                    cost = (2, 2, 2),
                ),
            ),
        }

        for key, params in self.valid_items.items():
            args = params['args']
            item_type = params.get('item_type')
            if item_type is None:
                item_type = Stub_ItemClass()
            args.update(dict(
                item_type = item_type,
            ))
            instance = item.item(**args)
            params['instance'] = instance

        self.iterate_params = scaffold.make_params_iterator(
            default_params_dict = self.valid_items
        )

    def test_instantiate(self):
        """ New Base instance should be created """
        for key, params in self.iterate_params():
            instance = params['instance']
            self.failIfEqual(None, instance)

    def test_instantiate_bogus(self):
        """ New Base with bogus arguments should fail """
        bogus_items = {
            'args_0': dict(
                args = dict(),
                except_class = TypeError,
            ),
            'args_2': dict(
                args = dict(
                    item_type = Stub_ItemClass(),
                    bogus_arg = None,
                ),
                except_class = TypeError,
            ),
            'bad_item_type': dict(
                args = dict(
                    item_type = None,
                ),
                except_class = AttributeError,
            ),
        }

        for key, params in self.iterate_params(bogus_items):
            args = params['args']
            except_class = params['except_class']
            try:
                self.failUnlessRaises(except_class,
                    item.item, **args
                )
            except AssertionError, e:
                print ("Arguments %(args)s: "
                    "Didn't get exception %(except_class)s"
                    % params
                )
                raise e

    def test_study_pay_zero(self):
        """ Item.study of zero should not decrement costs """
        params = self.valid_items['cheap']
        instance = params['instance']
        cost_towards = (0, 0, 0)
        existing_cost = instance.cost
        result = instance.study(cost_towards)
        self.failIf(result)
        self.failUnlessEqual(existing_cost, instance.cost)

    def test_study_pay_part(self):
        """ Item.study of part cost should decrement but not complete """
        params = self.valid_items['cheap']
        instance = params['instance']
        cost_towards = (1, 1, 1)
        existing_cost = instance.cost
        result = instance.study(cost_towards)
        self.failIf(result)
        self.failIfEqual(existing_cost, instance.cost)

    def test_study_pay_full(self):
        """ Item.study of part cost should decrement but not complete """
        params = self.valid_items['cheap']
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
