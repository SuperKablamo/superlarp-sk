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
from google.appengine.api import oauth
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

############################# CODES ##########################################
##############################################################################
API200 = {'status': '200 OK', 'code': '/api/status/ok'}
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
    _trace = TRACE+'APIBase:: '
    logging.info(_trace)
    @property
    def current_user(self):
        '''Returns an authenticated User.  Or an Exception if the User is not
        properly authenticated.
        '''
        try:
            user = oauth.get_current_user()
            logging.info(_trace + 'user = ' + str(user))
            return user
        except oauth.OAuthRequestError:    
            logging.info(_trace + 'OAuthRequestError!')
            raise
    
    def error(self, code):
        '''Overide RequestHandler.error to return custom error templates.
        '''
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
        key = self.request.get('key')
        template = db.get('key')
        if template is not None:
            try:
                name = self.request.get('name')
            except AttributeError:
                r = API400
                r[MSG] = 'Missing \'name\' parameter.'              
            player = character.createPlayerFromTemplate(key, name, user)
            r = API200
            r[MSG] = 'Fortune favors the bold!'
            r[character.class_name()] = character.getJSONPlayer(player)
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
        character = db.get(key)
        if character is not None and character.class_name() == 'Character':
            r = API200
            r[MSG] = 'A hero returns!'
            r[character.class_name()] = character.getJSONPlayer(player)
        else:
            r = API404
            r[MSG] = 'PlayerCharacter not found for key '+key+' .'  
              
        return self.response.out.write(simplejson.dumps(r)) 
    
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
        character = db.get(key)
        if character is not None and character.class_name() == 'Character':
            r = API200
            r[MSG] = 'A villian returns!'
            r[character.class_name()] = character.getJSONNonPlayer(player)
        else:
            r = API404
            r[MSG] = 'NonPlayerCharacter not found for key '+key+' .'  
              
        return self.response.out.write(simplejson.dumps(r)) 
    
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
        model = None
        _class_name = None
        if _class = 'pc':
            templates = models.PlayerCharacterTemplates.all().fetch(100)    
            data = []
            for t in templates:
                data[t.key().id_or_name()] = {'name': t.name, 
                                              'race': t.race,
                                              'cast': t.cast,
                                              'level': t.level}
            
             r = API200
             r[MSG] = 'A quiver of characters.'
             r['PlayerCharacterTemplates'] = data
                                                          
        elif _class = 'npc':
            templates = models.NonPlayerCharacterTemplates.all().fetch(100)    
            data = []
            for t in templates:
                data[t.key().id_or_name()] = {'name': t.name, 
                                              'race': t.race,
                                              'level': t.level,
                                              'role': t.role,
                                              'challenge': t.challenge,
                                              'unique': t.unique}
            
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
        try:
            key = self.request.get('character_key')
        except AttributeError:
            r = API400
            r[MSG] = 'Missing \'character_key\' parameter.'
        
        character = db.get(key)
        if character is not None and character.class_name() == 'Character':
            party = party.createJSONParty(character)
            r = API200
            r[MSG] = 'It is gold and adventure you seek?'
            r[party.class_name()] = party
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
        party = db.get(key)
        if party is not None and party.class_name() == 'Party':
            r = API200
            r[MSG] = 'Adventure a party makes.'
            r[party.class_name()] = party.getJSONParty(party)
        else:
            r = API404
            r[MSG] = 'Party not found for key '+key+' .'  
              
        return self.response.out.write(simplejson.dumps(r))
    
    def put(self, key):
        '''Adds a Character to a Party.
        '''
        _trace = TRACE+'APIParties:: put() '
        logging.info(_trace)        
        party = db.get(key)        
        if party is not None and party.class_name() == 'Party':
            try:
                character_key = self.request.get('character_key')
            except AttributeError:
                r = API400
                r[MSG] = 'Missing \'character_key\' parameter.'
            
            character = db.get(character_key)
            if character is not None and character.class_name() == 'Character':
                party = party.updateJSONParty(party, character)
                r = API200
                r[MSG] = 'The party grows stronger!'
                r[party.class_name()] = party
            else:
                  r = API404
                  r[MSG] = 'Character not found for key '+character_key+' .'                  
            
            r = API200
            r[MSG] = 'Adventure a party makes.'
            r[party.class_name()] = party.getJSONParty(party)
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
        
    def post(self, key, action):
        '''Invokes an action on a particular Party.
        '''
        _trace = TRACE+'APIParties:: post() '
        logging.info(_trace)  
        party = db.get(key)
        if party is not None and party.class_name() == 'Party':
            
            '''Character attacks character(s) in Party Z using Item or Power      
            '''
            if action == 'attack':
                try:
                    player_key = self.request.get('player_key')
                    enemy_character_keys self.request.get('character_keys')
                    attack_type = self.request.get('attack_type')
                    attack_key = self.request.get('attack_key')
                except AttributeError:
                    r = API400
                    r[MSG] = 'Request is missing one or more parameters.' 
                
                # Get Player
                player = db.get(player_key)
                if player is None or player.class_name() != 'Character':
                    r = API404
                    r[MSG] = 'Player not found for player_key '+player_key+' .'                            
                    return self.response.out.write(simplejson.dumps(r))   
                
                # Get Attack                
                attack = db.get(attack_key)
                if attack_type == 'item':
                    if attack is None or attack.class_name() != 'Item':
                        r = API404
                        r[MSG] = 'Item not found for attack_key '+attack_key+' .'                            
                        return self.response.out.write(simplejson.dumps(r))
                elif attack_type == 'power':
                    if attack is None or attack.class_name() != 'Power':
                        r = API404
                        r[MSG] = 'Power not found for attack_key '+attack_key+' .'                            
                        return self.response.out.write(simplejson.dumps(r))
                else:
                    r = API400
                    r[MSG] = 'Invalid \'attack_type\'.'                             
                    return self.response.out.write(simplejson.dumps(r))  
                
                # Get enemy Characters  
                enemies = []
                for e in enemy_character_keys:
                    enemy = db.get(e)
                    if enemy is None or enemy.class_name() != 'Character':
                        r = API404
                        r[MSG] = 'Character not found for character_key '+e+' .'                            
                        return self.response.out.write(simplejson.dumps(r))
                    else:
                        enemies.append(enemy)
                
                damage = party.getJSONAttack(party, enemies, 
                                             attacker, attack_type, attack)
                
                r = API200
                r[MSG] = 'Smite thy enemies!'
                r['Damage'] = damage                                                                             
                    
            '''Character checkins in at a location seeking Parties, Traps or
            Events.
            '''
            elif action == 'quest':

            
                parties = party.getJSONParties(party, player, location)
                r = API200
                r[MSG] = 'Who goes there?'
                r['Parties'] = parties
            
            '''Character sends a message to character(s) in a Party.
            '''    
            elif action == 'greet':
                # get character a, party a, party b, location, skill.                 
            
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


