# ============================================================================
# Copyright (c) 2011, SuperKablamo, LLC.
# All rights reserved.
# info@superkablamo.com
#
# api.py defines the RequestHandlers and Methods for the API.  See the Wiki
# on GitHub for how to use the API.
#
# ============================================================================

############################# SK IMPORTS #####################################
############################################################################## 
import models
import rules
import utils

from model import character
from model import party
from settings import *

############################# GAE IMPORTS ####################################
##############################################################################
import os
import logging

from django.utils import simplejson
from google.appengine.api import oauth
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

############################# CODES ##########################################
##############################################################################
API200 = {'status': '200 OK', 'code': '/api/status/ok'}
API201 = {'status': '201 Created', 'code': '/api/status/ok'}
API400 = {'status': '400 Bad Request', 'code': '/api/status/error'}
API401 = {'status': '401 Unauthorized', 'code': '/api/status/error'}
API404 = {'status': '404 Not Found', 'code': '/api/status/error'}
API405 = {'status': '405 Method Not Allowed', 'code': '/api/status/error'}
API422 = {'status': '422 Unprocessable Entity', 'code': '/api/status/error'}
API500 = {'status': '500 Internal Server Error', 'code': '/api/status/error'}
MSG = 'message'

############################# REQUEST HANDLERS ############################### 
##############################################################################
class APIBase(webapp.RequestHandler):
    
    def get_user(self):
        '''Returns a User object associated with a Google account.
        '''
        _trace = TRACE+'APIBase:: get_user() '
        logging.info(_trace)
        user = users.get_current_user()
        logging.info(_trace+'user = '+ str(user.email()))            
        return user        
        
    def authenticate(self):
        '''Returns an authenticated User.  Or an Exception if the User is not
        properly authenticated.
        '''
        _trace = TRACE+'APIBase:: authenticate() '
        logging.info(_trace)
        user = None
        try:
            user = oauth.get_current_user()
            logging.info(_trace + 'user = ' + str(user))
        except oauth.InvalidOAuthParametersError:
            logging.error(_trace + 'InvalidOAuthParametersError! The client provided OAuth parameters with the request, but they are invalid.')
            self.error(401)
        except oauth.InvalidOAuthTokenError:
            logging.error(_trace + 'InvalidOAuthTokenError! The client provided an OAuth token with the request, but it has been revoked by the user, or is otherwise invalid.')
            self.error(401)            
        except oauth.OAuthServiceFailureError:
            logging.error(_trace + 'OAuthServiceFailureError! There was an internal error with the OAuth service.')
            self.error(401)            
      
        return user
    
    def error(self, code):
        '''Overide RequestHandler.error to return custom error templates.
        '''
        _trace = TRACE+'APIBase:: error() '
        logging.error(_trace)        
        self.response.clear()
        self.response.set_status(code)
        if code == 400:
            r = API400
        if code == 401:
            r = API401
        elif code == 404:
            r = API404
        elif code == 405:
            r = API405
        elif code == 422:
            r = API422
        else:
            r = API500
        return self.response.out.write(simplejson.dumps(r))                  
        
class APICreatePlayerCharacters(APIBase):
    def post(self):
        '''Creates a new Player Character.
        '''
        _trace = TRACE+'APICreatePlayerCharacters:: post() '
        logging.info(_trace)        
        user = self.get_user()
        if user is None:
            r = API404
            r[MSG] = 'User not found.'
            return self.response.out.write(simplejson.dumps(r))            
        key = self.request.get('key')
        logging.info(_trace+'key = '+key)  
        template = db.get(key)
        if template is not None:
            try:
                name = self.request.get('name')
            except AttributeError:
                r = API400
                r[MSG] = 'Missing \'name\' parameter.' 
                return self.response.out.write(simplejson.dumps(r))                     
            logging.info(_trace+'name = '+name)                           
            player = character.createPlayerFromTemplate(template, name, user)
            r = API201
            r[MSG] = 'Fortune favors the bold!'
            r[player.class_name()] = character.getJSONPlayer(player)
        else:    
            r = API404
            r[MSG] = 'Template not found for key '+key+' .'        
        return self.response.out.write(simplejson.dumps(r)) 
        
