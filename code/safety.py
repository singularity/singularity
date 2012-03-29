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

def log_error(error_message):
    sys.stderr.write(error_message + "\n")
    if len(logging.getLogger().handlers) > 0:
        try:
            logging.getLogger().error(error_message)
        except IOError: # Probably access denied with --singledir. That's ok
            pass

def safe_call(func, args=(), kwargs={}, on_error=None):
    try:
        return func(*args, **kwargs)
    except Exception, e:
        if isinstance(e, SystemExit):
            raise
        buffer = Buffer("Exception in function %s at %s:\n"
                                   % (func.__name__, get_timestamp()))
        traceback.print_exc(file=buffer)
        log_error(buffer.data)

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
