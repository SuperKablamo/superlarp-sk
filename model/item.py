# ============================================================================
# Copyright (c) 2011, SuperKablamo, LLC.
# All rights reserved.
# info@superkablamo.com
#
# Item.py defines the Data and Methods for providing Items to the game 
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

######################## METHODS #############################################
##############################################################################
def seedWeapons():
    """Primes the datastore with Weapons data.
    """
    _trace = TRACE+'seedWeapons() '
    logging.info(_trace)
    weapons = []
    for x in WEAPON_DATA:
        logging.info(_trace+' x = '+str(x))        
        casts = []
        attributes = []
        for a in x['casts']:
            casts.append(a)
        for a in x['attributes']:
            attributes.append(a)
            
        # These are optional properties and may not be in the seed data.    
        keys = x.keys()
        if 'implement' in keys: 
            implement = x['implement']
        else: implement = None
        if 'attack_bonus' in keys: 
            attack_bonus = x['attack_bonus']
        else: attack_bonus = None
        if 'damage_bonus' in keys: 
            damage_bonus = x['damage_bonus']
        else: damage_bonus = None
        if 'critical_damage_die' in keys: 
            critical_damage_die = x['critical_damage_die']
        else: critical_damage_die = None
        if 'critical_damage_dice' in keys: 
            critical_damage_dice = x['critical_damage_dice']
        else: critical_damage_dice = None
        if 'defense_type_bonus' in keys: 
            defense_type_bonus = x['defense_type_bonus']
        else: defense_type_bonus = None
        if 'defense_bonus' in keys: 
            defense_bonus = x['defense_bonus']
        else: defense_bonus = None
                                             
        weapon = models.Weapon(key_name = x['name'],
                               proficiency = x['proficiency'],        
                               name = x['name'],
                               damage_die = x['damage_die'],
                               damage_dice = x['damage_dice'],                               
                               ranges = x['ranges'],
                               price = x['price'],                               
                               weight = x['weight'],
                               slot = x['slot'],
                               group = x['group'],
                               attributes = attributes,
                               category = x['category'],
                               casts = casts,
                               magic = x['magic'],
                               implmement = implement,
                               attack_bonus = attack_bonus,
                               damage_bonus = damage_bonus,
                               critical_damage_die = critical_damage_die,
                               critical_damage_dice = critical_damage_dice,
                               defense_type_bonus = defense_type_bonus,
                               defense_bonus = defense_bonus)          
        
        weapon.json = getJSONItem(models.WPN, weapon)
        weapons.append(weapon)
    
    db.put(weapons)    
    return

def seedArmor():
    """Primes the datastore with Armor data.
    """
    _trace = TRACE+'seedArmor() '
    logging.info(_trace)
    armors = []
    for x in ARMOR_DATA:
        logging.info(_trace+' x = '+str(x))        
        casts = []
        for a in x['casts']:
            casts.append(a)

        # These are optional properties and may not be in the seed data.    
        keys = x.keys()        
        if 'defense_type_bonus' in keys: 
            defense_type_bonus = x['defense_type_bonus']
        else: defense_type_bonus = None
        if 'defense_bonus' in keys: 
            defense_bonus = x['defense_bonus']
        else: defense_bonus = None
        
        armor = models.Armor(key_name = x['name'],        
                             name = x['name'],
                             bonus = x['bonus'],
                             check = x['check'],
                             speed = x['speed'],
                             price = x['price'],                               
                             weight = x['weight'],
                             slot = x['slot'],
                             category = x['category'],
                             casts = casts,
                             magic = x['magic'],
                             defense_type_bonus = defense_type_bonus,
                             defense_bonus = defense_bonus)          
        
        armor.json = getJSONItem(models.ARM, armor)
        armors.append(armor)
    
    db.put(armors)    
    return

def getJSONItem(model_name, model):
    json = {'name': model.name, 'description': model.description, 
            'level': model.level, 'slot': model.slot, 'price': model.price,
            'casts': model.casts, 'weight': model.weight, 
            'magic': model.magic, 
            'ability_type_bonus': model.ability_type_bonus,
            'ability_bonus': model.ability_bonus}
            
    if model.power is not None:
        json['power'] = model.power.name        

    # Construct JSON specific to the subclass             
    if model_name == models.WPN:
        json['damage_die'] = model.damage_die
        json['damage_dice'] = model.damage_dice
        json['group'] = model.group
        json['attributes'] = model.attributes
        json['ranges'] = model.ranges
        json['proficiency'] = model.proficiency
        json['attack_bonus'] = model.attack_bonus
        json['damage_bonus'] = model.damage_bonus
        json['critical_damage_die'] = model.critical_damage_die
        json['critical_damage_dice'] = model.critical_damage_dice
        json['defense_type_bonus'] = model.defense_type_bonus
        json['defense_bonus'] = model.defense_bonus
        json['implement'] = model.implement                              
        
    elif model_name == models.ARM:
        json['bonus'] = model.bonus
        json['check'] = model.check
        json['speed'] = model.speed
                            
    elif model_name == models.IMP:
        json['category'] = model.category
    
    elif model_name == models.GEA:  
        json['foo'] = model.foo
        
    return json
        
