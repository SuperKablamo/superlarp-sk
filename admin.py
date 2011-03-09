#
# Copyright 2010 SuperKablamo, LLC
# info@superkablamo.com
#

############################# SK IMPORTS #####################################
############################################################################## 
import rules
import seed

from settings import *

############################# GAE IMPORTS ####################################
##############################################################################
import os
import logging
import urllib2

from django.utils import simplejson
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

############################# REQUEST HANDLERS ############################### 
##############################################################################   
class Admin(webapp.RequestHandler):
    def get(self):
        template_values = {
            'text': 'Hello World'
        }
        generate(self, 'admin.html', template_values)        

class InitAdmin(webapp.RequestHandler):
    def get(self):
        template_values = {
            'text': 'Hello World'
        }
        generate(self, 'admin_init.html', template_values)        

    def post(self, method):
        logging.info('################## InitAdmin:: post() ####################')
        if method == "races": 
            r = seed.seedRaces()
        elif method == "casts": 
            r = seed.seedCasts()
        elif method == "bonuses": 
            r = seed.seedBonuses()            
        #else: r = API404
        #return self.response.out.write(simplejson.dumps(r))


class CastAdmin(webapp.RequestHandler):
    def get(self):
        template_values = {
            'text': 'Hello World'
        }
        generate(self, 'admin_cast.html', template_values)        

class RaceAdmin(webapp.RequestHandler):
    def get(self):
        template_values = {
            'text': 'Hello World'
        }
        generate(self, 'admin_race.html', template_values)

class ArmorAdmin(webapp.RequestHandler):
    def get(self):
        template_values = {
            'text': 'Hello World'
        }
        generate(self, 'admin_armor.html', template_values)

class WeaponAdmin(webapp.RequestHandler):
    def get(self):
        template_values = {
            'text': 'Hello World'
        }
        generate(self, 'admin_weapon.html', template_values)

class PowerAdmin(webapp.RequestHandler):
    def get(self):
        template_values = {
            'text': 'Hello World'
        }
        generate(self, 'admin_power.html', template_values)                        
        
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
application = webapp.WSGIApplication([('/admin/', Admin),
                                      ('/admin/init', InitAdmin),
                                      (r'/admin/init/(.*)', InitAdmin),
                                      ('/admin/cast', CastAdmin),
                                      ('/admin/race', RaceAdmin),
                                      ('/admin/armor', ArmorAdmin),
                                      ('/admin/weapon', WeaponAdmin),
                                      ('/admin/power', PowerAdmin)],
                                       debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()