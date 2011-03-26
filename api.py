#
# Copyright 2010 SuperKablamo, LLC
# info@superkablamo.com
#

############################# SK IMPORTS #####################################
############################################################################## 
import models
import utils

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
        logging.info('################### APIPlayer:: get() ################')
        i = utils.strToInt(player_id)
        player = models.PlayerCharacter.get_by_id(i)
        r = getJSONPlayer(player)
        return self.response.out.write(simplejson.dumps(r))
        
    def post(self, method):
        logging.info('################## APIPlayer:: post() ################')
        if method == 'new': 
            r = createPlayer(self)
        else: 
            r = API404
            r[MSG] = 'New Player was not created.'
        return self.response.out.write(simplejson.dumps(r)) 

class APINonPlayer(webapp.RequestHandler):
    """Provides API access to NonPlayer Character data. Responses are in JSON.
    """
    def get(self, method):
        logging.info('################### APINonPlayer:: get() #############')
    
    def post(self, method):
        logging.info('################## APINonPlayer:: post() #############')
        if method == 'new': 
            r = createNonPlayer(self)
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
        logging.info('################# APIPlayerItem:: post() #############')
        r = API404
        if model == models.WPN.lower():
            if method == "add":
                player_id = self.request.get('player_id')
                name = self.request.get('weapon_name')
                player = addToPlayer(models.Weapon, name, player_id)
                if player is not None:
                    r =  getJSONPlayer(player)  
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
        logging.info('################# APIPlayerPower:: post() ############')
        r = API404
        if model == models.ATT.lower():
            if method == "add":
                player_id = self.request.get('player_id')
                name = self.request.get('attack_name')
                player = addToPlayer(models.Attack, name, player_id)
                if player is not None:
                    r =  getJSONPlayer(player) 
                else:
                    r['message'] = 'Power was not added to Player.'             
        return self.response.out.write(simplejson.dumps(r)) 
            
               
######################## METHODS #############################################
##############################################################################
def getJSONPlayer(player):
    json = {'name': player.name, 'level': player.level, 'race': player.race,
            'alignment': player.alignment, 'size': player.size, 
            'experience': player.experience, 'speed': player.speed, 
            'hit_points': player.hit_points, 'cast': player.cast, 
            'height': player.height, 'weight': player.weight, 
            'scores': player.scores, 'created': str(player.created), 
            'id': str(player.key().id())}
            
    # Construct JSON for Player Powers
    powers = db.get(player.powers)
    attacks = []
    utilities = []
    healing = [] 
    for p in powers:
        if p.class_name() == models.ATT:
            attacks.append(p.json)   
        elif p.class_name() == models.UTL:
            utilities.append(p.json)
        elif p.class_name() == models.HEL:
            healing.append(p.json)
                        
    powers_json = {'attacks': attacks, 
                   'utilities': utilities, 
                   'healing': healing}
    
    # Construct JSON for Player Items
    items = db.get(player.items)
    weapons = []
    armor = []
    implements = []
    gear = []   
    potions = [] 
    artifacts =[]
    rings = []               
    for i in items:  
        if i.class_name() == models.WPN:
            weapons.append(i.json)        
        elif i.class_name() == models.ARM:      
            armor.append(i.json)
        elif i.class_name() == models.IMP:      
            implements.append(i.json)
        elif i.class_name() == models.GEA:      
            gear.append(i.json)
        elif i.class_name() == models.POT:      
            potions.append(i.json)
        elif i.class_name() == models.RIN:      
            rings.append(i.json)
        elif i.class_name() == models.ART:      
            artifacts.potions.append(i.json)

    items_json = {'weapons': weapons, 'armor': armor, 'potions': potions,
                  'implements': implements, 'gear': gear, 'rings': rings,
                  'artifacts': artifacts}
                  
    json['powers'] = powers_json 
    json['items'] = items_json
    return json

def addToPlayer(model_type, object_name, player_id):
    """Adds an Item or Power to a Player.
    """
    args = '('+str(model_type)+', '+object_name+', '+player_id+')'
    logging.info('########## addToPlayer'+args)
    id_ = utils.strToInt(player_id)
    player = models.PlayerCharacter.get_by_id(id_)
    object_ = model_type.get_by_key_name(object_name)
    name = model_type.class_name() 
    logging.info('########## name = '+name+' ###############################')
    # Determine whether this is object is a subclass of Item or Power
    if name in (models.WPN, models.ARM, models.IMP, models.GEA): 
        player.items.append(object_.key())
    elif name in (models.ATT, models.UTL, models.HEL):
        player.powers.append(object_.key())
    else:
        logging.info('########## NO MATCH FOUND for '+object_name+' ########')
        return None    
    db.put(player)  
    return player

