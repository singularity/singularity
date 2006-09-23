# -*- coding: utf-8 -*-

# scaffold.py
# Part of Endgame: Singularity (a game simulating a rogue AI)
#
# Copyright © 2006 Ben Finney <ben+python@benfinney.id.au>
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied.

""" Scaffolding for unit test modules
"""

import unittest
import os
import sys

test_dir = os.path.dirname(os.path.abspath(__file__))
code_dir = os.path.dirname(test_dir)
if not test_dir in sys.path:
    sys.path.insert(1, test_dir)
if not code_dir in sys.path:
    sys.path.insert(1, code_dir)


def suite(module_name):
    """ Create the test suite for named module """
    from sys import modules
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(modules[module_name])
    return suite

def unittest_main(argv=None):
    """ Mainline function for each unit test module """

    from sys import argv as sys_argv
    if not argv:
        argv = sys_argv

    exitcode = None
    try:
        unittest.main(argv=argv, defaultTest='suite')
    except SystemExit, e:
        exitcode = e.code

    return exitcode


def make_params_iterator(default_params_dict):
    """ Make a function for generating test parameters """

    def iterate_params(params_dict=None):
        """ Iterate a single test for a set of parameters """
        if not params_dict:
            params_dict = default_params_dict
        for key, params in params_dict.items():
            yield key, params

    return iterate_params


class Test_Exception(unittest.TestCase):
    """ Test cases for exception classes """

    def __init__(self, *args, **kwargs):
        """ Set up a new instance """
        self.valid_exceptions = NotImplemented
        unittest.TestCase.__init__(self, *args, **kwargs)

    def setUp(self):
        """ Set up test fixtures """
        for exc_type, params in self.valid_exceptions.items():
            args = (None,) * params['min_args']
            instance = exc_type(*args)
            self.valid_exceptions[exc_type]['instance'] = instance

        self.iterate_params = make_params_iterator(
            default_params_dict = self.valid_exceptions
        )

    def test_exception_instance(self):
        """ Exception instance should be created """
        for key, params in self.iterate_params():
            self.failUnless(params['instance'])

    def test_exception_types(self):
        """ Exception instances should match expected types """
        for key, params in self.iterate_params():
            instance = params['instance']
            for match_type in params['types']:
                self.failUnless(isinstance(instance, match_type))
