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

def safe_call(func, args=(), kwargs={}, on_error=None):
    try:
        return func(*args, **kwargs)
    except Exception:
        logging.error("Try to save and exit the game, and contact the developers.",
                      exc_info=1)
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
