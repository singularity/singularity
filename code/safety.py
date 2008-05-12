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

import os
import os.path

# We store error.log in .endgame on OSes with a HOME directory;
# otherwise, we store it in the CWD.  As we're not importing any
# parts of E:S here, we have to reimplement this logic.
logpath = "error.log"
if os.environ.has_key("HOME"):
    prefs_dir = os.path.expanduser("~/.endgame")
    if os.path.isdir(prefs_dir):
        logpath = os.path.join(prefs_dir, "error.log")

logging.getLogger().addHandler(logging.FileHandler(logpath))

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
    logging.getLogger().error(error_message)
    sys.stderr.write(error_message + "\n")

def safe_call(func, args, kwargs, on_error):
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
