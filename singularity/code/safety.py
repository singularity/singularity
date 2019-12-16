#file: safety.py
#Copyright (C) 2008 FunnyMan3595
#This file is part of Endgame: Singularity.

#Endgame: Singularity is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.

#Endgame: Singularity is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with Endgame: Singularity; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#This file contains wrapper functions for making error-tolerant "safe" calls.

import logging
import time
import traceback
import sys

class Buffer(object):
    def __init__(self, prefix=""):
        self.data = prefix
    def write(self, unbuffered):
        self.data += unbuffered

def get_timestamp(when=None):
    if when == None:
        when = time.time()
    return time.ctime(when) + " " + time.tzname[time.daylight]


def log_error(error_message, *args):
    if len(args):
        sys.stderr.write((error_message % args) + "\n")
    else:
        sys.stderr.write(error_message + "\n")
    if len(logging.getLogger().handlers) > 0:
        try:
            logging.getLogger().error(error_message, *args)
        except IOError:  # Probably access denied with --singledir. That's ok
            pass


def log_func_exc(func):
    buffer = Buffer("Exception in function %s at %s:\n```\n"
                                   % (func.__name__, get_timestamp()))
    traceback.print_exc(file=buffer)
    buffer.write("```")
    log_error(buffer.data)


FIRST_ERROR = True

def safe_call(func, args=(), kwargs={}, on_error=None):
    try:
        return func(*args, **kwargs)
    except Exception:
        global FIRST_ERROR
        if FIRST_ERROR:
            log_error("----- Basic information (Please include all the data below in the bug report) ------")
            log_error("Please submit the crash on github: https://github.com/singularity/singularity/issues/new")
            try:
                from singularity import __full_version__
            except ImportError:
                __full_version__ = "N/A (Import error)"
            log_error("Singularity version %s", __full_version__)
            log_error("Python version %s", sys.version.replace("\n", ''))
            FIRST_ERROR = False
        log_func_exc(func)

#        # ... --- ...
#        import g
#        g.play_sound("click")
#        delays = (.15, .15, .8, .5, .5, .8, .15, .15)
#        for delay in delays:
#            time.sleep(delay)
#            g.play_sound("click")

        return on_error

# Catches any errors raised by a function, logs them, and returns the given
# value.
#
# Apply to a function like so:
# @safe(my_error_code)
# def my_function(...)
#
# And then:
# result = my_function(...)
# if result == my_error_code:
#     # An error was raised.
def safe(on_error):
    return lambda func: _safe(func, on_error)

def _safe(func, on_error):
    return lambda *args, **kwargs: safe_call(func, args, kwargs, on_error)
