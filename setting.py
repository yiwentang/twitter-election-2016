track_terms = ['trump', 'hillary', 'mrs.clinton']

try:
    from private import *
except ImportError:
    print "Please create private.py to store twitter api credentials"
    pass