######## OLD STUFF BELOW 

            
class APIPlayerCharacterTemplates(APIBase):
    def get(self):
        '''Returns all PlayerCharacterTemplates.
        '''
        _trace = TRACE+'APIPlayerCharacterTemplates:: get() '
        logging.info(_trace)
        try:
            user = self.current_user()
        except:
            r = API401
            return self.response.out.write(simplejson.dumps(r))
        
        r = API200
        templates = character.getJSONPlayerCharacterTemplates()
        r['player_character_templates'] = templates
        return self.response.out.write(simplejson.dumps(r))                            
        
class APIPlayerCharacter(APIBase):
    def get(self, key):
        '''Returns a PlayerCharacter for the given key.
        '''
        _trace = TRACE+'APIPlayerCharacter:: get() '
        logging.info(_trace)
        try:
            user = self.current_user()
        except:
            r = API401
            return self.response.out.write(simplejson.dumps(r))
                    
        player = db.get(character_key)
        if player is None:
            r = API404
            r[MSG] = 'Player not found.'
        else:
            r = API200
            r[MSG] = 'A hero?'        
            r['player_character'] = character.getJSONPlayer(player)
        return self.response.out.write(simplejson.dumps(r))    

class APIPlayerParty(APIBase):
    
    def post(self):
        '''Returns a new PlayerParty for a PlayerCharacter.
        ''' 
        return
        
