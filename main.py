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
        template_values = {
            'text': 'Hello World'
        }
        generate(self, 'main.html', template_values)        

######################## METHODS #############################################
##############################################################################
def generate(self, template_name, template_values):
    directory = os.path.dirname(__file__)
    path = os.path.join(directory, 
                        os.path.join('templates', template_name))

    self.response.out.write(template.render(path, 
                                            template_values, 
                                            debug=DEBUG))
                                            
##############################################################################
##############################################################################
application = webapp.WSGIApplication([(r'/.*', MainHandler)],
                                       debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()