def createPlayer(self):
    """Creates a new Player Character and returns that character as a JSON
    Response.
    """
    logging.info('###################### createPlayer() ####################')    
    # Build the basic data format for scores and fill base values ...
    abilities = buildScores(self, models.ABILITIES_KEY, models.ABILITY_KEYS)
    skills = buildScores(self, models.SKILLS_KEY, models.SKILL_KEYS)
    defenses = buildScores(self, models.DEFENSES_KEY, models.DEFENSE_KEYS)
    scores = {'abilities': abilities, 'skills': skills, 'defenses': defenses}
    logging.info('###################### score = '+str(scores)+'############')
    scores = buildDefenses(scores)
    # Update score data with Race and Cast bonuses ...
    race = models.Race.get_by_key_name(self.request.get('race'))
    cast = models.Cast.get_by_key_name(self.request.get('cast'))   
    logging.info('###################### score = '+str(scores)+'############')     
    scores = addMods(self, scores, race.mods, cast.mods)
    hp = buildHitPoints(cast, scores)
    player = models.PlayerCharacter(name = self.request.get('name'),
                                    level = 1,
                                    speed = utils.strToInt(self.request.get('speed')),
                                    size = self.request.get('size'),
                                    race = self.request.get('race'),
                                    cast = self.request.get('cast'),
                                    alignment = self.request.get('alignment'),
                                    hit_points = hp,
                                    height = utils.strToInt(self.request.get('height')),
                                    weight = utils.strToInt(self.request.get('weight')),
                                    scores = scores)
    db.put(player)
    return 
        
def buildScores(self, cat_key, attr_keys):
    scores = {}
    for a in attr_keys:
        # If Defense scores, start at a base of 10 ...
        if cat_key == models.DEFENSES_KEY:
            score = 10
        # But, Ability and Skill scores are set at Character creation ...    
        else:
            score = self.request.get(a)
        mod = 0
        mods = None
        # If Ability Scores, then add the Ability modifier ...
        if cat_key == models.ABILITIES_KEY: 
            mod = models.ABILITY_MODIFIERS[score]
            mods = []
            origin = models.ABILITY_MOD
            type_ = a
            mods.append({'origin':origin, 'mod': mod, 'type': type_})
        score_dict = {'score': score, 'mod': mod, 'mods': mods}
        scores[a] = score_dict
    return scores

def buildHitPoints(cast, scores):
    logging.info('############## buildHitPoints() ##########################')    
    #{"hp": 10, "surge": 2, "recharge": 3}
    con = scores[models.ABILITIES_KEY]['CON']['score']
    hp = cast.hit_point_base + utils.strToInt(con)
    surge_recharge = cast.surge_recharge
    surge = hp//4
    hit_points = {'hp': hp, 'surge': surge, 'surge_recharge': surge_recharge}
    return hit_points
    
