# ============================================================================
# Copyright (c) 2011, SuperKablamo, LLC.
# All rights reserved.
# info@superkablamo.com
#
# character.py 
# ============================================================================

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

############################# CONSTANTS ######################################
##############################################################################
UTILITY = 10 
ENCOUNTER = 3600
DAILY = 43200

######################## METHODS #############################################
##############################################################################
def getJSONPlayer(player):
    '''Returns a PlayerCharacter or PlayerCharacterTemplate as JSON.
    '''
    _trace = TRACE + 'getJSONPlayer() '
    logging.info(_trace)
    logging.info(_trace + 'player = ' + player.name)
    json = {'name': player.name, 'level': player.level, 'race': player.race,
            'alignment': player.alignment, 'size': player.size, 
            'experience': player.experience, 'speed': player.speed, 
            'hit_points': player.hit_points, 'cast': player.cast, 
            'height': player.height, 'weight': player.weight, 
            'scores': player.scores, 'created': str(player.created), 
            'purse': player.purse, 'resist': player.resist,
            'vulnerable': player.vulnerable, 'key': str(player.key())}

    if nonplayer.class_name() == 'PlayerCharacterTemplate':
        json['template_id'] = nonplayer.template_id

    if nonplayer.class_name() == 'Player':
        if player.user:
           json['user'] = player.user.nickname()
    
    logging.info(_trace + 'json = ' + str(json))            
    # Construct JSON for Player Powers
    powers = db.get(player.powers)
    attacks = []
    utilities = []
    healing = [] 
    for p in powers:
        logging.info(_trace + 'power = ' + str(p))
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
     
    immunities = []
    for i in player.immunities:
        immunities.append(i)
    languages = []
    for l in player.languages:
        languages.append(l)
    
    json['languages'] = languages    
    json['immunities'] = immunities
    json['powers'] = powers_json 
    json['items'] = items_json
    return json

def getJSONNonPlayer(nonplayer):
    '''Returns a Monster or PlayerCharacterTemplate as JSON.
    '''    
    json = {'name': nonplayer.name, 'level': nonplayer.level, 
            'race': nonplayer.race, 'alignment': nonplayer.alignment, 
            'size': nonplayer.size, 'experience': nonplayer.experience, 
            'speed': nonplayer.speed, 'hit_points': nonplayer.hit_points, 
            'scores': nonplayer.scores, 'description': nonplayer.description,
            'origin': nonplayer.origin, 'category': nonplayer.category,
            'actions': nonplayer.actions, 'role': nonplayer.role, 
            'challenge': nonplayer.challenge, 'keywords': nonplayer.keywords,
            'artifacts': nonplayer.artifacts,
            'languages': nonplayer.languages, 'resist': nonplayer.resist,
            'vulnerable': nonplayer.vulnerable,
            'created': str(nonplayer.created), 
            'id': str(nonplayer.key().id())}
    
    if nonplayer.class_name == 'Monster':
        if nonplayer.user:
            json['user'] = nonplayer.user.nickname()
    
    if nonplayer.class_name == 'NonPlayerCharacterTemplate':
        json['template_id'] = nonplayer.template_id
        json['unique'] = nonplayer.unique
        json['active'] = nonplayer.active
    
    # Construct JSON for NonPlayer Items
    items = db.get(nonplayer.items)
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

    # Construct JSON for NonPlayer immunities
    immunities = []
    for i in nonplayer.immunities:
        immunities.appened(i)
    
    json['immunities'] = immunities
    json['items'] = items_json
    return json    
    
def addToPlayer(model_type, object_name, player_id):
    '''Adds an Item or Power to a Player.
    '''
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
    '''Creates a new Player Character and returns that character as a JSON
    Response.
    '''
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
    return player

