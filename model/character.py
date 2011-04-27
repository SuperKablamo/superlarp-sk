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
    json = {'name': player.name, 'level': player.level, 'race': player.race,
            'alignment': player.alignment, 'size': player.size, 
            'experience': player.experience, 'speed': player.speed, 
            'hit_points': player.hit_points, 'cast': player.cast, 
            'height': player.height, 'weight': player.weight, 
            'scores': player.scores, 'created': str(player.created), 
            'purse': player.purse, 'resist': player.resist,
            'vulnerable': player.vulnerable, 'id': str(player.key().id())}
            
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
     
    # Construct JSON for Player immunities
    immunities = []
    for i in player.immunities:
        immunities.appened(i)
    
    json['immunities'] = immunities
    json['powers'] = powers_json 
    json['items'] = items_json
    return json

def getJSONNonPlayer(nonplayer):
    json = {'name': nonplayer.name, 'level': nonplayer.level, 
            'race': nonplayer.race, 'alignment': nonplayer.alignment, 
            'size': nonplayer.size, 'experience': nonplayer.experience, 
            'speed': nonplayer.speed, 'hit_points': nonplayer.hit_points, 
            'scores': nonplayer.scores, 'description': nonplayer.description,
            'origin': nonplayer.origin, 'category': nonplayer.category,
            'actions': nonplayer.actions, 'unique': nonplayer.unique,
            'role': nonplayer.role, 'challenge': nonplayer.challenge,
            'keywords': nonplayer.keywords, 'artifacts': nonplayer.artifacts,
            'languages': nonplayer.languages, 
            'resistance': nonplayer.resistance,
            'vulnerable': nonplayer.vulnerable,
            'created': str(nonplayer.created),
            'id': str(nonplayer.key().id())}
    
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

