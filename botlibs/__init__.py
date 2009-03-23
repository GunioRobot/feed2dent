"""
archbot library

this package contains the following methods:

tighturlify -- Method to turn a url into a bit.ly shortened url.
mkdent      -- Method to post data to identica.
"""

###
### imports
import urllib
import urllib2
import sys
import re
import logging
import lxml

###
### conditional imports
try: import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        print "Could not import json or simplejson module"
        sys.exit(1)

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

###
### method defs
def tighturlify(config, url):
    """use tighturl to shorten a url and return the shorter version"""
    logger = logging.getLogger('botlibs.tighturlify')
    ## prepare the connection requirements
    request = urllib2.Request('%s%s' % (config.apiurl, url))
    request.add_header('User-agent', 'archbot/1.0')
    logger.debug('performaing tighturl request')
    response = urllib2.urlopen(request)

    from lxml.html import parse
    logger.debug('parsing response html')
    doc = parse(response)
    page = doc.getroot()
    try:
        tighturl = page.forms[0].fields['tighturl']
    except KeyError:
        # not where it is expected to be.
        tighturl = None
    logger.debug('got url: "%s"', tighturl)
    return tighturl

def mkdent(config, data):
    """post text to identi.ca"""
    logger = logging.getLogger('botlibs.mkdent')
    ## make sure to chop data
    if len(data) > 136:
        logger.info('dent was too long. copping')
        logger.debug('dent before chop: "%s"', data)
        data = data[:136] + ' ...'
        logger.debug('dent after chop: "%s"', data)

    ## prepare the connection requirements
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(
        realm=None,
        uri=config.apiurl,
        user=config.user,
        passwd=config.passwd)
    auth_handler = urllib2.HTTPBasicAuthHandler(password_mgr)
    opener = urllib2.build_opener(auth_handler)
    request = urllib2.Request(
        config.apiurl, 
        urllib.urlencode({'status': data}),
        {'User-agent': 'archbot/1.0'})

    ## perform the http post
    try:
        logger.debug('posting dent')
        output = opener.open(request).read()
    except urllib2.HTTPError, e:
        logger.error('failure. reason: %s', e.code)
        logger.exception('exception:')
        sys.exit(1)
    except urllib2.URLError, e:
        logger.error('failure. reason: %s', e.reason)
        logger.exception('exception:')
        sys.exit(1)
    else:
        logger.debug('dent posted')
        reply = json.loads(output)
        print "post-id: %d , %s" % (reply['id'],reply['text'])

# setup a null logger so we don't spew junk if a parent 
# logger isn't configured
h = NullLoggingHandler()
logging.getLogger('botlibs').addHandler(h)

