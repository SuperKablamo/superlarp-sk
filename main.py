# ============================================================================
# Copyright (c) 2011, SuperKablamo, LLC.
# All rights reserved.
# info@superkablamo.com
#
#
#
# ============================================================================

############################# SK IMPORTS #####################################
############################################################################## 
import rules

from settings import *

############################# GAE IMPORTS ####################################
##############################################################################
import os
import logging

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

############################# REQUEST HANDLERS ############################### 
##############################################################################   
class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write('Hello world!')

######################## METHODS #############################################
##############################################################################

##############################################################################
##############################################################################
application = webapp.WSGIApplication([(r'/.*', MainHandler)],
                                       debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()