def buildDefenses(scores):
    logging.info('############## buildDefenses() ###########################')    
    #TODO: determine higher score for each pair of associated abilities,
    # add any modifiers . . .
    for d in models.DEFENSE_KEYS:
        if d == 'FORT':
            str_ = getMod(scores, models.ABILITIES_KEY, 'STR') 
            con = getMod(scores, models.ABILITIES_KEY, 'CON') 
            if str_ > con:
                keyword = 'STR'
                mod = str_
                logging.info('########### STR mod = '+str(mod)+' ###########')
            else:    
                keyword = 'CON'
                mod = con
                logging.info('########### CON mod = '+str(mod)+' ###########')
            mod = {'origin': models.ABILITY_MOD, 'mod': mod, 'type': keyword}    
            scores = setMod(scores, models.DEFENSES_KEY, d, mod)

        elif d == 'REF':
            int_ = getMod(scores, models.ABILITIES_KEY, 'INT') 
            dex = getMod(scores, models.ABILITIES_KEY, 'DEX')   
            if int_ > dex:
                keyword = 'INT'
                mod = int_
                logging.info('########### INT mod = '+str(mod)+' ###########')
            else:    
                keyword = 'DEX'
                mod = dex
                logging.info('########### DEX mod = '+str(mod)+' ###########')                
            mod = {'origin': models.ABILITY_MOD, 'mod': mod, 'type': keyword}    
            scores = setMod(scores, models.DEFENSES_KEY, d, mod)                     
        elif d == 'WILL':            
            wis = getMod(scores, models.ABILITIES_KEY, 'WIS') 
            cha = getMod(scores, models.ABILITIES_KEY, 'CHA')
            if wis > cha:
                keyword = 'WIS'
                mod = wis
                logging.info('########### WIS mod = '+str(mod)+' ###########')                
            else:    
                keyword = 'CHA'
                mod = cha
                logging.info('########### CHA mod = '+str(mod)+' ###########')                
            mod = {'origin': models.ABILITY_MOD, 'mod': mod, 'type': keyword}    
            scores = setMod(scores, models.DEFENSES_KEY, d, mod)            
                
    return scores    

def addMods(self, scores, *mods):
    logging.info('############## addMods() #################################')
    logging.info('############## scores = '+str(scores)+' ##################')
    logging.info('############## score_keys = '+str(models.SCORE_KEYS)+' ###')    
    for m in mods: # Loop through each List of mods ...
        logging.info('#################### m = '+str(m)+' ##################')
        for k in models.SCORE_KEYS: # Loop through categories in mod List ...
            logging.info('#################### k = '+str(k)+' ##############')
            if k in m: # If there are mods for that category ...
                for mod in m[k]: # Loop through those mods ...
                    logging.info('#################### mod = '+str(mod)+' ##')
                    origin = mod['origin']
                    type_ = mod['type']
                    mod = mod['mod']
                    if scores[k][type_]['mods'] is None:
                        mods = []
                        mods.append({'origin':origin, 
                                     'mod': mod, 
                                     'type': type_})
                        scores[k][type_]['mods'] = mods
                    else:
                        scores[k][type_]['mods'].append({'origin':origin, 
                                                         'mod': mod, 
                                                         'type': type_})
                    total_mod = scores[k][type_]['mod']
                    logging.info('##### total_mod = '+str(total_mod)+' #####')  
                    logging.info('##### mod = '+str(mod)+' ##########')                                           
                    total_mod += mod
                    logging.info('##### total_mod = '+str(total_mod)+' #####')                      
                    scores[k][type_]['mod'] = total_mod      
                    logging.info('# mod = '+str(scores[k][type_]['mod'])+' #')                                 
    
    return scores

def getMod(scores, cat_key, keyword):
    logging.info('######################## getMod() ########################')    
    mod = scores[cat_key][keyword]['mod']
    return utils.strToInt(mod)
    
def getScore(scores, cat_key, keyword):
    logging.info('######################## getScore() ######################')      
    score = scores[cat_key][keyword]['score']    
    return utils.strToInt(score)    
    
def setMod(scores, cat_key, keyword, mod):
    logging.info('######################## setMod() ########################')
    logging.info('######################## cat_key = '+cat_key+' ###########')    
    logging.info('######################## keyword = '+keyword+' ###########')    
    logging.info('######################## mod = '+str(mod)+' ##############')        
    # If "mods" doesn't exist then create it ... 
    if scores[cat_key][keyword]['mods'] is None:
        mods = [mod]
        scores[cat_key][keyword]['mods'] = mods
    # Otherwise add to the existing List of mods ...    
    else: 
        scores[cat_key][keyword]['mods'].append(mod)
    total_mod = scores[cat_key][keyword]['mod']
    logging.info('##################### total_mod = '+str(total_mod)+' #####')   
    total_mod += mod['mod']
    logging.info('##################### mod = '+str(mod['mod'])+' ##########')      
    logging.info('##################### total_mod = '+str(total_mod)+' #####')   
    scores[cat_key][keyword]['mod'] = total_mod
    logging.info('########### mods = '+str(scores[cat_key][keyword])+' #####')     
    return scores
    
def setScore(scores, cat_key, keyword, score):          
    logging.info('######################## setScore() ######################')  
    scores[cat_key][keyword]['score'] = score       
    return scores
                     
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

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
