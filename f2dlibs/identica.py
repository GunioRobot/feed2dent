"""
identica module

this module contains the following methods:

dent      -- Method to post data to identica.
"""

###
### imports
import sys
import logging
import urllib
import urllib2

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
### method defs
def dent(config, data):
    """post text to identi.ca"""
    logger = logging.getLogger('botlibs.identica.dent')
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