def createPlayerFromTemplate(pc_template, name, user):
    '''Creates a new PlayerCharacter from a PlayerCharacterTemplate.
    ''' 
    _trace = TRACE + 'createPlayerFromTemplate():: '
    logging.info(_trace)
    if pc_template is None: return None
    player = models.Player(name = name,
                           level = pc_template.level,
                           race = pc_template.race,
                           alignment = pc_template.alignment,
                           size = pc_template.size,
                           experience = pc_template.experience,
                           speed = pc_template.speed,
                           items = pc_template.items,
                           hit_points = pc_template.hit_points,
                           scores = pc_template.scores,
                           languages = pc_template.languages,
                           immunities = pc_template.immunities,
                           resist = pc_template.resist,
                           vulnerable = pc_template.vulnerable,
                           cast = pc_template.cast,
                           height = pc_template.height,
                           weight = pc_template.weight,
                           powers = pc_template.powers,
                           equipped = pc_template.equipped,
                           purse = pc_template.purse,
                           user = user)
    db.put(player)                       
    return player
        
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
    #{'hp': 10, 'surge': 2, 'recharge': 3}
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
    # If 'mods' doesn't exist then create it ... 
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

def getJSONPlayerCharacterTemplates():
    '''Returns all PlayerCharacterTemplates as JSON.
    '''
    _trace = TRACE+'getJSONPlayerCharactersTemplates() '
    logging.info(_trace)    
    templates = models.PlayerCharacterTemplate.all().fetch(10)
    json = []
    for t in templates:
        character = getJSONPlayer(t)
        json.append(character)
        
    return json
    
def seedPlayerCharacterTemplates():
    '''Primes the datastore with PlayerCharacter templates.
    '''
    _trace = TRACE+'seedPlayerCharactersTemplates() '
    logging.info(_trace)
    pc_templates = []   
    for x in PC_TEMPLATES:    
        logging.info(_trace+'x = '+str(x))
        
        # Parse out lists of data.
        powers = []
        items = []
        languages = []        
        keys = x['powers'].keys()
        for k in keys:
            _dict = x['powers'][k]
            for name in _dict:
                key = db.Key.from_path('Power', name)
                powers.append(key)    
                        
        keys = x['items'].keys()
        for k in keys:
            _dict = x['items'][k]
            for name in _dict:
                key = db.Key.from_path('Item', name)
                items.append(key)
                
        for a in x['languages']:
            languages.append(a)    
        
        pc_template = models.PlayerCharacterTemplate(key_name = x['name'],
                                   name = x['name'],
                                   template_id = x['template_id'],
                                   level = 1,
                                   race = x['race'],
                                   alignment = x['alignment'], 
                                   size = x['size'],
                                   experience = 0,
                                   speed = x['speed'], 
                                   hit_points = x['hit_points'],                                    
                                   languages = languages,
                                   immunities = [],
                                   scores = x['scores'],
                                   cast = x['cast'],
                                   height = x['height'],
                                   weight = x['weight'],
                                   powers = powers,
                                   items = items,
                                   purse = x['purse'])

        pc_templates.append(pc_template)      

    db.put(pc_templates)                         
    return