class APIPlayerCharacters(APIBase):
    def get(self, key):
        '''Returns a PlayerCharacter provided a key.
        '''
        _trace = TRACE+'APIPlayerCharacters:: get() '
        logging.info(_trace)        
        _character = db.get(key)
        if _character is not None and _character.class_name() == 'Player':
            r = API200
            r[MSG] = 'A hero returns!'
            r[_character.class_name()] = character.getJSONPlayer(_character)
        else:
            r = API404
            r[MSG] = 'PlayerCharacter not found for key '+key+' .'                
        return self.response.out.write(simplejson.dumps(r)) 
    
    # TODO: NOT TESTED
    def put(self, key):
        '''Updates a PlayerCharacter and Returns the new PlayerCharacter data. 
        '''
        _trace = TRACE+'APIPlayerCharacters:: put() '
        logging.info(_trace)        
        character = db.get(key) 
        if character is not None:
            # TODO
            pass
        else:
            r = API404
            r[MSG] = 'PlayerCharacter not found for key '+key+' .'        
        return self.response.out.write(simplejson.dumps(r)) 
    
    # TODO: NOT TESTED        
    def delete(self, key):
        '''Deletes a PlayerCharacter. 
        '''
        _trace = TRACE+'APIPlayerCharacters:: delete() '
        logging.info(_trace)        
        character = db.get(key) 
        if character is not None and character.class_name() == 'Character':
            character.delete()
            r = API200
            r[MSG] = 'The funeral pyre burns bright.'
        else:
            r = API404
            r[MSG] = 'PlayerCharacter not found for key '+key+' .'        
        return self.response.out.write(simplejson.dumps(r))

class APINonPlayerCharacters(APIBase):
    def get(self, key):
        '''Returns a NonPlayerCharacter provided a key.
        '''
        _trace = TRACE+'APINonPlayerCharacters:: get() '
        logging.info(_trace)        
        _character = db.get(key)
        if _character is not None and _character.class_name() == 'Monster':
            r = API200
            r[MSG] = 'A villian returns!'
            r[_character.class_name()] = character.getJSONNonPlayer(_character)
        else:
            r = API404
            r[MSG] = 'NonPlayerCharacter not found for key '+key+' .'              
        return self.response.out.write(simplejson.dumps(r)) 
    
    # TODO: NOT TESTED      
    def put(self, key):
        '''Updates a NonPlayerCharacter and Returns the new 
        NonPlayerCharacter data. 
        '''
        _trace = TRACE+'APINonPlayerCharacters:: put() '
        logging.info(_trace)        
        character = db.get(key) 
        if character is not None:
            # TODO
            pass
        else:
            r = API404
            r[MSG] = 'NonPlayerCharacter not found for key '+key+' .'              
        return self.response.out.write(simplejson.dumps(r))
    
    # TODO: NOT TESTED      
    def delete(self, key):
        '''Deletes a NonPlayerCharacter. 
        '''
        _trace = TRACE+'APINonPlayerCharacters:: delete() '
        logging.info(_trace)        
        character = db.get(key) 
        if character is not None and character.class_name() == 'Character':
            character.delete()
            r = API200
            r[MSG] = 'The world is a better place now that this one is gone.'
        else:
            r = API404
            r[MSG] = 'NonPlayerCharacter not found for key '+key+' .'              
        return self.response.out.write(simplejson.dumps(r))

class APITemplates(APIBase):
    def get(self, _class):
        '''Returns all PlayerCharacter or NonPlayerCharacterTemplates 
        available for use.
        '''
        _trace = TRACE+'APITemplates:: get() '
        logging.info(_trace)  
        user = self.get_user()
        if user is None:
            r = API404
            r[MSG] = 'User not found.'
            return self.response.out.write(simplejson.dumps(r))
        model = None
        _class_name = None
        if _class == 'pc':
            logging.info(_trace+'_class = pc')  
            templates = models.PlayerCharacterTemplate.all().fetch(100)    
            data = []
            for t in templates:
                json = {'key': str(t.key()),
                        'name': t.name, 
                        'race': t.race,
                        'cast': t.cast,
                        'level': t.level}
                        
                data.append(json)
            
            r = API200
            r[MSG] = 'A quiver of characters.'
            r['PlayerCharacterTemplates'] = data                  
        elif _class == 'npc':
            logging.info(_trace+'_class = npc')              
            templates = models.NonPlayerCharacterTemplate.all().fetch(100)    
            data = []
            for t in templates:
                json = {'key': str(t.key()),
                        'name': t.name,
                        'race': t.race,
                        'level': t.level,
                        'role': t.role,
                        'challenge': t.challenge,
                        'unique': t.unique}
                             
                data.append(json)
            
            r = API200
            r[MSG] = 'A quiver of monsters.'
            r['NonPlayerCharacterTemplates'] = data
        else:
            r = API400
            r[MSG] = 'Invalid class \'_class\', no templates found.'  
        
        return self.response.out.write(simplejson.dumps(r))

