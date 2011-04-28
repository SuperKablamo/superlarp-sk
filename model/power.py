# ============================================================================
# Copyright (c) 2011, SuperKablamo, LLC.
# All rights reserved.
# info@superkablamo.com
#
# Power.py defines the Data and Methods for providing Powers to the game 
# world.
#
# ============================================================================

############################# SK IMPORTS #####################################
############################################################################## 
import models

from utils import roll
from settings import *

############################# GAE IMPORTS ####################################
##############################################################################
import logging

from google.appengine.ext import db
from random import choice

############################# CONSTANTS ######################################
##############################################################################
UTILITY = 10 
ENCOUNTER = 3600
DAILY = 43200

######################## METHODS #############################################
##############################################################################
def seedAttacks():
    """Primes the datastore with Attacks data.
    """
    _trace = TRACE+'seedAttacks() '
    logging.info(_trace)
    attacks = []   
         
    for x in ATTACK_DATA:    
        logging.info(_trace+'x = '+str(x))
        damage_keywords = []
        casts = []
        for a in x['damage_keywords']:
            damage_keywords.append(a)
        for a in x['casts']:
            casts.append(a)            

        attack = models.Attack(key_name = x['name'],
                               name = x['name'],
                               description = x['description'],
                               recharge = x['recharge'],
                               level = x['level'],
                               source_keyword = x['source_keyword'],
                               accessory_keyword = x['accessory_keyword'],
                               damage_keywords = damage_keywords,
                               casts = casts,
                               ranges = x['ranges'],
                               attack_ability = x['attack_ability'],
                               attack_mod = x['attack_mod'],
                               defense_ability = x['defense_ability'],
                               damage_weapon_multiplier = x['damage_weapon_multiplier'],
                               damage_ability_mod = x['damage_ability_mod'],
                               damage_dice = x['damage_dice'],
                               damage_die = x['damage_die'],
                               max_targets =  x['max_targets'],
                               max_attacks = x['max_attacks'])
        
        attack.json = getJSONPower(models.ATT, attack)
        attacks.append(attack)      
        
    db.put(attacks)                         
    return

def getJSONPower(model_name, model):
    json = {'name': model.name, 'description': model.description, 
            'recharge': model.recharge, 'level': model.level, 
            'source_keyword': model.source_keyword, 'casts': model.casts}

    # Construct JSON specific to the subclass        
    if model_name == models.ATT:
        json['damage_keywords'] = model.damage_keywords
        json['accessory_keyword'] = model.accessory_keyword
        json['ranges'] = model.ranges
        json['attack_ability'] = model.attack_ability
        json['attack_mod'] = model.attack_mod
        json['defense_ability'] = model.defense_ability
        json['damage_weapon_multiplier'] = model.damage_weapon_multiplier
        json['damage_ability_mod'] = model.damage_ability_mod
        json['damage_dice'] = model.damage_dice
        json['damage_die'] = model.damage_die
        json['effect'] = model.effect
        json['max_targets'] = model.max_targets
        json['max_attacks'] = model.max_attacks    

    elif model_name == models.UTL:
        json['foo'] = model.foo

    elif model_name == models.HEL:
        json['hit_points'] = model.hit_points
        json['effect_range'] = model.effect_range

    return json
    
