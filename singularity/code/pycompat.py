# A minimal python compatiability layer to support the bare minimum requirements
# that singularity need to be python2 and python3 compatible at the same time.
#
# We could use the six module for this, but it seems like overkill given how
# little we need.

try:
    long = long
except NameError:
    long = int

try:
    unicode = unicode
except NameError:
    unicode = str

try:
    basestring = basestring
except NameError:
    basestring = str

try:
    xrange = xrange
except NameError:
    xrange = range

try:
    # Python 3
    from configparser import ConfigParser, RawConfigParser
    SafeConfigParser = ConfigParser
except ImportError:
    # Python 2.7
    from ConfigParser import ConfigParser, SafeConfigParser, RawConfigParser

    ConfigParser.read_file = ConfigParser.readfp
    SafeConfigParser.read_file = SafeConfigParser.readfp
    RawConfigParser.read_file = RawConfigParser.readfp
