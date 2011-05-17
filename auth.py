#!/usr/bin/env python
#
# Copyright 2011 Ezox Systems, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import time
import urllib
import cgi
import logging

from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from google.appengine.ext import db
from google.appengine.api import urlfetch

import oauth2 as oauth

SETTINGS = {'APP': 'superlarp-sk',
            'CONSUMER_KEY': 'superlarp-sk.appspot.com',
            'CONSUMER_SECRET': '7DYB6MJ2s-IQcd7VJYJUmcct'}

OAUTH_URLS = {'OAuthGetRequestToken': 'https://superlarp-sk.appspot.com/_ah/OAuthGetRequestToken',
              'OAuthAuthRequestToken': 'https://superlarp-sk.appspot.com/_ah/OAuthAuthorizeToken',
              'OAuthGetAccessToken': 'https://superlarp-sk.appspot.com/_ah/OAuthGetAccessToken',
              'testrequest': 'https://superlarp-sk.appspot.com/'}

class Tokens(db.Model):
    request_token = db.TextProperty()
    token = db.TextProperty()

class AuthorizeHandler(webapp.RequestHandler):
    """Handle getting oauth token and storing with user's info."""
    def get(self):
        params = {
            'oauth_version': "1.0",
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_timestamp': int(time.time()),
            'oauth_callback': 'https://superlarp-sk.appspot.com/auth/finalize',
            'oauth_consumer_key': SETTINGS['CONSUMER_KEY'],
            'oauth_signature_method': 'HMAC-SHA1',
        }

        self.response.out.write('<br/><br/>params = ' + str(params))
        
        url = OAUTH_URLS['OAuthGetRequestToken']

        consumer = oauth.Consumer(key=SETTINGS['CONSUMER_KEY'],
                                  secret=SETTINGS['CONSUMER_SECRET'])
        
        self.response.out.write('<br/><br/>consumer =' + str(consumer))
        self.response.out.write('<br/><br/>url =' + str(url))
                                  
        request = oauth.Request(method='POST', url=url, parameters=params)
        request.sign_request(oauth.SignatureMethod_HMAC_SHA1(),
                             consumer, None)
                             

        params['oauth_signature_method'] = request['oauth_signature_method']
        params['oauth_signature'] = request['oauth_signature']

        result = urlfetch.fetch(url, payload=urllib.urlencode(params),
                                method='POST')
        
        self.response.out.write('<br/><br/>params = ' + str(params))                 

        if result.status_code == 200:
            oauth_token = cgi.parse_qs(result.content)
            user = Tokens(key_name='token')
            user.request_token = chr(30).join('%s%s%s'
                % (key, chr(31), value[0]) for key, value in oauth_token.iteritems())
            user.put()
            url = '%s?oauth_token=%s' % (
                OAUTH_URLS['OAuthAuthRequestToken'],
                oauth_token['oauth_token'][0])
            self.redirect(url)
            return
        else:
            logging.error('Failed to get request token.')
            logging.error(result.status_code)
            logging.error(result.content)

        self.response.out.write('<br/><br/>Something bad happened.')


class FinalizeAuthHandler(webapp.RequestHandler):
    """Handle exchange the oauth request token for an access token."""
    def get(self):
        authed = False
        oauth_token = self.request.get('oauth_token')
        oauth_verifier = self.request.get('oauth_verifier')

        params = {
            'oauth_version': "1.0",
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_timestamp': int(time.time()),
            'oauth_consumer_key': SETTINGS['CONSUMER_KEY'],
            'oauth_token': oauth_token,
            'oauth_verifier': oauth_verifier,
            'oauth_signature_method': 'HMAC-SHA1'
        }

        url = OAUTH_URLS['OAuthGetAccessToken']

        user = Tokens.get_by_key_name('token')

        token_data = dict(item.split(chr(31))
                            for item in user.request_token.split(chr(30)))
        token = oauth.Token(key=token_data['oauth_token'],
                            secret=token_data['oauth_token_secret'])
        consumer = oauth.Consumer(key=SETTINGS['CONSUMER_KEY'],
                                  secret=SETTINGS['CONSUMER_SECRET'])
        request = oauth.Request(method='POST', url=url, parameters=params)
        request.sign_request(oauth.SignatureMethod_HMAC_SHA1(),
                             consumer, token)

        params['oauth_signature_method'] = request['oauth_signature_method']
        params['oauth_signature'] = request['oauth_signature']

        result = urlfetch.fetch(url, method='POST',
                                payload=urllib.urlencode(params))
        if result.status_code == 200:
            authed = True
            token_data = cgi.parse_qs(result.content)
            user.token = chr(30).join('%s%s%s' % (key, chr(31), value[0])
                                        for key, value in token_data.iteritems())
            user.request_token = None
            user.put()
        else:
            logging.error('Failed to get access token.')
            logging.error(result.status_code)
            logging.error(result.content)
            return

        self.response.out.write('you been authed: %s' % (authed,))


class AuthedRequestHandler(webapp.RequestHandler):
    """Make an Authed request to the app."""
    def get(self):
        user = Tokens.get_by_key_name('token')

        token_data = dict(item.split(chr(31))
                            for item in user.token.split(chr(30)))

        oauth_token = token_data['oauth_token']
        oauth_verifier = token_data['oauth_token_secret']

        token = oauth.Token(key=oauth_token,
                            secret=oauth_verifier)
        consumer = oauth.Consumer(key=SETTINGS['CONSUMER_KEY'],
                                  secret=SETTINGS['CONSUMER_SECRET'])

        params = {
            'oauth_version': "1.0",
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_timestamp': int(time.time()),
            'oauth_consumer_key': SETTINGS['CONSUMER_KEY'],
            'oauth_token': oauth_token,
            'oauth_signature_method': 'HMAC-SHA1'
        }

        url = OAUTH_URLS['testrequest']

        request = oauth.Request(method='GET', url=url, parameters=params)
        request.sign_request(oauth.SignatureMethod_HMAC_SHA1(),
                             consumer, token)

        params['oauth_signature_method'] = request['oauth_signature_method']
        params['oauth_signature'] = request['oauth_signature']

        full_url = '%s?%s' % (url, urllib.urlencode(params))

        result = urlfetch.fetch(full_url, method='GET')

        if result.status_code == 200:
            self.response.out.write(result.content)
        else:
            logging.error('Failed to get access token.')
            logging.error(result.status_code)
            logging.error(result.content)
            self.response.out.write('failure')
            return

##############################################################################
##############################################################################
application = webapp.WSGIApplication([('/auth/get', AuthorizeHandler),
                                      ('/auth/finalize', FinalizeAuthHandler),
                                      ('/auth/test', AuthedRequestHandler)],
                                       debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