######################## DATA ################################################
##############################################################################
WEAPON_DATA = [

  ############################## SIMPLE MELEE  ###############################
  {'name': 'Dagger',
  'proficiency': 3,
  'damage_dice': 1,
  'damage_die': 4,
  'ranges': 1100,
  'price': 1,
  'weight': 1,
  'slot': 'One-Hand',
  'group': 'Light Blade',
  'attributes': ['Off-hand', 'Light Thrown'],
  'category': 'Simple Melee',
  'casts': ['Fighter', 'Rogue', 'Wizard', 'Cleric'],
  'magic': False},
  {'name': 'Mace',
  'proficiency': 2,
  'damage_dice': 1,
  'damage_die': 8,
  'ranges': 1000,
  'price': 5,
  'weight': 6,
  'slot': 'One-Hand',
  'group': 'Mace',
  'attributes': ['Versatile'],
  'category': 'Simple Melee',
  'casts': ['Fighter', 'Cleric'],
  'magic': False},
  {'name': 'Spear',
  'proficiency': 2,
  'damage_dice': 1,
  'damage_die': 8,
  'ranges': 1000,
  'price': 5,
  'weight': 6,
  'slot': 'One-Hand',
  'group': 'Spear',
  'attributes': ['Versatile'],
  'category': 'Simple Melee',
  'casts': ['Fighter', 'Cleric'],
  'magic': False},  
  {'name': 'Morningstar',
  'proficiency': 2,
  'damage_dice': 1,
  'damage_die': 10,
  'ranges': 1000,
  'price': 10,
  'weight': 8,
  'slot': 'Two-Hand',
  'group': 'Mace',
  'attributes': [],
  'category': 'Simple Melee',
  'casts': ['Fighter', 'Cleric'],
  'magic': False},  
  {'name': 'Quarterstaff',
  'proficiency': 2,
  'damage_dice': 1,
  'damage_die': 8,
  'ranges': 1000,
  'price': 5,
  'weight': 10,
  'slot': 'Two-Hand',
  'group': 'Staff',
  'attributes': [],
  'category': 'Simple Melee',
  'casts': ['Fighter', 'Cleric', 'Wizard'],
  'magic': False},
  {'name': 'Staff of Defense',
  'proficiency': 2,
  'damage_dice': 1,
  'damage_die': 8,
  'ranges': 1000,
  'price': 5,
  'weight': 10,
  'slot': 'Two-Hand',
  'group': 'Staff',
  'attributes': [],
  'category': 'Simple Melee',
  'casts': ['Wizard'],
  'magic': True,
  'implement': True,
  'defense_type_bonus': 'AC',
  'defense_bonus': 1},

  ############################## MARTIAL MELEE  ##############################
  {'name': 'Battleaxe',
  'proficiency': 2,
  'damage_dice': 1,
  'damage_die': 10,
  'ranges': 1000,
  'price': 15,
  'weight': 6,
  'slot': 'One-Hand',
  'group': 'Axe',
  'attributes': ['Versatile'],
  'category': 'Martial Melee',
  'casts': ['Fighter'],
  'magic': False},
  {'name': 'Longsword',
  'proficiency': 3,
  'damage_dice': 1,
  'damage_die': 8,
  'ranges': 1000,
  'price': 15,
  'weight': 4,
  'slot': 'One-Hand',
  'group': 'Heavy Blade',
  'attributes': ['Versatile'],
  'category': 'Martial Melee',
  'casts': ['Fighter'],
  'magic': False},
  {'name': 'Shortsword',
  'proficiency': 3,
  'damage_dice': 1,
  'damage_die': 6,
  'ranges': 1000,
  'price': 10,
  'weight': 2,
  'slot': 'One-Hand',
  'group': 'Light Blade',
  'attributes': ['Off-hand'],
  'category': 'Martial Melee',
  'casts': ['Fighter', 'Rogue'],
  'magic': False},
  {'name': 'Warhammer',
  'proficiency': 2,
  'damage_dice': 1,
  'damage_die': 10,
  'ranges': 1000,
  'price': 15,
  'weight': 5,
  'slot': 'One-Hand',
  'group': 'Hammer',
  'attributes': ['Versatile'],
  'category': 'Martial Melee',
  'casts': ['Cleric', 'Fighter'],
  'magic': False},
  {'name': 'Greataxe',
  'proficiency': 2,
  'damage_dice': 1,
  'damage_die': 12,
  'ranges': 1000,
  'price': 30,
  'weight': 12,
  'slot': 'Two-Hand',
  'group': 'Axe',
  'attributes': ['High Critical'],
  'category': 'Martial Melee',
  'casts': ['Fighter'],
  'magic': False},
  {'name': 'Greatsword',
  'proficiency': 3,
  'damage_dice': 1,
  'damage_die': 10,
  'ranges': 1000,
  'price': 30,
  'weight': 8,
  'slot': 'Two-Hand',
  'group': 'Heavy Blade',
  'attributes': [],
  'category': 'Martial Melee',
  'casts': ['Fighter'],
  'magic': False},
      
  ############################## IMPROVISED MELEE ############################
  {'name': 'Unarmed',
  'proficiency': 0,
  'damage_dice': 1,
  'damage_die': 4,
  'ranges': 1000,
  'price': 0,
  'weight': 0,
  'slot': 'One-Hand',
  'group': 'Unarmed',
  'attributes': [],
  'category': 'Improvised Melee',
  'casts': ['Fighter', 'Cleric', 'Wizard', 'Rogue'],
  'magic': False},
  
  ############################## SIMPLE RANGED ###############################
  {'name': 'Hand Crossbow',
  'proficiency': 2,
  'damage_dice': 1,
  'damage_die': 6,
  'ranges': 1100,
  'price': 25,
  'weight': 2,
  'slot': 'One-Hand',
  'group': 'Crossbow',
  'attributes': ['Load Free'],
  'category': 'Simple Ranged',
  'casts': ['Fighter', 'Cleric', 'Rogue'],
  'magic': False},
  {'name': 'Sling',
  'proficiency': 2,
  'damage_dice': 1,
  'damage_die': 6,
  'ranges': 1100,
  'price': 1,
  'weight': 1,
  'slot': 'One-Hand',
  'group': 'Sling',
  'attributes': ['Load Free'],
  'category': 'Simple Ranged',
  'casts': ['Fighter', 'Cleric', 'Rogue'],
  'magic': False},
  {'name': 'Crossbow',
  'proficiency': 2,
  'damage_dice': 1,
  'damage_die': 8,
  'ranges': 1110,
  'price': 25,
  'weight': 4,
  'slot': 'Two-Hand',
  'group': 'Crossbow',
  'attributes': ['Load Minor'],
  'category': 'Simple Ranged',
  'casts': ['Fighter', 'Cleric'],
  'magic': False},  
    
  ############################## MARTIAL RANGED ##############################
  {'name': 'Longbow',
  'proficiency': 2,
  'damage_dice': 1,
  'damage_die': 10,
  'ranges': 1111,
  'price': 30,
  'weight': 3,
  'slot': 'Two-Hand',
  'group': 'Bow',
  'attributes': ['Load Free'],
  'category': 'Martial Ranged',
  'casts': ['Fighter'],
  'magic': False},
  {'name': 'Shortbow',
  'proficiency': 2,
  'damage_dice': 1,
  'damage_die': 8,
  'ranges': 1110,
  'price': 25,
  'weight': 2,
  'slot': 'Two-Hand',
  'group': 'Bow',
  'attributes': ['Load Free', 'Small'],
  'category': 'Martial Ranged',
  'casts': ['Fighter'],
  'magic': False}]