######################## DATA ################################################
##############################################################################    
PC_TEMPLATES = [  

  ############################## PLAYER TEMPLATE 1 ###########################
  {'template_id': 1,
  'name': 'Human Fighter',
  'cast': 'Fighter',
  'race': 'Human',
  'weight': 220,
  'height': 72,
  'purse': {'copper': 0, 'silver': 0, 'gold': 100, 'platinum': 0, 'gems': 0},
  'powers': 
    {'attacks': ['Sure Strike','Furious Strike','Brute Strike'],      
    'utilities': [],
    'healing': []},
  'scores': 
    {'skills': 
      {'Acrobatics':{'bonus':1,'points':{'ability':1,'level':0,'trained':0,'armor':0}},
      'Arcana':{'bonus':0,'points':{'ability':0,'level':0,'trained': 0,'armor':0}},
      'Athletics':{'bonus':9,'points':{'ability':4,'level':0,'trained':5,'armor':0}},
      'Bluff':{'bonus':0,'points':{'ability':0,'level':0,'trained':0,'armor':0}},
      'Diplomacy':{'bonus':0,'points':{'ability':0,'level':0,'trained':0,'armor':0}},
      'Dungeoneering':{'bonus':1,'points':{'ability':1,'level':0,'trained':0,'armor':0}},
      'Endurance':{'bonus':7,'points':{'ability':2,'level':0,'trained':5,'armor':0}},
      'Heal':{'bonus':1,'points':{'ability':1,'level':0,'trained':0,'armor':0}},
      'History':{'bonus':0,'points':{'ability':0,'level':0,'trained':0,'armor':0}},
      'Insight':{'bonus':1,'points':{'ability':1,'level':0,'trained':0,'armor':0}},
      'Intimidate':{'bonus':5,'points':{'ability':0,'level':0,'trained':5,'armor':0}},
      'Nature':{'bonus':1,'points':{'ability':1,'level':0,'trained':0,'armor':0}},
      'Perception':{'bonus':1,'points':{'ability':1,'level':0,'trained':0,'armor':0}},
      'Religion':{'bonus':0,'points':{'ability':0,'level':0,'trained':0,'armor':0}},
      'Stealth':{'bonus':1,'points':{'ability':1,'level':0,'trained':0,'armor':0}},
      'Streetwise':{'bonus':5,'points':{'ability':0,'level':0,'trained':5,'armor':0}},
      'Thievery':{'bonus':1,'points':{'ability':1,'level':0,'trained':0,'armor':0}}},
    'abilities': 
      {'DEX':{'score':13,'config':{'levelup':0,'race':0,'base':13},'mods':{'halflevel':0,'ability':1},'mod':1},
      'CHA':{'score':11,'config':{'levelup':0,'race':0,'base':11},'mods':{'halflevel':0,'ability':0},'mod':0},
      'INT':{'score':10,'config':{'levelup':0,'race':0,'base':10},'mods':{'halflevel':0,'ability':0},'mod':0},
      'WIS':{'score':12,'config':{'levelup':0,'race':0,'base':12},'mods':{'halflevel':0,'ability':1},'mod':1},
      'STR':{'score':18,'config':{'levelup':0,'race':2,'base':16},'mods':{'halflevel':0,'ability':4},'mod':4},
      'CON':{'score':14,'config':{'levelup':0,'race':0,'base':14},'mods':{'halflevel':0,'ability':2},'mod':2}},
    'defenses': 
      {'WILL':{'score': 12,'config':{'base':10,'class':0,'race':1,'ability':1,'level':0,'armor':0,'item':0}},
      'AC':{'score':17,'config':{'base':10,'class':0,'race':0,'ability':0,'level':0,'armor':7,'item':0}},
      'REF':{'score':12,'config':{'base':10,'class':0,'race':1,'ability':1,'level':0,'armor':0,'item': 0}},
      'FORT':{'score':17,'config':{'base':10,'class':2,'race':1,'ability':4,'level':0,'armor':0,'item':0}}}},
  'hit_points':{'surge_recharge':7855,'hp':29,'surge':7},
  'items': 
    {'gear': [],
    'armor': ['Scale'],
    'rings': [],
    'weapons': ['Greatsword','Longbow'],
    'artifacts': [],
    'potions': []},
  'speed': 6,
  'alignment': 'Good',
  'size': 'Medium',
  'languages': ['Common', 'Dwarven']},
  
  ############################## PLAYER TEMPLATE 2 ###########################
  {'template_id': 2,
  'name': 'Halfling Rogue',
  'cast': 'Rogue',
  'race': 'Halfling',
  'weight': 80,
  'height': 48,
  'purse': {'copper': 0, 'silver': 0, 'gold': 100, 'platinum': 0, 'gems': 0},
  'powers': 
    {'attacks': ['Piercing Strike','Torturous Strike','Sly Strike'],
    'utilities': [],
    'healing': []},
  'scores': 
    {'skills': 
      {'Acrobatics':{'bonus':9,'points':{'ability':4,'level':0,'trained':5,'armor':0}},
      'Arcana':{'bonus':0,'points':{'ability':0,'level':0,'trained': 0,'armor':0}},
      'Athletics':{'bonus':1,'points':{'ability':1,'level':0,'trained':0,'armor':0}},
      'Bluff':{'bonus':8,'points':{'ability':3,'level':0,'trained':5,'armor':0}},
      'Diplomacy':{'bonus':3,'points':{'ability':3,'level':0,'trained':0,'armor':0}},
      'Dungeoneering':{'bonus':0,'points':{'ability':0,'level':0,'trained':0,'armor':0}},
      'Endurance':{'bonus':1,'points':{'ability':1,'level':0,'trained':5,'armor':0}},
      'Heal':{'bonus':0,'points':{'ability':0,'level':0,'trained':0,'armor':0}},
      'History':{'bonus':0,'points':{'ability':0,'level':0,'trained':0,'armor':0}},
      'Insight':{'bonus':5,'points':{'ability':0,'level':0,'trained':5,'armor':0}},
      'Intimidate':{'bonus':5,'points':{'ability':0,'level':0,'trained':5,'armor':0}},
      'Nature':{'bonus':3,'points':{'ability':3,'level':0,'trained':0,'armor':0}},
      'Perception':{'bonus':5,'points':{'ability':0,'level':0,'trained':5,'armor':0}},
      'Religion':{'bonus':0,'points':{'ability':0,'level':0,'trained':0,'armor':0}},
      'Stealth':{'bonus':9,'points':{'ability':4,'level':0,'trained':5,'armor':0}},
      'Streetwise':{'bonus':3,'points':{'ability':3,'level':0,'trained':0,'armor':0}},
      'Thievery':{'bonus':9,'points':{'ability':4,'level':0,'trained':5,'armor':0}}},
    'abilities': 
      {'DEX':{'score':18,'config':{'levelup':0,'race':2,'base':16},'mods':{'halflevel':0,'ability':4},'mod':4},
      'CHA':{'score':16,'config':{'levelup':0,'race':2,'base':14},'mods':{'halflevel':0,'ability':3},'mod':3},
      'INT':{'score':10,'config':{'levelup':0,'race':0,'base':10},'mods':{'halflevel':0,'ability':0},'mod':0},
      'WIS':{'score':11,'config':{'levelup':0,'race':0,'base':11},'mods':{'halflevel':0,'ability':0},'mod':0},
      'STR':{'score':13,'config':{'levelup':0,'race':0,'base':13},'mods':{'halflevel':0,'ability':1},'mod':1},
      'CON':{'score':12,'config':{'levelup':0,'race':0,'base':12},'mods':{'halflevel':0,'ability':1},'mod':1}},
    'defenses': 
      {'WILL':{'score': 13,'config':{'base':10,'class':0,'race':0,'ability':3,'level':0,'armor':0,'item':0}},
      'AC':{'score':16,'config':{'base':10,'class':0,'race':0,'ability':4,'level':0,'armor':2,'item':0}},
      'REF':{'score':16,'config':{'base':10,'class':2,'race':0,'ability':4,'level':0,'armor':0,'item': 0}},
      'FORT':{'score':11,'config':{'base':10,'class':0,'race':0,'ability':1,'level':0,'armor':0,'item':0}}}},
  'hit_points':{'surge_recharge':12343,'hp':24,'surge':6},
  'items': 
    {'gear': [],
    'armor': ['Leather'],
    'rings': [],
    'weapons': ['Shortsword','Dagger'],
    'artifacts': [],
    'potions': []},
  'speed': 6,
  'alignment': 'Good',
  'size': 'Small',
  'languages': ['Common', 'Elven']},  

  ############################## PLAYER TEMPLATE 3 ###########################
  {'template_id': 3,
  'name': 'Elf Wizard',
  'cast': 'Wizard',
  'race': 'Elf',
  'weight': 120,
  'height': 64,
  'purse': {'copper': 0, 'silver': 0, 'gold': 100, 'platinum': 0, 'gems': 0},
  'powers': 
    {'attacks': ['Magic Missile','Ray of Frost','Burning Hands','Acid Arrow'],
    'utilities': [],
    'healing': []},
  'scores': 
    {'skills': 
      {'Acrobatics':{'bonus':3,'points':{'ability':3,'level':0,'trained':0,'armor':0}},
      'Arcana':{'bonus':8,'points':{'ability':3,'level':0,'trained':5,'armor':0}},
      'Athletics':{'bonus':0,'points':{'ability':0,'level':0,'trained':0,'armor':0}},
      'Bluff':{'bonus':0,'points':{'ability':0,'level':0,'trained':0,'armor':0}},
      'Diplomacy':{'bonus':0,'points':{'ability':0,'level':0,'trained':0,'armor':0}},
      'Dungeoneering':{'bonus':7,'points':{'ability':2,'level':0,'trained':5,'armor':0}},
      'Endurance':{'bonus':1,'points':{'ability':1,'level':0,'trained':0,'armor':0}},
      'Heal':{'bonus':2,'points':{'ability':2,'level':0,'trained':0,'armor':0}},
      'History':{'bonus':8,'points':{'ability':3,'level':0,'trained':5,'armor':0}},
      'Insight':{'bonus':7,'points':{'ability':2,'level':0,'trained':5,'armor':0}},
      'Intimidate':{'bonus':0,'points':{'ability':0,'level':0,'trained':0,'armor':0}},
      'Nature':{'bonus':2,'points':{'ability':2,'level':0,'trained':0,'armor':0}},
      'Perception':{'bonus':2,'points':{'ability':2,'level':0,'trained':0,'armor':0}},
      'Religion':{'bonus':3,'points':{'ability':3,'level':0,'trained':0,'armor':0}},
      'Stealth':{'bonus':3,'points':{'ability':3,'level':0,'trained':0,'armor':0}},
      'Streetwise':{'bonus':0,'points':{'ability':0,'level':0,'trained':0,'armor':0}},
      'Thievery':{'bonus':3,'points':{'ability':3,'level':0,'trained':0,'armor':0}}},
    'abilities': 
      {'DEX':{'score':16,'config':{'levelup':0,'race':2,'base':14},'mods':{'halflevel':0,'ability':3},'mod':3},
      'CHA':{'score':11,'config':{'levelup':0,'race':0,'base':11},'mods':{'halflevel':0,'ability':0},'mod':0},
      'INT':{'score':16,'config':{'levelup':0,'race':0,'base':16},'mods':{'halflevel':0,'ability':3},'mod':3},
      'WIS':{'score':15,'config':{'levelup':0,'race':2,'base':13},'mods':{'halflevel':0,'ability':2},'mod':2},
      'STR':{'score':10,'config':{'levelup':0,'race':0,'base':10},'mods':{'halflevel':0,'ability':0},'mod':0},
      'CON':{'score':12,'config':{'levelup':0,'race':0,'base':12},'mods':{'halflevel':0,'ability':1},'mod':1}},
    'defenses': 
      {'WILL':{'score': 14,'config':{'base':10,'class':2,'race':0,'ability':2,'level':0,'armor':0,'item':0}},
      'AC':{'score':14,'config':{'base':10,'class':0,'race':0,'ability':3,'level':0,'armor':0,'item':1}},
      'REF':{'score':13,'config':{'base':10,'class':0,'race':0,'ability':3,'level':0,'armor':0,'item': 0}},
      'FORT':{'score':11,'config':{'base':10,'class':0,'race':0,'ability':1,'level':0,'armor':0,'item':0}}}},
  'hit_points':{'surge_recharge':12343,'hp':22,'surge':5},
  'items': 
    {'gear': [],
    'armor': ['Cloth'],
    'rings': [],
    'weapons': ['Staff of Defense'],
    'artifacts': [],
    'potions': []},
  'speed': 6,
  'alignment': 'Good',
  'size': 'Medium',
  'languages': ['Common', 'Elven']},

  ############################## PLAYER TEMPLATE 4 ###########################
  {'template_id': 4,
  'name': 'Dwarf Cleric',
  'cast': 'Cleric',
  'race': 'Dwarf',
  'weight': 205,
  'height': 54,
  'purse': {'copper': 0, 'silver': 0, 'gold': 100, 'platinum': 0, 'gems': 0},
  'powers': 
    {'attacks': ['Weapon of Faith','Spoken Word','Cleansing Flame'],
    'utilities': [],
    'healing': []},
  'scores': 
    {'skills': 
      {'Acrobatics':{'bonus':-1,'points':{'ability':0,'level':0,'trained':0,'armor':-1}},
      'Arcana':{'bonus':0,'points':{'ability':0,'level':0,'trained':0,'armor':0}},
      'Athletics':{'bonus':2,'points':{'ability':3,'level':0,'trained':0,'armor':-1}},
      'Bluff':{'bonus':1,'points':{'ability':1,'level':0,'trained':0,'armor':0}},
      'Diplomacy':{'bonus':6,'points':{'ability':1,'level':0,'trained':5,'armor':0}},
      'Dungeoneering':{'bonus':5,'points':{'ability':3,'level':0,'trained':0,'armor':0,'race':2}},
      'Endurance':{'bonus':3,'points':{'ability':2,'level':0,'trained':0,'armor':-1,'race':2}},
      'Heal':{'bonus':8,'points':{'ability':3,'level':0,'trained':5,'armor':0}},
      'History':{'bonus':0,'points':{'ability':0,'level':0,'trained':0,'armor':0}},
      'Insight':{'bonus':8,'points':{'ability':3,'level':0,'trained':5,'armor':0}},
      'Intimidate':{'bonus':1,'points':{'ability':1,'level':0,'trained':0,'armor':0}},
      'Nature':{'bonus':3,'points':{'ability':3,'level':0,'trained':0,'armor':0}},
      'Perception':{'bonus':3,'points':{'ability':3,'level':0,'trained':0,'armor':0}},
      'Religion':{'bonus':5,'points':{'ability':0,'level':0,'trained':5,'armor':0}},
      'Stealth':{'bonus':-1,'points':{'ability':0,'level':0,'trained':0,'armor':-1}},
      'Streetwise':{'bonus':1,'points':{'ability':1,'level':0,'trained':0,'armor':0}},
      'Thievery':{'bonus':-1,'points':{'ability':0,'level':0,'trained':0,'armor':-1}}},
    'abilities': 
      {'DEX':{'score':11,'config':{'levelup':0,'race':0,'base':11},'mods':{'halflevel':0,'ability':0},'mod':0},
      'CHA':{'score':13,'config':{'levelup':0,'race':0,'base':13},'mods':{'halflevel':0,'ability':1},'mod':1},
      'INT':{'score':10,'config':{'levelup':0,'race':0,'base':10},'mods':{'halflevel':0,'ability':0},'mod':0},
      'WIS':{'score':16,'config':{'levelup':0,'race':2,'base':14},'mods':{'halflevel':0,'ability':3},'mod':3},
      'STR':{'score':16,'config':{'levelup':0,'race':0,'base':16},'mods':{'halflevel':0,'ability':3},'mod':3},
      'CON':{'score':14,'config':{'levelup':0,'race':2,'base':12},'mods':{'halflevel':0,'ability':2},'mod':2}},
    'defenses': 
      {'WILL':{'score': 15,'config':{'base':10,'class':2,'race':0,'ability':3,'level':0,'armor':0,'item':0}},
      'AC':{'score':17,'config':{'base':10,'class':0,'race':0,'ability':0,'level':0,'armor':7,'item':0}},
      'REF':{'score':11,'config':{'base':10,'class':0,'race':0,'ability':0,'level':0,'armor':1,'item': 0}},
      'FORT':{'score':13,'config':{'base':10,'class':0,'race':0,'ability':3,'level':0,'armor':0,'item':0}}}},
  'hit_points':{'surge_recharge':9600,'hp':26,'surge':6},
  'items': 
    {'gear': [],
    'armor': ['Chainmail', 'Light Shield'],
    'rings': [],
    'weapons': ['Warhammer', 'Crossbow'],
    'artifacts': [],
    'potions': []},
  'speed': 5,
  'alignment': 'Good',
  'size': 'Medium',
  'languages': ['Common', 'Dwarven']}]
  
