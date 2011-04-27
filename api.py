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
import rules
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
        r = API200
        r[MSG] = 'A hero?'        
        r[player.class_name()] = character.getJSONPlayer(player)
        return self.response.out.write(simplejson.dumps(r))
        
    def post(self, method):
        logging.info(TRACE+'APIPlayer:: post()')
        if method == 'new': 
            r = API200
            player = character.createPlayer(self)
            r[MSG] = 'This one won\'t last long I fear.'
            r[player.class_name()] = character.getJSONPlayer(player)
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
        r = API200
        r[nonplayer.class_name()] = character.getJSONNonPlayer(nonplayer)
        return self.response.out.write(simplejson.dumps(r))        
    
    def post(self, method):
        logging.info(TRACE+'APINonPlayer:: post()')
        if method == 'new': 
            r = API200
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
            if method == 'add':
                player_id = self.request.get('player_id')
                name = self.request.get('weapon_name')
                player = character.addToPlayer(models.Weapon, name, player_id)
                r = API200
                if player is not None:
                    r[MSG] = 'Another tool for the trade?'
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
                r = API200
                if player is not None:
                    r[MSG] = 'With great power comes great responsibility.'
                    r[player.class_name()] =  character.getJSONPlayer(player) 
                else:
                    r[MSG] = 'Power was not added to Player.'             
        return self.response.out.write(simplejson.dumps(r)) 

class APIPlayerAction(webapp.RequestHandler):
    """Provides API access to Player Actions.  Responses are in JSON.
    """
    def get(self, type, method):
        r = API404
        return self.response.out.write(simplejson.dumps(r)) 

    def post(self, action):
        _trace = TRACE+'APIPlayerAction:: post() '
        logging.info(_trace)
        r = API404
        player_id = self.request.get('player_id')
        action_name = self.request.get('action_name')
        target_ids = self.request.get('target_ids')
        logging.info('action = '+action)        
        logging.info(_trace+'player_id = '+player_id)
        logging.info(_trace+'action_name = '+action_name)
        logging.info(_trace+'target_ids = '+target_ids)
        
        # Get the Player and Monsters in one get, and sort them 
        keys = []
        player_key = db.Key.from_path('PlayerCharacter', player_id)
        keys.append(player_key)
        for t in target_ids:
            monster_key = db.Key.from_path('Monster', t)
            keys.append(monster_key)
        entities = db.get(keys)  
        player = None
        monsters = []  
        for e in entities:
            if e.kind() == 'PlayerCharacter':
                player = e
                logging.info('player.name = '+player.name)
            if e.kind() == 'Monster':
                monsters.append(e)
                logging.info('monster.name = '+e.name)
                    
        # Determine the type of Action being used
        if action == 'weapon':
            weapons = player.actions['weapons']
            weapon = None
            for w in weapons:
                if w.name == action_name:
                    weapon = w
            
            damage = rules.rollAttack(player, monsters, weapon)
            r = API200
            r['damage'] = damage
                     
        if action == 'attack':
            powers = player.actions['powers']
            power = None
            for p in powers:
                if p.name == action_name:
                    power = p            
                    
            damage = rules.rollAttack(player, monsters, power)  
            r = API200
            r['damage'] = damage                      

        return self.response.out.write(simplejson.dumps(r))


class APIParty(webapp.RequestHandler):
    """Provides API access to Party, PlayerParty and NonPlayerParty data.
    Responses are in JSON.
    """
    def get(self, method):
        r = API404
        logging.info(TRACE+'APIParty:: get()')
        if method == 'encounter': 
            party_id = self.request.get('party_id')
            lat = self.request.get('lat')
            lon = self.request.get('lon')
            geo_pt = db.GeoPt(lat, lon)
            id_ = utils.strToInt(party_id)
            player_party = models.PlayerParty.get_by_id(id_)
            # Return Error if player_party is not found.
            if player_party is None:
                r[MSG] = 'Invalid party_id!'
                return self.response.out.write(simplejson.dumps(r))
                
            monster_party = rules.rollEncounter(player_party, geo_pt)
            r = API200
            if monster_party is not None:
                r[MSG] = 'Cowards run, Heroes fight!'
                r[monster_party.class_name()] = monster_party.json
            else:
                r[MSG] = 'No monsters found.'
                r['NonPlayerParty'] = None    
        else: 
            r[MSG] = method + ' is not a valid resource.'
        return self.response.out.write(simplejson.dumps(r))
    
    def post(post, method):
        return None    
               
######################## METHODS #############################################
##############################################################################
def logEncounterCheck(player_party, encounter=False):
    """
    {'encounters': {'count': 23, 'uniques': 2, 'start_time': POSIX
                   'last_encounter': {'time_since': POSIX, 'checks': 9}}}
    """
    return None
                     
##############################################################################
##############################################################################
application = webapp.WSGIApplication([(r'/api/character/player/item/(.*)/(.*)', 
                                       APIPlayerItem),
                                      (r'/api/character/player/power/(.*)/(.*)', 
                                       APIPlayerPower), 
                                      (r'/api/character/player/action/(.*)', 
                                       APIPlayerAction),                                       
                                      (r'/api/character/player/(.*)', 
                                       APIPlayer),
                                      (r'/api/character/nonplayer/(.*)', 
                                       APINonPlayer),
                                      (r'/api/party/(.*)', APIParty), 
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
