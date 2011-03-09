#
# Copyright 2010 SuperKablamo, LLC
# info@superkablamo.com
#

############################# SK IMPORTS #####################################
############################################################################## 
import models

from settings import *

############################# GAE IMPORTS ####################################
##############################################################################
import os
import logging

from django.utils import simplejson
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

############################# REQUEST HANDLERS ############################### 
##############################################################################
class APIPlayer(webapp.RequestHandler):
    """Provides API access to Player Character data.  Responses are in JSON.
    """
    def get(self, method):
        logging.info('################### APIPlayer:: get() ################')
    
    def post(self, method):
        logging.info('################## APIPlayer:: post() ################')
        if method == "new": 
            r = createPlayer(self)
        else: r = API404
        return self.response.out.write(simplejson.dumps(r)) 

class APIError(webapp.RequestHandler):
    """Provides basic API error Response in JSON.
    """
    def get(self, foo):
        r = API404
        return self.response.out.write(simplejson.dumps(r)) 

    def post(self, foo):
        r = API404
        return self.response.out.write(simplejson.dumps(r)) 
               
######################## METHODS #############################################
##############################################################################
def createPlayer(self):
    
    
    player = models.Player(name=self.request.get('name'),
                           level=1,
                           race=self.request.get('race'),
                           cast=self.request.get('cast'),
                           alignment=self.request.get('alignment'),
                           strength

"""
class Character(polymodel.PolyModel):
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)    
    name = db.StringProperty(required=True)
    level = db.IntegerProperty(required=True, default=1)
    race = db.StringProperty(required=True)
    alignment = db.StringProperty(required=True)
    size = db.StringProperty(required=True)
    experience = db.IntegerProperty(required=True, default=0)
    hit_points = db.IntegerProperty(required=True)
    speed = db.IntegerProperty(required=True)
    scores = JSONProperty(required=True)
    powers = db.ListProperty(db.Key, required=True, default=None)
    items = db.ListProperty(db.Key, required=True, default=None)
    equipped = db.ListProperty(db.Key, required=True, default=None)
        
class PlayerCharacter(Character):
    cast = db.StringProperty(required=True)
    height = db.IntegerProperty(required=True)
    weight = db.IntegerProperty(required=True)    
 """   
                        
##############################################################################
##############################################################################
application = webapp.WSGIApplication([(r'/api/character/player/(.*)', APIPlayer),
                                      (r'/api/character/nonplayer/(.*)', APINonPlayer),
                                      (r'/api/(.*)', APIError)
                                     ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