def buildPCTemplates():
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
  'level': 1,
  'experience': 0,
  'immunities': [],
  'purse': {'copper': 0, 'silver': 0, 'gold': 100, 'platinum': 0, 'gems': 0},
  'resistance': None,
  'vulnerable': None,
  'powers': 
    {'attacks':
      [{'name': 'Cleave',
      'description': 'You hit one enemy, then cleave into another.',
      'level': 1,
      'recharge': UTILITY,
      'casts': ['Fighter'],
      'accessory_keyword': 'Weapon',      
      'source_keyword': 'Martial',            
      'defense_ability': 'AC',
      'attack_ability': 'STR',
      'max_attacks': 1,
      'max_targets': 2,
      'attack_range': 0,
      'attack_mod': 0,
      'damage_die': 0,
      'damage_dice': 0,
      'damage_mod': 0,
      'damage_weapon_multiplier': 1,
      'damage_ability_mod': None,
      'miss': 0,
      'effect': None,
      'effect_keyword': None,
      'damage_keywords': []},
      {'name': 'Reaping Strike',
      'description': 'You punctuate your scything attacks with a wicked jabs and small cutting blows that slip through your enemy\'s defenses.',
      'level': 1,
      'recharge': UTILITY,
      'casts': ['Fighter'],
      'accessory_keyword': 'Weapon',      
      'source_keyword': 'Martial',            
      'defense_ability': 'AC',
      'attack_ability': 'STR',
      'max_attacks': 1,
      'max_targets': 1,
      'attack_range': 0,
      'attack_mod': 0,
      'damage_die': 0,
      'damage_dice': 0,
      'damage_mod': 0,
      'damage_weapon_multiplier': 1,
      'damage_ability_mod': None,
      'miss': 4,
      'effect': None,
      'effect_keyword': None,
      'damage_keywords': []},
      {'name': 'Sure Strike',
      'description': 'You trade power for precision.',
      'level': 1,
      'recharge': UTILITY,
      'casts': ['Fighter'],
      'accessory_keyword': 'Weapon',      
      'source_keyword': 'Martial',            
      'defense_ability': 'AC',
      'attack_ability': 'STR',
      'max_attacks': 1,
      'max_targets': 1,
      'attack_range': 0,
      'attack_mod': 2,
      'damage_die': 0,
      'damage_dice': 0,
      'damage_mod': 0,
      'damage_weapon_multiplier': 1,
      'damage_ability_mod': None,
      'miss': 4,
      'effect': None,
      'effect_keyword': None,
      'damage_keywords': []},      
      {'name': 'Spinning Sweep',
      'description': 'You spin beneath your enemy\'s guard with a long, powerful cut and then sweep your leg through his an instant later to knock him head over heels.',
      'level': 1,
      'recharge': ENCOUNTER,
      'casts': ['Fighter'],
      'accessory_keyword': 'Weapon',      
      'source_keyword': 'Martial',            
      'defense_ability': 'AC',
      'attack_ability': 'STR',
      'max_attacks': 1,
      'max_targets': 1,
      'attack_range': 0,
      'attack_mod': 0,
      'damage_die': 0,
      'damage_dice': 0,
      'damage_mod': 0,
      'damage_weapon_multiplier': 1,
      'damage_ability_mod': None,
      'miss': 0,
      'effect': None,
      'effect_keyword': 'Prone',
      'damage_keywords': []},
      {'name': 'Brute Strike',
      'description': 'You shatter armor and bone with a ringing blow!.',
      'level': 1,
      'recharge': DAILY,
      'casts': ['Fighter'],
      'accessory_keyword': 'Weapon',      
      'source_keyword': 'Martial',            
      'defense_ability': 'AC',
      'attack_ability': 'STR',
      'max_attacks': 1,
      'max_targets': 1,
      'attack_range': 0,
      'attack_mod': 0,
      'damage_die': 0,
      'damage_dice': 0,
      'damage_mod': 0,
      'damage_weapon_multiplier': 3,
      'damage_ability_mod': None,
      'miss': 0,
      'effect': None,
      'effect_keyword': None,
      'damage_keywords': []}],      
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
    {'implements': [],
    'gear': [],
    'armor': 
      [{'name': 'Scale',
      'description': None,
      'group': 'Heavy',
      'cost': 45,      
      'attributes': [],
      'casts': ['Fighter'],      
      'magic': False,
      'weight': 45,            
      'slot': 'Body',
      'ac_bonus': 7,
      'min_bonus': 0,
      'check': 0,
      'speed': -1}],
    'rings': [],
    'weapons': 
      [{'name': 'Greatsword',
      'description': None,
      'level': 1,
      'group': 'Heavy Blade',
      'cost': 30,      
      'attributes': [],
      'casts': ['Barbarian','Fighter','Ranger'],      
      'magic': False,
      'weight': 8,      
      'short_range': 0,
      'long_range': 0,            
      'slot': 'Two-hand',
      'proficiency': 3,
      'damage_dice': 1,
      'damage_die': 10},
      {'name': 'Longbow',
      'description': None,
      'level': 1,
      'group': 'Bow',
      'cost': 30,      
      'attributes': ['Load Free'],
      'casts': ['Fighter','Ranger'],      
      'magic': False,
      'weight': 3,      
      'short_range': 30,
      'long_range': 60,            
      'slot': 'Two-hand',
      'proficiency': 2,
      'damage_dice': 1,
      'damage_die': 10}],
    'artifacts': [],
    'potions': []},
  'speed': 6,
  'alignment': 'Good',
  'size': 'Medium'},
  
  ############################## PLAYER TEMPLATE 2 ###########################
  {'template_id': 2,
  'name': 'Human Fighter',
  'cast': 'Fighter',
  'race': 'Human',
  'weight': 80,
  'height': 48,
  'level': 1,
  'experience': 0,
  'immunities': [],
  'purse': {'copper': 0, 'silver': 0, 'gold': 100, 'platinum': 0, 'gems': 0},
  'resistance': None,
  'vulnerable': None,
  'powers': 
    {'attacks':
      [{'name': 'Deft Strike',
      'description': 'A final lunge brings you into an advantageous position.',
      'level': 1,
      'recharge': UTILITY,
      'casts': ['Rogue'],
      'accessory_keyword': 'Weapon',      
      'source_keyword': 'Martial',            
      'defense_ability': 'AC',
      'attack_ability': 'DEX',
      'max_attacks': 1,
      'max_targets': 1,
      'attack_range': 30,
      'attack_mod': 0,
      'damage_die': 0,
      'damage_dice': 0,
      'damage_mod': 0,
      'damage_weapon_multiplier': 1,
      'damage_ability_mod': 'DEX',
      'miss': 0,
      'effect': UTILITY,
      'effect_keyword': 'Slows',
      'damage_keywords': []},
      {'name': 'Sly Flourish',
      'description': 'A distracting flourish causes the enemy to forget the blade at his throat.',
      'level': 1,
      'recharge': UTILITY,
      'casts': ['Rogue'],
      'accessory_keyword': 'Weapon',      
      'source_keyword': 'Martial',            
      'defense_ability': 'AC',
      'attack_ability': 'DEX',
      'max_attacks': 1,
      'max_targets': 1,
      'attack_range': 30,
      'attack_mod': 0,
      'damage_die': 0,
      'damage_dice': 0,
      'damage_mod': 4,
      'damage_weapon_multiplier': 1,
      'damage_ability_mod': 'CHA',
      'miss': 0,
      'effect': None,
      'effect_keyword': None,
      'damage_keywords': []},
      {'name': 'Positioning Strike',
      'description': 'A false stumble and a shove place the enemy exactlky where you want him.',
      'level': 1,
      'recharge': ENCOUNTER,
      'casts': ['Fighter'],
      'accessory_keyword': 'Weapon',      
      'source_keyword': 'Martial',            
      'defense_ability': 'AC',
      'attack_ability': 'STR',
      'max_attacks': 1,
      'max_targets': 1,
      'attack_range': 0,
      'attack_mod': 0,
      'damage_die': 0,
      'damage_dice': 0,
      'damage_mod': 0,
      'damage_weapon_multiplier': 1,
      'damage_ability_mod': 'DEX',
      'miss': 4,
      'effect': UTILITY*3,
      'effect_keyword': 'Slows',
      'damage_keywords': []},      
      {'name': 'Trick Strike',
      'description': 'You spin beneath your enemy\'s guard with a long, powerful cut and then sweep your leg through his an instant later to knock him head over heels.',
      'level': 1,
      'recharge': ENCOUNTER,
      'casts': ['Rogue'],
      'accessory_keyword': 'Weapon',      
      'source_keyword': 'Martial',            
      'defense_ability': 'AC',
      'attack_ability': 'DEX',
      'max_attacks': 1,
      'max_targets': 1,
      'attack_range': 30,
      'attack_mod': 0,
      'damage_die': 0,
      'damage_dice': 0,
      'damage_mod': 0,
      'damage_weapon_multiplier': 3,
      'damage_ability_mod': 'DEX',
      'miss': 0,
      'effect': UTILITY,
      'effect_keyword': 'Slows',
      'damage_keywords': []}],
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
    {'implements': [],
    'gear': [],
    'armor':  
      [{'name': 'Leather',
      'description': None,
      'group': 'Light',
      'cost': 25,      
      'attributes': [],
      'casts': ['Barbarian','Fighter','Ranger','Rogue','Wizard','Cleric'],      
      'magic': False,
      'weight': 15,            
      'slot': 'Body',
      'ac_bonus': 2,
      'min_bonus': 0,
      'check': 0,
      'speed': 0}],
    'rings': [],
    'weapons': 
      [{'name': 'Shortsword',
      'description': None,
      'level': 1,
      'group': 'Light Blade',
      'cost': 10,      
      'attributes': ['Off-hand'],
      'casts': ['Barbarian','Fighter','Ranger','Rogue','Cleric'],      
      'magic': False,
      'weight': 2,      
      'short_range': 0,
      'long_range': 0,            
      'slot': 'One-hand',
      'proficiency': 3,
      'damage_dice': 1,
      'damage_die': 6},
      {'name': 'Dagger',
      'description': None,
      'level': 1,
      'group': 'Light Blade',
      'cost': 1,      
      'attributes': ['Off-hand', 'Light Thrown'],
      'casts': ['Barbarian','Fighter','Ranger','Rogue','Wizard','Cleric'],      
      'magic': False,
      'weight': 1,      
      'short_range': 15,
      'long_range': 20,            
      'slot': 'One-hand',
      'proficiency': 3,
      'damage_dice': 1,
      'damage_die': 4}],
    'artifacts': [],
    'potions': []},
  'speed': 6,
  'alignment': 'Good',
  'size': 'Small'},  

  ############################## PLAYER TEMPLATE 3 ###########################
  {'template_id': 3,
  'name': 'Elf Wizard',
  'cast': 'Wizard',
  'race': 'Elf',
  'weight': 120,
  'height': 64,
  'level': 1,
  'experience': 0,
  'immunities': [],
  'purse': {'copper': 0, 'silver': 0, 'gold': 100, 'platinum': 0, 'gems': 0},
  'resistance': None,
  'vulnerable': None,
  'powers': 
    {'attacks':
      [{'name': 'Cloud of Daggers',
      'description': 'You create a small cloud of whirling daggers of force that relentlessy attack creatures in the area.',
      'level': 1,
      'recharge': UTILITY,
      'casts': ['Wizard'],
      'accessory_keyword': 'Implement',      
      'source_keyword': 'Arcane',            
      'defense_ability': 'REF',
      'attack_ability': 'INT',
      'max_attacks': 1,
      'max_targets': 1,
      'attack_range': 30,
      'attack_mod': 0,
      'damage_die': 2,
      'damage_dice': 4,
      'damage_mod': 0,
      'damage_weapon_multiplier': 0,
      'damage_ability_mod': 'INT',
      'miss': 0,
      'effect': None,
      'effect_keyword': None,
      'damage_keywords': ['Force']},
      {'name': 'Magic Missile',
      'description': 'You launch a silvery bolt of force at an enemy.',
      'level': 1,
      'recharge': UTILITY,
      'casts': ['Wizard'],
      'accessory_keyword': 'Implement',      
      'source_keyword': 'Arcane',            
      'defense_ability': 'REF',
      'attack_ability': 'INT',
      'max_attacks': 1,
      'max_targets': 1,
      'attack_range': 30,
      'attack_mod': 0,
      'damage_die': 2,
      'damage_dice': 4,
      'damage_mod': 0,
      'damage_weapon_multiplier': 0,
      'damage_ability_mod': 'INT',
      'miss': 0,
      'effect': None,
      'effect_keyword': None,
      'damage_keywords': ['Force']},
      {'name': 'Burning Hands',
      'description': 'A fierce burst of flame erupts from your hands and scorches nearby foes.',
      'level': 1,
      'recharge': ENCOUNTER,
      'casts': ['Wizard'],
      'accessory_keyword': 'Implement',      
      'source_keyword': 'Arcane',            
      'defense_ability': 'REF',
      'attack_ability': 'INT',
      'max_attacks': 1,
      'max_targets': 3,
      'attack_range': 0,
      'attack_mod': 0,
      'damage_die': 2,
      'damage_dice': 6,
      'damage_mod': 0,
      'damage_weapon_multiplier': 0,
      'damage_ability_mod': 'INT',
      'miss': 0,
      'effect': 0,
      'effect_keyword': None,
      'damage_keywords': ['Fire']},      
      {'name': 'Acid Arrow',
      'description': 'A shimmering arrow of green, glowing liquid streaks to your target and bursts in a spray of sizzling acid.',
      'level': 1,
      'recharge': DAILY,
      'casts': ['Wizard'],
      'accessory_keyword': 'Implement',      
      'source_keyword': 'Arcane',            
      'defense_ability': 'REF',
      'attack_ability': 'INT',
      'max_attacks': 1,
      'max_targets': 2,
      'attack_range': 30,
      'attack_mod': 0,
      'damage_die': 2,
      'damage_dice': 8,
      'damage_mod': 0,
      'damage_weapon_multiplier': 3,
      'damage_ability_mod': 'DEX',
      'miss': 6,
      'effect': 0,
      'effect_keyword': None,
      'damage_keywords': ['Acid']}],
    'utilities': 
      [],
    'healing': 
      []},
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
    {'implements': [],
    'gear': [],
    'armor':  
      [{'name': 'Cloth',
      'description': None,
      'group': 'Light',
      'cost': 1,      
      'attributes': [],
      'casts': ['Barbarian','Fighter','Ranger','Rogue','Wizard','Cleric'],      
      'magic': False,
      'weight': 4,            
      'slot': 'Body',
      'ac_bonus': 0,
      'min_bonus': 0,
      'check': 0,
      'speed': 0}],
    'rings': [],
    'weapons': 
      [{'name': 'Staff of Defense',
      'description': None,
      'level': 1,
      'group': 'Staff',
      'cost': 5,      
      'attributes': [],
      'casts': ['Wizard'],      
      'magic': False,
      'weight': 4,      
      'short_range': 0,
      'long_range': 0,            
      'slot': 'Two-hand',
      'proficiency': 2,
      'damage_dice': 1,
      'damage_die': 8,
      'bonus': 1,
      'bonus_type': 'AC'}],
    'artifacts': [],
    'potions': []},
  'speed': 6,
  'alignment': 'Good',
  'size': 'Medium'},

  ############################## PLAYER TEMPLATE 4 ###########################
  {'template_id': 4,
  'name': 'Dwarf Cleric',
  'cast': 'Cleric',
  'race': 'Dwarf',
  'weight': 205,
  'height': 54,
  'level': 1,
  'experience': 0,
  'immunities': [],
  'purse': {'copper': 0, 'silver': 0, 'gold': 100, 'platinum': 0, 'gems': 0},
  'resistance': None,
  'vulnerable': None,
  'powers': 
    {'attacks':
      [{'name': 'Righteous Brand',
      'description': 'You smite your foe with your weapon and brand it with a ghostly, glowing symbol of your deity\'s anger.',
      'level': 1,
      'recharge': UTILITY,
      'casts': ['Cleric'],
      'accessory_keyword': 'Weapon',      
      'source_keyword': 'Divine',            
      'defense_ability': 'AC',
      'attack_ability': 'STR',
      'max_attacks': 1,
      'max_targets': 1,
      'attack_range': 0,
      'attack_mod': 0,
      'damage_die': 0,
      'damage_dice': 0,
      'damage_mod': 0,
      'damage_weapon_multiplier': 1,
      'damage_ability_mod': None,
      'miss': 0,
      'effect': UTILITY,
      'effect_keyword': 'Dazed',
      'damage_keywords': []},
      {'name': 'Priest\'s Prayer',
      'description': 'You utter a prayer as you attack with your weapon.',
      'level': 1,
      'recharge': UTILITY,
      'casts': ['Cleric'],
      'accessory_keyword': 'Weapon',      
      'source_keyword': 'Divine',            
      'defense_ability': 'AC',
      'attack_ability': 'STR',
      'max_attacks': 1,
      'max_targets': 1,
      'attack_range': 0,
      'attack_mod': 0,
      'damage_die': 0,
      'damage_dice': 0,
      'damage_mod': 0,
      'damage_weapon_multiplier': 1,
      'damage_ability_mod': 'STR',
      'miss': 0,
      'effect': None,
      'effect_keyword': None,
      'damage_keywords': []},
      {'name': 'Wrathful Thunder',
      'description': 'Your arm is made strong by the power of your deity.  When you strike, a terrible thunderclap smites your adversary and dazes him.',
      'level': 1,
      'recharge': ENCOUNTER,
      'casts': ['Cleric'],
      'accessory_keyword': 'Weapon',      
      'source_keyword': 'Divine',            
      'defense_ability': 'AC',
      'attack_ability': 'STR',
      'max_attacks': 1,
      'max_targets': 1,
      'attack_range': 0,
      'attack_mod': 0,
      'damage_die': 0,
      'damage_dice': 0,
      'damage_mod': 0,
      'damage_weapon_multiplier': 0,
      'damage_ability_mod': 'STR',
      'miss': 0,
      'effect': UTILITY*3,
      'effect_keyword': 'Dazed',
      'damage_keywords': ['Thunder']},      
      {'name': 'Avenging Flame',
      'description': 'You slam your weapon into your foe, who bursts into flame.  Divine fire avenges each attack your enemy dares to make.',
      'level': 1,
      'recharge': DAILY,
      'casts': ['Cleric'],
      'accessory_keyword': 'Weapon',      
      'source_keyword': 'Divine',            
      'defense_ability': 'AC',
      'attack_ability': 'STR',
      'max_attacks': 1,
      'max_targets': 1,
      'attack_range': 0,
      'attack_mod': 0,
      'damage_die': 2,
      'damage_dice': 8,
      'damage_mod': 5,
      'damage_weapon_multiplier': 2,
      'damage_ability_mod': 'STR',
      'miss': 6,
      'effect': 0,
      'effect_keyword': None,
      'damage_keywords': ['Fire']}],
    'utilities': 
      [],
    'healing': 
      []},
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
    {'implements': [],
    'gear': [],
    'armor':  
      [{'name': 'Chainmail',
      'description': None,
      'group': 'Heavy',
      'cost': 40,      
      'attributes': [],
      'casts': ['Fighter','Cleric'],      
      'magic': False,
      'weight': 40,            
      'slot': 'Body',
      'ac_bonus': 6,
      'min_bonus': 0,
      'check': -1,
      'speed': -1},
      {'name': 'Light Shield',
      'description': None,
      'group': 'Shield',
      'cost': 5,      
      'attributes': [],
      'casts': ['Fighter','Cleric'],      
      'magic': False,
      'weight': 6,            
      'slot': 'One-Hand',
      'ac_bonus': 1,
      'min_bonus': 0,
      'check': 0,
      'speed': 0}],
    'rings': [],
    'weapons': 
      [{'name': 'Warhammer',
      'description': None,
      'level': 1,
      'group': 'Hammer',
      'cost': 5,      
      'attributes': ['Versatile'],
      'casts': ['Cleric','Fighter'],      
      'magic': False,
      'weight': 2,      
      'short_range': 0,
      'long_range': 0,            
      'slot': 'One-hand',
      'proficiency': 2,
      'damage_dice': 1,
      'damage_die': 10,
      'bonus': 0,
      'bonus_type': None},
      {'name': 'Crossbow',
      'description': None,
      'level': 1,
      'group': 'Crossbow',
      'cost': 25,      
      'attributes': ['Load Minor'],
      'casts': ['Cleric','Fighter','Ranger','Rogue','Barbarian'],      
      'magic': False,
      'weight': 4,      
      'short_range': 20,
      'long_range': 40,            
      'slot': 'Two-hand',
      'proficiency': 2,
      'damage_dice': 1,
      'damage_die': 8,
      'bonus': 0,
      'bonus_type': None}],
    'artifacts': [],
    'potions': []},
  'speed': 5,
  'alignment': 'Good',
  'size': 'Medium'}]
  
