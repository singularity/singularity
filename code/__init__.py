# A dirty hack to merge stdlib's "code" module to local namespace
# Allows IDEs and debuggers that import code, like PyDev, to work properly
# In the future this package should be renamed to "src" so it does not collide
# with Python's standard library modules/packages.
def _copy():

    import sys, os, imp
    esdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    fd, path, desc = imp.find_module(__name__, [p for p in sys.path
                                                if not p.startswith(esdir)])
    module = imp.load_module(__name__ + '_stdlib', fd, path, desc)
    fd.close()
    for key in module.__dict__:
        if not hasattr(sys.modules[__name__], key):
            setattr(sys.modules[__name__], key, getattr(module, key))
try:
    _copy()
except Exception:
    # _copy() is entirely optional, so it really doesn't matter if it fails
    pass
del _copy
