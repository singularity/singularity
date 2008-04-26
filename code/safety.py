import logging, time, traceback, sys
logging.getLogger().addHandler(logging.FileHandler("error.log"))

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
