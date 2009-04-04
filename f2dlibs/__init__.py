"""
f2dlibs library
"""

###
### imports
import sys
import re
import pickle
import urllib
import urllib2
import logging

###
### class defs
class Storage(dict):
    """Just a simple storage class"""
    def __init__(self, dict=None):
        if dict:
            self.update(dict)

    def __getattr__(self,key):
        try:
            return self[key]
        except KeyError, k:
            raise AttributeError, k

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError, k:
            raise AttributeError, k

    def __repr__(self):
        return '<Storage ' + dict.__repr__(self) + '>'

class FeedContainer(object):
    """Container object for feeds."""

    def __init__(self, filename):
        self.feeds = Storage()
        self.filename = filename
        self.loaded = False

    def load(self):
        """Load datfile as a feedcontainer"""
        self.feeds = pickle.load(open(self.filename, 'rb'))
        self.loaded = True

    def save(self):
        pickle.dump(self.feeds, open(self.filename, 'wb'))

class NullLoggingHandler(logging.Handler):
    """Null logging handler for logging"""
    def emit(self, record): pass

class TimeoutError(Exception):
    """Timeout error class"""

###
### function defs
def timeout(timelimit, func, *args, **kwargs):
    """
    snippet from http://code.activestate.com/recipes/473878/
    """
    import threading
    class FeedFetchThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.result = None
            self.error = None

        def run(self):
            try:
                self.result = func(*args, **kwargs)
            except:
                self.error = sys.exc_info()[:2]

    fft = FeedFetchThread()
    fft.start()
    fft.join(timelimit)
    if fft.isAlive():
        raise TimeoutError
    if fft.error:
        # reraise to caller
        raise fft.error[0], fft.error[1]
    return fft.result

# setup a null logger so we don't spew junk if a parent 
# logger isn't configured
h = NullLoggingHandler()
logging.getLogger('botlibs').addHandler(h)