class APICreateParties(APIBase):
    def post(self):
        '''Creates and Returns a new Party.
        '''
        _trace = TRACE+'APICreateParties:: post() '
        logging.info(_trace)       
        key = self.request.get('key')
        lat = self.request.get('lat')
        lon = self.request.get('lon')
        if key is None:
            r = API400
            r[MSG] = 'Missing \'key\' parameter.'
        if lat is None:
            r = API400
            r[MSG] = 'Missing \'lat\' parameter.'
        if lon is None:
            r = API400
            r[MSG] = 'Missing \'lon\' parameter.'                        
        logging.info(_trace+'key ='+key)    
        logging.info(_trace+'lat = '+lat)    
        logging.info(_trace+'lon ='+lon)                    
        character = db.get(str(key))
        if character is not None or character.class_name() == 'Character':
            location = db.GeoPt(lat, lon)
            _party = party.createJSONParty(character, location)
            r = API201
            r[MSG] = 'It is gold and adventure you seek?'
            r['PlayerParty'] = _party
        else:
            r = API404
            r[MSG] = 'Character not found for key '+key+' .'
                
        return self.response.out.write(simplejson.dumps(r)) 
       
class APIParties(APIBase):
    def get(self, key):
        '''Returns the Party.
        '''
        _trace = TRACE+'APIParties:: get() '
        logging.info(_trace)        
        _party = db.get(key)
        if _party is not None: 
            if _party.class_name() in ['PlayerParty', 'NonPlayerParty']:
                r = API200
                r[MSG] = 'Adventure or Destruction a party makes.'
                r[_party.class_name()] = party.getJSONParty(_party)
        else:
            r = API404
            r[MSG] = 'Party not found for key '+key+' .'  
              
        return self.response.out.write(simplejson.dumps(r))
    
    def put(self, key):
        '''Adds a Character to a Party.
        '''
        _trace = TRACE+'APIParties:: put() '
        logging.info(_trace)        
        _party = db.get(key)        
        if _party is not None and _party.class_name() == 'Party':
            try:
                character_key = self.request.get('character_key')
            except AttributeError:
                r = API400
                r[MSG] = 'Missing \'character_key\' parameter.'
            
            character = db.get(character_key)
            if character is not None and character.class_name() == 'Character':
                _party = party.updateJSONParty(party, character)
                r = API200
                r[MSG] = 'The party grows stronger!'
                r[_party.class_name()] = _party
            else:
                  r = API404
                  r[MSG] = 'Character not found for key '+character_key+' .'                  
            
            r = API200
            r[MSG] = 'Adventure a party makes.'
            r[_party.class_name()] = party.getJSONParty(party)
        else:
            r = API404
            r[MSG] = 'Party not found for key '+key+' .'  
              
        return self.response.out.write(simplejson.dumps(r))
    
    def delete(self, key):
        '''Deletes a Party. 
        '''
        _trace = TRACE+'APIParties:: delete() '
        logging.info(_trace)        
        party = db.get(key) 
        if party is not None and party.class_name() == 'Party':
            party.delete()
            r = API200
            r[MSG] = 'The quest has been abandoned.'
        else:
            r = API404
            r[MSG] = 'Party not found for key '+key+' .'              
        
        return self.response.out.write(simplejson.dumps(r)) 