ARMOR_DATA = [

  ############################## LIGHT  ######################################
  {'name': 'Cloth',
  'bonus': 0,
  'check': 0,
  'speed': 0,
  'price': 1,
  'weight': 4,
  'slot': 'Body',
  'category': 'Light',
  'casts': ['Cleric', 'Fighter', 'Rogue', 'Wizard'],
  'magic': False},
  {'name': 'Leather',
  'bonus': 2,
  'check': 0,
  'speed': 0,
  'price': 25,
  'weight': 15,
  'slot': 'Body',  
  'category': 'Light',
  'casts': ['Cleric', 'Fighter', 'Rogue'],
  'magic': False},  
  {'name': 'Hide',
  'bonus': 3,
  'check': -1,
  'speed': 0,
  'price': 30,
  'weight': 25,
  'slot': 'Body',  
  'category': 'Light',
  'casts': ['Cleric', 'Fighter'],
  'magic': False},
   
  ############################## HEAVY  ######################################  
  {'name': 'Chainmail',
  'bonus': 6,
  'check': -1,
  'speed': -1,
  'price': 40,
  'weight': 40,
  'slot': 'Body',  
  'category': 'Heavy',
  'casts': ['Fighter'],
  'magic': False},
  {'name': 'Scale',
  'bonus': 7,
  'check': 0,
  'speed': -1,
  'price': 45,
  'weight': 45,
  'slot': 'Body',  
  'category': 'Heavy',
  'casts': ['Fighter'],
  'magic': False},
  {'name': 'Plate',
  'bonus': 8,
  'check': -2,
  'speed': -1,
  'price': 50,
  'weight': 50,
  'slot': 'Body',  
  'category': 'Heavy',
  'casts': ['Fighter'],
  'magic': False},
      
  ############################## SHIELD  #####################################
  {'name': 'Light Shield',
  'bonus': 1,
  'check': 0,
  'speed': 0,
  'price': 5,
  'weight': 6,
  'slot': 'One-Hand',  
  'category': 'Shield',
  'casts': ['Fighter', 'Cleric'],
  'magic': False},
  {'name': 'Heavy Shield',
  'bonus': 2,
  'check': 0,
  'speed': 0,
  'price': 10,
  'weight': 15,
  'slot': 'One-hand',  
  'category': 'Shield',
  'casts': ['Fighter'],
  'magic': False}]