######################## DATA ################################################
##############################################################################
ATTACK_DATA = [

  ############################## FIGHTER ATTACKS  ############################
  {'name': 'Sure Strike',
  'description': 'Trade power for precision.', 
  'casts': ['Fighter'],
  'level': 1,           
  'recharge': UTILITY,
  'source_keyword': 'Martial',
  'accessory_keyword': 'Weapon',
  'damage_keywords': [],    
  'max_targets': 1,
  'max_attacks': 1,
  'ranges': 1000,
  'attack_ability': 'STR',      
  'attack_mod': 2, 
  'defense_ability': 'AC',
  'damage_die': 0,
  'damage_dice': 0,
  'damage_weapon_multiplier': 1,  
  'damage_ability_mod': None},
  {'name': 'Furious Strike',
  'description': 'Unleash your anger.', 
  'casts': ['Fighter'],
  'level': 1,           
  'recharge': ENCOUNTER,
  'source_keyword': 'Martial',
  'accessory_keyword': 'Weapon',
  'damage_keywords': [],    
  'max_targets': 1,
  'max_attacks': 1,
  'ranges': 1000,
  'attack_ability': 'STR',      
  'attack_mod': 0, 
  'defense_ability': 'AC',
  'damage_die': 0,
  'damage_dice': 0,
  'damage_weapon_multiplier': 2,  
  'damage_ability_mod': 'STR'},
  {'name': 'Brute Strike',
  'description': 'Shatter armor and bone with your might.', 
  'casts': ['Fighter'],
  'level': 1,           
  'recharge': DAILY,
  'source_keyword': 'Martial',
  'accessory_keyword': 'Weapon',
  'damage_keywords': [],    
  'max_targets': 1,
  'max_attacks': 1,
  'ranges': 1000,
  'attack_ability': 'STR',      
  'attack_mod': 0, 
  'defense_ability': 'AC',
  'damage_die': 0,
  'damage_dice': 0,
  'damage_weapon_multiplier': 3,  
  'damage_ability_mod': 'STR'},    
  
  ############################## ROGUE ATTACKS  ##############################
       
  {'name': 'Piercing Strike',
  'casts': ['Rogue'],
  'level': 1,      
  'description': 'Exploit the weakness in your foe\'s armor.',      
  'recharge': UTILITY,
  'source_keyword': 'Martial',
  'accessory_keyword': 'Weapon',
  'damage_keywords': [],     
  'effect_keyword': None,
  'ranges': 1000,
  'max_targets': 1,
  'max_attacks': 1,
  'attack_ability': 'DEX',
  'attack_mod': 0,
  'defense_ability': 'AC',
  'damage_die': 0,
  'damage_dice': 0,     
  'damage_weapon_multiplier': 1,
  'damage_ability_mod': 'DEX'},
  {'name': 'Torturous Strike',
  'casts': ['Rogue'],
  'level': 1,      
  'description': 'Twist the blade for maximum pain.',      
  'recharge': ENCOUNTER,
  'source_keyword': 'Martial',
  'accessory_keyword': 'Weapon',
  'damage_keywords': [],
  'effect_keyword': None,
  'ranges': 1000,
  'max_targets': 1,
  'max_attacks': 1,
  'attack_ability': 'DEX',
  'attack_mod': 0,
  'defense_ability': 'AC',
  'damage_die': 0,
  'damage_dice': 0,     
  'damage_weapon_multiplier': 2,
  'damage_ability_mod': 'DEX'},
  {'name': 'Sly Strike',
  'casts': ['Rogue'],
  'level': 1,      
  'description': 'Lure your foe in by feinting injury.',      
  'recharge': ENCOUNTER,
  'source_keyword': 'Martial',
  'accessory_keyword': 'Weapon',
  'damage_keywords': [],
  'effect_keyword': None,
  'ranges': 1110,
  'max_targets': 1,
  'max_attacks': 1,
  'attack_ability': 'DEX',
  'attack_mod': 2,
  'defense_ability': 'AC',
  'damage_die': 0,
  'damage_dice': 0,     
  'damage_weapon_multiplier': 3,
  'damage_ability_mod': 'DEX'},

  ############################## WIZARD ATTACKS  #############################
  {'name': 'Magic Missile',
  'casts': ['Wizard'],
  'level': 1,      
  'description': 'A missile of magical energy darts forth from your fingertip and strikes your enemy.',      
  'recharge': UTILITY,
  'source_keyword': 'Arcane',
  'accessory_keyword': 'Implement',
  'damage_keywords': ['Force'],
  'effect_keyword': None,
  'ranges': 1100,
  'max_targets': 1,
  'max_attacks': 1,
  'attack_ability': 'INT',
  'attack_mod': 0,
  'defense_ability': 'REF',
  'damage_die': 2,
  'damage_dice': 4,     
  'damage_weapon_multiplier': 0,
  'damage_ability_mod': 'INT'},
  {'name': 'Ray of Frost',
  'casts': ['Wizard'],
  'level': 1,      
  'description': 'A ray of freezing air and ice projects from your pointing finger.',      
  'recharge': UTILITY,
  'source_keyword': 'Arcane',
  'accessory_keyword': 'Implement',
  'damage_keywords': ['Cold'],
  'effect_keyword': None,
  'ranges': 1100,
  'max_targets': 1,
  'max_attacks': 1,
  'attack_ability': 'INT',
  'attack_mod': 0,
  'defense_ability': 'FORT',
  'damage_die': 1,
  'damage_dice': 6,     
  'damage_weapon_multiplier': 0,
  'damage_ability_mod': 'INT'},  
  {'name': 'Burning Hands',
  'casts': ['Wizard'],
  'level': 1,      
  'description': 'A cone of searing flame shoots from your fingertips.',      
  'recharge': ENCOUNTER,
  'source_keyword': 'Arcane',
  'accessory_keyword': 'Implement',
  'damage_keywords': ['Fire'],
  'effect_keyword': None,
  'ranges': 1100,
  'max_targets': 3,
  'max_attacks': 1,
  'attack_ability': 'INT',
  'attack_mod': 0,
  'defense_ability': 'REF',
  'damage_die': 2,
  'damage_dice': 6,     
  'damage_weapon_multiplier': 0,
  'damage_ability_mod': 'INT'},  
  {'name': 'Acid Arrow',
  'casts': ['Wizard'],
  'level': 1,      
  'description': 'A magical arrow of acid springs from your hand and speeds to its target.',      
  'recharge': DAILY,
  'source_keyword': 'Arcane',
  'accessory_keyword': 'Implement',
  'damage_keywords': ['Acid'],
  'effect_keyword': None,
  'ranges': 1100,
  'max_targets': 1,
  'max_attacks': 1,
  'attack_ability': 'INT',
  'attack_mod': 0,
  'defense_ability': 'REF',
  'damage_die': 3,
  'damage_dice': 8,     
  'damage_weapon_multiplier': 0,
  'damage_ability_mod': 'INT'}, 
 
  ############################## CLERIC ATTACKS  #############################
  {'name': 'Weapon of Faith',
  'casts': ['Cleric'],
  'level': 1,      
  'description': 'Your weapon radiates brilliant rays of divine light, searing your enemy.',      
  'recharge': UTILITY,
  'source_keyword': 'Divine',
  'accessory_keyword': 'Weapon',
  'damage_keywords': ['Radiant'],
  'effect_keyword': None,
  'ranges': 1000,
  'max_targets': 1,
  'max_attacks': 1,
  'attack_ability': 'WIS',
  'attack_mod': 0,
  'defense_ability': 'REF',
  'damage_die': 1,
  'damage_dice': 8,     
  'damage_weapon_multiplier': 0,
  'damage_ability_mod': 'WIS'}, 
  {'name': 'Spoken Word',
  'casts': ['Cleric'],
  'level': 1,      
  'description': 'A whisper channels the voice of your diety into a thunderous voice heard only by your foe, gripping your enemey in fear.',      
  'recharge': ENCOUNTER,
  'source_keyword': 'Divine',
  'accessory_keyword': 'Implement',
  'damage_keywords': ['Fear'],
  'effect_keyword': None,
  'ranges': 1000,
  'max_targets': 1,
  'max_attacks': 1,
  'attack_ability': 'WIS',
  'attack_mod': 0,
  'defense_ability': 'WILL',
  'damage_die': 2,
  'damage_dice': 6,     
  'damage_weapon_multiplier': 0,
  'damage_ability_mod': 'WIS'},
  {'name': 'Cleansing Flame',
  'casts': ['Cleric'],
  'level': 1,      
  'description': 'Your weapon bursts into flames as you strike, enveloping your enemy in fire.',      
  'recharge': ENCOUNTER,
  'source_keyword': 'Divine',
  'accessory_keyword': 'Weapon',
  'damage_keywords': ['Fire'],
  'effect_keyword': None,
  'ranges': 1000,
  'max_targets': 1,
  'max_attacks': 1,
  'attack_ability': 'STR',
  'attack_mod': 0,
  'defense_ability': 'AC',
  'damage_die': 1,
  'damage_dice': 6,     
  'damage_weapon_multiplier': 2,
  'damage_ability_mod': 'STR'}] 
  

     