class APIPartyActions(APIBase):        
    def post(self, key, action):
        '''Invokes an action on a particular Party.
        '''
        _trace = TRACE+'APIParties:: post() '
        logging.info(_trace)  
        logging.info(_trace+'body = '+str(self.request.body))        
        _party = db.get(str(key))
        if _party is not None or _party.class_name() == 'Party':
            
            #Character attacks character(s) in Party Z using Item or Power      
            if action == 'attack':
                player_key = self.request.get('player_key')
                monster_keys = self.request.get_all('monsters')
                weapon_key = self.request.get('weapon_key')
                attack_key = self.request.get('attack_key')
                location = self.request.get('location')
                missing = utils.findMissingParams(self, 'player_key', 
                                                  'monster_keys', 'location')

                if missing is not None:
                    r = API400
                    r[MSG] = 'Required parameters not found:'+str(missing) 
                
                # Get Player    
                player = db.get(player_key)
                if player is None or player.class_name() != 'Player':
                    r = API404
                    r[MSG] = 'Player not found for player_key '+player_key+' .'                            
                    return self.response.out.write(simplejson.dumps(r))   
                
                # Both Power.Attack and Item.Weapon are considered an 'attack'
                
                # Get Power-Attack
                if len(attack_key) != 0:
                    logging.info(_trace+'getting Attack!')
                    attack = db.get(attack_key)                    
                    if attack is None or attack.class_name() != 'Attack':
                        r = API404
                        r[MSG] = 'Power not found for attack_key '+attack_key+' .'                            
                        return self.response.out.write(simplejson.dumps(r))
                
                # Get Item-Weapon        
                elif len(weapon_key) != 0:
                    logging.info(_trace+'getting Weapon!')
                    attack = db.get(weapon_key) 
                    if attack is None or attack.class_name() != 'Weapon':
                        r = API404
                        r[MSG] = 'Item not found for weapon_key '+attack_key+' .'                            
                        return self.response.out.write(simplejson.dumps(r))                                   
                
                # Get nothing - return Error
                else:
                    r = API404
                    r[MSG] = 'Missing parameter \'attack_key\' or \'power_key\'.'                            
                    return self.response.out.write(simplejson.dumps(r))                            
                
                # Get Monsters  
                monsters = db.get(monster_keys)
                for m in monsters:
                    if m is None or m.class_name() != 'Monster':
                        r = API404
                        r[MSG] = 'Monster not found for monster_key '+str(m)+'.'                            
                        return self.response.out.write(simplejson.dumps(r))
                        monsters.remove(m)
                
                damage = party.getJSONAttack(_party, monsters, 
                                             player, attack)
                
                r = API200
                r[MSG] = 'Smite thy enemies!'
                r['damage'] = damage                                                                             
                    
            # Character checkins in at a location seeking Parties, Traps or
            # Events.
            elif action == 'quest':
                logging.info(_trace+'action = quest')      
                player_key = self.request.get('player_key')
                location = self.request.get('location')
                if location is None or player_key is None:
                    r = API400
                    r[MSG] = 'Request is missing one or more parameters.' 
                    
                # Build location                
                geo_loc = utils.parseLocation(location)
                
                # Get Player
                player = db.get(str(player_key))
                logging.info(_trace+'player.class_name = '+player.class_name()) 
                if player is None or player.class_name() != 'Player':
                    r = API404
                    r[MSG] = 'Player not found for player_key '+player_key+' .'                            
                    return self.response.out.write(simplejson.dumps(r)) 
                    
                monster_party = party.getJSONQuest(_party, player, geo_loc)
                r = API200
                r[MSG] = 'Seeking fortune.'
                data = monster_party.json
                data['key'] = str(monster_party.key())
                r['NonPlayerParty'] = data
            
            #Character sends a message to character(s) in a Party.
            elif action == 'greet':
                # TODO:: get character a, party a, party b, location, skill.                 
            
                party.sendPartyMessage(party, player, message)
                r = API200
                r[MSG] = 'Do you speak Draconic?'
                
            else:
                r = API400
                r[MSG] = 'Invalid action \'action\'.'       

        else:
            r = API404
            r[MSG] = 'Party not found for key '+key+' .'
                    
        return self.response.out.write(simplejson.dumps(r)) 

######################## METHODS #############################################
##############################################################################
                     
##############################################################################
##############################################################################
application = webapp.WSGIApplication([(r'/api/playercharacters', 
                                       APICreatePlayerCharacters),
                                      (r'/api/playercharacters/(.*)', 
                                       APIPlayerCharacters),
                                      (r'/api/nonplayercharacters/(.*)', 
                                       APINonPlayerCharacters),
                                      (r'/api/templates/(.*)', 
                                       APITemplates),
                                      (r'/api/parties', 
                                       APICreateParties),
                                      (r'/api/parties/(.*)/(.*)', 
                                       APIPartyActions),
                                      (r'/api/parties/(.*)', 
                                       APIParties)
                                     ],
                                     debug=DEBUG)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