class APINonPlayerParty(APIBase):
    
    def post(self):
        '''Returns a new NonPlayerParty if there are Monsters in the area.
        '''  
        return

    def put(self):
        '''Returns an updated NonPlayerParty after and any damage applied.
        '''
        
class APICharacterPlayerAction(APIBase):
    def get(self, key, action):
        '''Returns action data.
        '''
        try:
            user = self.current_user()
        except:
            r = API401
            return self.response.out.write(simplejson.dumps(r))
        
        if action == 'adventure':
        
        else:
            r = API404
            r[MSG] = 'Action not found.'                            

class APIPlayerFOO(webapp.RequestHandler):
    '''Provides API access to Player Character CRUD.  Responses are in JSON.
    '''
    def get(self, character_key):
        '''Returns a Player Character for the 
        '''    
        _trace = TRACE+'APIPlayer:: get() '
        logging.info(_trace)
        player = db.get(character_key)
        r = API200
        r[MSG] = 'A hero?'        
        r[player.class_name()] = character.getJSONPlayer(player)
        return self.response.out.write(simplejson.dumps(r))
        
    def post(self, character_key):
        '''Create a new Player Character.  If the character_key is 0, create 
        a new custom Player Character, otherwise create a new Player 
        Character based on the PlayerCharacterTemplate corresponding to the 
        character_key.
        '''    
        _trace = TRACE+'APIPlayer:: post() '
        logging.info(_trace)
        try:
            user = oauth.get_current_user()
            logging.info(_trace + 'user = ' + str(user))
        except oauth.OAuthRequestError, e:
            logging.info(_trace + e)               
            r = API401
            return self.response.out.write(simplejson.dumps(r))  
                 
        if template_key == '0': 
            r = API404
            '''
            r = API200
            player = character.createPlayer(self)
            r[MSG] = 'This one won\'t last long I fear.'
            r[player.class_name()] = character.getJSONPlayer(player)
            '''
            r[MSG] = 'Custom Player Characters not allowed at this time.'
        else: 
            player = character.createPlayerFromTemplate(character_key, 
                                                        self, user)
                                                         
            if player is not None:
                r = API200
                r[player.class_name()] = character.getJSONPlayer(player)
            else:    
                r = API404
                r[MSG] = 'Template not found.'
        return self.response.out.write(simplejson.dumps(r)) 

class APINonPlayer(webapp.RequestHandler):
    '''Provides API access to NonPlayer Character data. Responses are in JSON.
    '''
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
    '''Provides basic API error Response in JSON.
    '''
    def get(self, foo):
        r = API404
        return self.response.out.write(simplejson.dumps(r)) 

    def post(self, foo):
        r = API404
        return self.response.out.write(simplejson.dumps(r)) 
        
class APIPlayerItem(webapp.RequestHandler):
    '''Provides API access to Player Item data.  Responses are in JSON.
    '''
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
    '''Provides API access to Player Power data.  Responses are in JSON.
    '''
    def get(self, type, method):
        r = API404
        return self.response.out.write(simplejson.dumps(r)) 

    def post(self, model, method):
        logging.info(TRACE+'APIPlayerPower:: post()')
        r = API404
        if model == models.ATT.lower():
            if method == 'add':
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
    '''Provides API access to Player Actions.  Responses are in JSON.
    '''
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
    '''Provides API access to Party, PlayerParty and NonPlayerParty data.
    Responses are in JSON.
    '''
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
    '''
    {'encounters': {'count': 23, 'uniques': 2, 'start_time': POSIX
                   'last_encounter': {'time_since': POSIX, 'checks': 9}}}
    '''
    return None
                     
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
                                       APIParties),                                   
                                      (r'/api/parties/(.*)', 
                                       APIParties)
                                     ],
                                     debug=DEBUG)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
