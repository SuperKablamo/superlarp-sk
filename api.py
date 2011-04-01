# ============================================================================
# Copyright (c) 2011, SuperKablamo, LLC.
# All rights reserved.
# info@superkablamo.com
#
# API.py defines the RequestHandlers and Methods for the API.  See the Wiki
# on GitHub for how to use the API.
#
# ============================================================================

############################# SK IMPORTS #####################################
############################################################################## 
import models
import utils

from model import character
from settings import *

############################# GAE IMPORTS ####################################
##############################################################################
import os
import logging

from django.utils import simplejson
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

############################# CODES ##########################################
##############################################################################

API200 = {"status": "200 OK", "code": "/api/status/ok"}
API403 = {"status": "403 Forbidden", "code": "/api/status/error"}
API404 = {"status": "404 Not Found", "code": "/api/status/error"}
API500 = {"status": "500 Internal Server Error", "code": "/api/status/error"}
MSG = 'message'

############################# REQUEST HANDLERS ############################### 
##############################################################################
class APIPlayer(webapp.RequestHandler):
    """Provides API access to Player Character data.  Responses are in JSON.
    """
    def get(self, player_id):
        logging.info(TRACE+'APIPlayer:: get()')
        i = utils.strToInt(player_id)
        player = models.PlayerCharacter.get_by_id(i)
        r = character.getJSONPlayer(player)
        return self.response.out.write(simplejson.dumps(r))
        
    def post(self, method):
        logging.info(TRACE+'APIPlayer:: post()')
        if method == 'new': 
            r = createPlayer(self)
        else: 
            r = API404
            r[MSG] = 'New Player was not created.'
        return self.response.out.write(simplejson.dumps(r)) 

class APINonPlayer(webapp.RequestHandler):
    """Provides API access to NonPlayer Character data. Responses are in JSON.
    """
    def get(self, nonplayer_id):
        logging.info(TRACE+'APINonPlayer:: get()')
        i = utils.strToInt(nonplayer_id)
        nonplayer = models.NonPlayerCharacter.get_by_id(i)
        r = character.getJSONNonPlayer(nonplayer)
        return self.response.out.write(simplejson.dumps(r))        
    
    def post(self, method):
        logging.info(TRACE+'APINonPlayer:: post()')
        if method == 'new': 
            r = character.createNonPlayer(self)
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
        
class APIPlayerItem(webapp.RequestHandler):
    """Provides API access to Player Item data.  Responses are in JSON.
    """
    def get(self, type, method):
        r = API404
        return self.response.out.write(simplejson.dumps(r)) 

    def post(self, model, method):
        logging.info(TRACE+'APIPlayerItem:: post()')
        r = API404
        if model == models.WPN.lower():
            if method == "add":
                player_id = self.request.get('player_id')
                name = self.request.get('weapon_name')
                player = character.addToPlayer(models.Weapon, name, player_id)
                if player is not None:
                    r =  character.getJSONPlayer(player)  
                else:
                    r[MSG] = 'Item was not added to Player.'                       
        return self.response.out.write(simplejson.dumps(r))   

class APIPlayerPower(webapp.RequestHandler):
    """Provides API access to Player Power data.  Responses are in JSON.
    """
    def get(self, type, method):
        r = API404
        return self.response.out.write(simplejson.dumps(r)) 

    def post(self, model, method):
        logging.info(TRACE+'APIPlayerPower:: post()')
        r = API404
        if model == models.ATT.lower():
            if method == "add":
                player_id = self.request.get('player_id')
                name = self.request.get('attack_name')
                player = character.addToPlayer(models.Attack, name, player_id)
                if player is not None:
                    r =  character.getJSONPlayer(player) 
                else:
                    r['message'] = 'Power was not added to Player.'             
        return self.response.out.write(simplejson.dumps(r)) 
            
               
######################## METHODS #############################################
##############################################################################
def logEncounterCheck(player_party, encounter=False):
    """
    {'encounter': {'encounters': 23, 'uniques': 2, 'start_time': POSIX
                   'last_encounter': {'time_since': POSIX, 'checks': 9}}}
    """
    return None
                     
##############################################################################
##############################################################################
application = webapp.WSGIApplication([(r'/api/character/player/item/(.*)/(.*)', 
                                       APIPlayerItem),
                                      (r'/api/character/player/power/(.*)/(.*)', 
                                       APIPlayerPower), 
                                      (r'/api/character/player/(.*)', 
                                       APIPlayer),
                                      (r'/api/character/nonplayer/(.*)', 
                                       APINonPlayer),
                                      (r'/api/(.*)', APIError)
                                     ],
                                     debug=True)

'''
api methods:
checkin - update location, check for monsters
create player
add item to player (include cost)
get loot - monster killed
transfer item to other player
attack monster
attack player





'''




def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
