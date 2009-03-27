"""
archbot library

this package contains the following methods:

tighturlify -- Method to turn a url into a bit.ly shortened url.
mkdent      -- Method to post data to identica.
"""

###
### imports
import sys
import re
import urllib
import urllib2
import logging
import lxml

###
### method defs
def ify(config, url):
    """use tighturl to shorten a url and return the shorter version"""
    logger = logging.getLogger('botlibs.tighturl.ify')
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

