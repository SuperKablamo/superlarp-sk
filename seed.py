# ============================================================================
# Copyright (c) 2011, SuperKablamo, LLC.
# All rights reserved.
# info@superkablamo.com
#
# Seed.py defines Data and Methods for seeding the Datastore with game data.
#
# ============================================================================

############################# SK IMPORTS #####################################
############################################################################## 
import models
import rules
import seed

from model import monster
from settings import *

############################# GAE IMPORTS ####################################
##############################################################################
import os
import logging
import time
import urllib2

from django.utils import simplejson
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

######################## CONSTANTS ###########################################
##############################################################################
    
RACE_DATA = [
    {'name': 'Dwarf',
     'motto': 'Masters of stone and iron, dauntless and unyielding in the face of adversity.',
     'ability_bonuses': [{'origin': 'Dwarf', 'type': 'CON', 'mod': 2}, {'origin': 'Dwarf', 'type': 'WIS', 'mod': 2}],    
     'skill_mods': [{'origin': 'Dwarf', 'type': 'Dungeoneering', 'mod': 2}, {'origin': 'Dwarf', 'type': 'Endurance', 'mod': 2}],    
     'defense_mods': [],              
     'size': 'Medium',
     'speed': 5,
     'min_height': 51,
     'max_height': 57,
     'min_weight': 160,
     'max_weight': 220},
    {'name': 'Elf',
     'motto': 'Quick, wary archers who freely roam the forests and wilds.',
     'ability_bonuses': [{'origin': 'Elf', 'type': 'DEX', 'mod': 2}, {'origin': 'Elf', 'type': 'WIS', 'mod': 2}],  
     'skill_mods': [{'origin': 'Elf', 'type': 'Nature', 'mod': 2}, {'origin': 'Elf', 'type': 'Perception', 'mod': 2}], 
     'defense_mods': [],               
     'size': 'Medium',
     'speed': 7,
     'min_height': 64,
     'max_height': 74,
     'min_weight': 130,
     'max_weight': 170},
    {'name' : 'Halfling',
     'motto': 'Quick and resourceful wanderers, small in stature but great in courage.',
     'ability_bonuses': [{'origin': 'Halfling', 'type': 'DEX', 'mod': 2}, {'origin': 'Halfling', 'type': 'CHA', 'mod': 2}],   
     'skill_mods': [{'origin': 'Halfling', 'type': 'Acrobatics', 'mod': 2}, {'origin': 'Halfling', 'type': 'Thievery', 'mod': 2}], 
     'defense_mods': [],            
     'size': 'Small',
     'speed': 6,
     'min_height': 46,
     'max_height': 50,
     'min_weight': 75,
     'max_weight': 85},
    {'name': 'Human',
     'motto': 'Ambitious, driven, pragmatic - a race of heroes, and also a race of villians.',
     'ability_bonuses': [{'origin': 'Human', 'type': 'CON', 'mod': 2}, {'origin': 'Human', 'type': 'INT', 'mod': 2}],
     'skill_mods': [],  
     'defense_mods': [{'origin': 'Human', 'type': 'FORT', 'mod': 1}, {'origin': 'Human', 'type': 'REF', 'mod': 1}, {'origin': 'Human', 'type': 'WILL', 'mod': 1}],           
     'size': 'Medium',
     'speed': 6,
     'min_height': 66,
     'max_height': 74,
     'min_weight': 135,
     'max_weight' : 220}]
     
CAST_DATA = [
    {'name': 'Cleric',
     'motto': 'Have courage, my friends!  Pelor favors us today!',
     'hit_point_base': 12,
     'hit_point_level': 5,
     'surge_recharge': 12342,
     'base_skill': 'Religion',
     'skills': ['Arcana', 'Diplomacy', 'Heal', 'History', 'Insight'],
     'ability_mods': [],      
     'skill_mods': [],      
     'defense_mods': [{'origin': 'Cleric', 'type': 'WILL', 'mod': 2}],
     'armor_profs': ['Cloth', 'Leather', 'Hide', 'Chainmail'] },     
    {'name': 'Ranger',
     'motto': 'I\'ll get the one in the back.  That\'s one hobgoblin who\'ll regret lifting a bow.',
     'hit_point_base': 12,
     'hit_point_level': 5,
     'surge_recharge': 14400,     
     'base_skill': 'Nature',
     'skills': ['Acrobatics', 'Athletics', 'Dungeoneering', 'Endurance', 'Heal', 'Perception', 'Stealth'],
     'ability_mods': [],      
     'skill_mods': [],     
     'defense_mods': [{'origin': 'Ranger', 'type': 'FORT', 'mod': 1}, {'origin': 'Ranger', 'type': 'REF', 'mod': 1}],     
     'armor_profs': ['Cloth', 'Leather', 'Hide'] },
    {'name': 'Rogue',
     'motto': 'You look surprised to see me.  If you\'d been paying attention, you might still be alive.',
     'hit_point_base': 12,
     'hit_point_level': 5,
     'surge_recharge': 14400,     
     'base_skill': 'Stealth',
     'skills': ['Acrobatics', 'Athletics', 'Bluff', 'Dungeoneering', 'Insight', 'Intimidate', 'Perception', 'Streetwise', 'Thievery'],
     'ability_mods': [],      
     'skill_mods': [],     
     'defense_mods': [{'origin': 'Rogue', 'type': 'REF', 'mod': 2}],     
     'armor_profs': ['Cloth', 'Leather'] },
    {'name': 'Wizard',
     'motto': 'I am the fire that burns, the choking fog, the storm that rains devastation on our foes.',
     'hit_point_base': 10,
     'hit_point_level': 4,
     'surge_recharge': 14400,          
     'base_skill': 'Arcana',
     'skills': ['Diplomacy', 'Dungeoneering', 'History', 'Insight', 'Nature', 'Religion'],
     'ability_mods': [],      
     'skill_mods': [],     
     'defense_mods': [{'origin': 'Wizard', 'type': 'WILL', 'mod': 2}],  
     'armor_profs': ['Cloth'] },
    {'name': 'Fighter',
     'motto': 'You\'ll have to deal with me first, dragon!',
     'hit_point_base': 15,
     'hit_point_level': 6,
     'surge_recharge': 9600,
     'base_skill': 'Athletics',
     'skills': ['Endurance', 'Heal', 'Intimidate', 'Streetwise'],
     'ability_mods': [],      
     'skill_mods': [],     
     'defense_mods': [{'origin': 'Fighter', 'type': 'FORT', 'mod': 2}],  
     'armor_profs': ['Cloth', 'Leather', 'Hide', 'Chainmail', 'Scale', 'Light Shield', 'Heavy Shield'] },
    {'name': 'Barbarian',
     'motto': 'My strength is the fury of the wild.',
     'hit_point_base': 15,
     'hit_point_level': 6,
     'surge_recharge': 10800,     
     'base_skill': 'Endurance',
     'skills': ['Acrobatics', 'Athletics', 'Heal', 'Intimidate', 'Nature', 'Perception'],
     'ability_mods': [],      
     'skill_mods': [],     
     'defense_mods': [{'origin': 'Barbarian', 'type': 'FORT', 'mod': 2}],
     'armor_profs': ['Cloth', 'Leather', 'Hide'] }]     

WEAPON_DATA = [
    {'name': 'Dagger',
     'level': 1,
     'slot': 'One-hand',
     'cost': 1,
     'weight': 3,
     'magic': False,
     'category': 'Simple Melee',
     'power': None,
     'damage_die': 4,
     'dice': 1,
     'group': 'Light Blade',
     'attributes': ['Off-hand', 'Light Thrown'],
     'casts': ['Barbarian', 'Cleric', 'Fighter', 'Ranger', 'Roque', 'Wizard'],
     'short_range': 5,
     'long_range': 10,
     'prof': 3},
    {'name': 'Mace',
     'level': 1,
     'slot': 'One-hand',
     'cost': 5,
     'weight': 6,
     'magic': False,
     'category': 'Simple Melee',
     'power': None,
     'damage_die': 8,
     'dice': 1,
     'group': 'Mace',
     'attributes': ['Versatile'],
     'casts': ['Barbarian', 'Cleric', 'Fighter', 'Ranger'],
     'short_range': 0,
     'long_range': 0,
     'prof': 2},     
    {'name': 'Spear',
     'level': 1,
     'slot': 'One-hand',
     'cost': 5,
     'weight': 6,
     'magic': False,
     'category': 'Simple Melee',
     'power': None,
     'damage_die': 8,
     'dice': 1,
     'group': 'Spear',
     'attributes': ['Versatile'],
     'casts': ['Barbarian', 'Cleric', 'Fighter', 'Ranger'],     
     'short_range': 0,
     'long_range': 0,
     'prof': 2},  
    {'name': 'Morningstar',
     'level': 1,
     'slot': 'Two-hand',
     'cost': 10,
     'weight': 8,
     'magic': False,
     'category': 'Simple Melee',
     'power': None,
     'damage_die': 4,
     'dice': 2,
     'group': 'Mace',
     'attributes': [],
     'casts': ['Barbarian', 'Cleric', 'Fighter', 'Ranger'],     
     'short_range': 0,
     'long_range': 0,
     'prof': 2},     
    {'name': 'Quarterstaff',
     'level': 1,
     'slot': 'Two-hand',
     'cost': 5,
     'weight': 4,
     'magic': False,
     'category': 'Simple Melee',
     'power': None,
     'damage_die': 8,
     'dice': 1,
     'group': 'Staff',
     'attributes': [],
     'casts': ['Barbarian', 'Cleric', 'Fighter', 'Ranger', 'Wizard'],     
     'short_range': 0,
     'long_range': 0,
     'prof': 2},  
    {'name': 'Battleaxe',
     'level': 1,
     'slot': 'One-hand',
     'cost': 15,
     'weight': 6,
     'magic': False,
     'category': 'Military Melee',
     'power': None,
     'damage_die': 10,
     'dice': 1,
     'group': 'Axe',
     'attributes': ['Versatile'],
     'casts': ['Barbarian', 'Fighter', 'Ranger'],     
     'short_range': 0,
     'long_range': 0,
     'prof': 2},     
    {'name': 'Longsword',
     'level': 1,
     'slot': 'One-hand',
     'cost': 15,
     'weight': 4,
     'magic': False,
     'category': 'Military Melee',
     'power': None,
     'damage_die': 8,
     'dice': 1,
     'group': 'Heavy Blade',
     'attributes': ['Versatile'],
     'casts': ['Barbarian', 'Fighter', 'Ranger'],     
     'short_range': 0,
     'long_range': 0,
     'prof': 3},
    {'name': 'Shortsword',
     'level': 1,
     'slot': 'One-hand',
     'cost': 10,
     'weight': 2,
     'magic': False,
     'category': 'Military Melee',
     'power': None,
     'damage_die': 6,
     'dice': 1,
     'group': 'Light Blade',
     'attributes': ['Off-hand'],
     'casts': ['Barbarian', 'Fighter', 'Ranger', 'Rogue'],     
     'short_range': 0,
     'long_range': 0,
     'prof': 3},
    {'name': 'Warhammer',
     'level': 1,
     'slot': 'One-hand',
     'cost': 15,
     'weight': 5,
     'magic': False,
     'category': 'Military Melee',
     'power': None,
     'damage_die': 10,
     'dice': 1,
     'group': 'Hammer',
     'attributes': ['Versatile'],
     'casts': ['Barbarian', 'Fighter', 'Ranger'],     
     'short_range': 0,
     'long_range': 0,
     'prof': 2},
    {'name': 'Greataxe',
     'level': 1,
     'slot': 'Two-hand',
     'cost': 30,
     'weight': 12,
     'magic': False,
     'category': 'Military Melee',
     'power': None,
     'damage_die': 12,
     'dice': 1,
     'group': 'Axe',
     'attributes': ['High Critical'],
     'casts': ['Barbarian', 'Fighter', 'Ranger'],     
     'short_range': 0,
     'long_range': 0,
     'prof': 2},     
    {'name': 'Greatsword',
     'level': 1,
     'slot': 'Two-hand',
     'cost': 30,
     'weight': 8,
     'magic': False,
     'category': 'Military Melee',
     'power': None,
     'damage_die': 10,
     'dice': 1,
     'group': 'Heavy Blade',
     'attributes': [],
     'casts': ['Barbarian', 'Fighter', 'Ranger'],     
     'short_range': 0,
     'long_range': 0,
     'prof': 3},         
    {'name': 'Hand Crossbow',
     'level': 1,
     'slot': 'One-hand',
     'cost': 25,
     'weight': 2,
     'magic': False,
     'category': 'Simple Ranged',
     'power': None,
     'damage_die': 6,
     'dice': 1,
     'group': 'Crossbow',
     'attributes': ['Load Free'],
     'casts': ['Cleric', 'Fighter', 'Ranger', 'Rogue'],     
     'short_range': 10,
     'long_range': 20,
     'prof': 2},
    {'name': 'Sling',
     'level': 1,
     'slot': 'One-hand',
     'cost': 1,
     'weight': 0,
     'magic': False,
     'category': 'Simple Ranged',
     'power': None,
     'damage_die': 6,
     'dice': 1,
     'group': 'Sling',
     'attributes': ['Load Free'],
     'casts': ['Cleric', 'Fighter', 'Ranger', 'Rogue'],     
     'short_range': 10,
     'long_range': 20,
     'prof': 2},
    {'name': 'Crossbow',
     'level': 1,
     'slot': 'Two-hand',
     'cost': 25,
     'weight': 4,
     'magic': False,
     'category': 'Simple Ranged',
     'power': None,
     'damage_die': 8,
     'dice': 1,
     'group': 'Crossbow',
     'attributes': ['Load Minor'],
     'casts': ['Fighter', 'Ranger'],     
     'short_range': 10,
     'long_range': 20,
     'prof': 2},
    {'name': 'Longbow',
     'level': 1,
     'slot': 'Two-hand',
     'cost': 30,
     'weight': 3,
     'magic': False,
     'category': 'Military Ranged',
     'power': None,
     'damage_die': 10,
     'dice': 1,
     'group': 'Bow',
     'attributes': ['Load Free'],
     'casts': ['Fighter', 'Ranger'],     
     'short_range': 20,
     'long_range': 40,
     'prof': 2},
    {'name': 'Shortbow',
     'level': 1,
     'slot': 'Two-hand',
     'cost': 25,
     'weight': 2,
     'magic': False,
     'category': 'Military Ranged',
     'power': None,
     'damage_die': 8,
     'dice': 1,
     'group': 'Bow',
     'attributes': ['Load Free'],
     'casts': ['Fighter', 'Ranger'],     
     'short_range': 15,
     'long_range': 30,
     'prof': 2}]

ATTACK_DATA = [
    {'name': 'Lance of Faith',
     'casts': ['Cleric'],
     'level': 1,
     'description': 'A brilliant ray of light sears your foe with golden radiance.',
     'recharge': 10,
     'source_keyword': 'Divine',
     'accessory_keyword': 'Implement',
     'damage_keywords': ['Radiant'],
     'effect_keyword': None,
     'attack_range': 5,
     'max_targets': 1,
     'max_attacks': 1,
     'attack_ability': 'WIS',
     'attack_mod': 0,
     'defense_ability': 'REF',
     'damage_die': 8,
     'damage_dice': 1,
     'damage_weapon_multiplier': None,     
     'damage_ability_mod': 'WIS'},
    {'name': 'Priest\'s Shield',
     'casts': ['Cleric'],
     'level': 1,      
     'description': 'You utter a minor defensive prayer as you attack with your weapon.',      
     'recharge': 10,
     'source_keyword': 'Divine',
     'accessory_keyword': 'Weapon',
     'damage_keywords': [],
     'effect_keyword': None,      
     'attack_range': 0,
     'max_targets': 1,
     'max_attacks': 1,
     'attack_ability': 'STR',
     'attack_mod': 0,
     'defense_ability': 'AC',
     'damage_die': None,
     'damage_dice': None,
     'damage_weapon_multiplier': 1,
     'damage_ability_mod': 'STR'},
    {'name': 'Divine Glow',
     'casts': ['Cleric'],
     'level': 1,      
     'description': 'Murmuring a prayer to your diety, you invoke a blast of white radiance from you holy symbol.  Foes burn in its stern light.',      
     'recharge': 3600,
     'source_keyword': 'Divine',
     'accessory_keyword': 'Implement',
     'damage_keywords': ['Radiant'],
     'effect_keyword': None,      
     'attack_range': 5,
     'max_targets': 3,
     'max_attacks': 1,
     'attack_ability': 'WIS',
     'attack_mod': 0,
     'defense_ability': 'REF',
     'damage_die': 8,
     'damage_dice': 1,
     'damage_weapon_multiplier': None,     
     'damage_ability_mod': 'WIS'},
    {'name': 'Howling Strike',
     'casts': ['Barbarian'],
     'level': 1,      
     'description': 'With a blood-freezing scream, you throw yourelf into the fray.',      
     'recharge': 10,
     'source_keyword': 'Primal',
     'accessory_keyword': 'Weapon',
     'damage_keywords': [],    
     'effect_keyword': None,
     'attack_range': 0,
     'max_targets': 1,
     'max_attacks': 1,
     'attack_ability': 'STR',
     'attack_mod': 0,
     'defense_ability': 'AC',
     'damage_weapon_multiplier': 1,
     'damage_die': 6,
     'damage_dice': 1,     
     'damage_weapon_multiplier': None,      
     'damage_ability_mod': 'STR'},
    {'name': 'Vault the Fallen',
     'casts': ['Barbarian'],
     'level': 1,      
     'description': 'You leap from one foe to the next, leaving blood in your wake.',      
     'recharge': 3600,
     'source_keyword': 'Primal',
     'accessory_keyword': 'Weapon',
     'damage_keywords': [],    
     'effect_keyword': None,      
     'attack_range': 0,
     'max_targets': 2,
     'max_attacks': 1,
     'attack_ability': 'STR',
     'attack_mod': 0,
     'defense_ability': 'AC',
     'damage_weapon_multiplier': 1,
     'damage_die': 6,
     'damage_dice': 1, 
     'damage_weapon_multiplier': None,          
     'damage_ability_mod': 'STR'},
    {'name': 'Macetail\'s Rage',
     'casts': ['Barbarian'],
     'level': 1,      
     'description': 'You knock your enemy to the ground with a slam like the behemoth\'s heavy tail, and the rage of the macetail fills you, refreshing you with every blow of your weapon.',      
     'recharge': 86400,
     'source_keyword': 'Primal',
     'accessory_keyword': 'Weapon',
     'damage_keywords': [],    
     'effect_keyword': 'Rage',
     'attack_range': 0,
     'max_targets': 3,
     'max_attacks': 1,
     'attack_ability': 'STR',
     'attack_mod': 0,
     'defense_ability': 'REF',
     'damage_die': None,
     'damage_dice': None,     
     'damage_weapon_multiplier': 1,
     'damage_ability_mod': 'STR'},      
    {'name': 'Cleave',
     'casts': ['Fighter'],
     'level': 1,      
     'description': 'You hit one enemy, then cleave into another.',      
     'recharge': 10,
     'source_keyword': 'Martial',
     'accessory_keyword': 'Weapon',
     'damage_keywords': [],    
     'effect_keyword': None,
     'attack_range': 0,
     'max_targets': 2,
     'max_attacks': 1,
     'attack_ability': 'STR',
     'attack_mod': 0,
     'defense_ability': 'AC',
     'damage_die': None,
     'damage_dice': None,     
     'damage_weapon_multiplier': 1,
     'damage_ability_mod': 'STR'},
    {'name': 'Steel Serpent Strike',
     'casts': ['Fighter'],
     'level': 1,      
     'description': 'You stab viciously at your foe\'s knee of foot.  No matter how tough your foe is, they will favor that leg for some time.',      
     'recharge': 3600,
     'source_keyword': 'Martial',
     'accessory_keyword': 'Weapon',
     'damage_keywords': [],     
     'effect_keyword': None,
     'attack_range': 0,
     'max_targets': 1,
     'max_attacks': 1,
     'attack_ability': 'STR',
     'attack_mod': 0,
     'defense_ability': 'AC',
     'damage_die': None,
     'damage_dice': None,     
     'damage_weapon_multiplier': 2,
     'damage_ability_mod': 'STR'},
    {'name': 'Brute Strike',
     'casts': ['Fighter'],
     'level': 1,      
     'description': 'You shatter armor and bone with a ringing blow.',      
     'recharge': 86400,
     'source_keyword': 'Martial',
     'accessory_keyword': 'Weapon',
     'damage_keywords': [],
     'effect_keyword': 'Reliable',
     'attack_range': 0,
     'max_targets': 1,
     'max_attacks': 1,
     'attack_ability': 'STR',
     'attack_mod': 0,
     'defense_ability': 'AC',
     'damage_die': None,
     'damage_dice': None,     
     'damage_weapon_multiplier': 3,
     'damage_ability_mod': 'STR'},      
    {'name': 'Twin Strike',
     'casts': ['Ranger'],
     'level': 1,      
     'description': 'If the first attack doesn\'t kill it, the second one might.',      
     'recharge': 10,
     'source_keyword': 'Martial',
     'accessory_keyword': 'Weapon',
     'damage_keywords': [],     
     'effect_keyword': None,      
     'attack_range': 30,
     'max_targets': 1,
     'max_attacks': 2,
     'attack_ability': 'DEX',
     'attack_mod': 0,
     'defense_ability': 'AC',
     'damage_die': None,
     'damage_dice': None,     
     'damage_weapon_multiplier': 1,
     'damage_ability_mod': None},
    {'name': 'Dire Wolverine Strike',
     'casts': ['Ranger'],
     'level': 1,      
     'description': 'Enemies surround you -- much to their chagrin, as you slash them to pieces with the ferocity of a wounded dire wolverine.',      
     'recharge': 3600,
     'source_keyword': 'Martial',
     'accessory_keyword': 'Weapon',
     'damage_keywords': [],     
     'effect_keyword': None,      
     'attack_range': 0,
     'max_targets': 3,
     'max_attacks': 1,
     'attack_ability': 'STR',
     'attack_mod': 0,
     'defense_ability': 'AC',
     'damage_die': None,
     'damage_dice': None,     
     'damage_weapon_multiplier': 1,
     'damage_ability_mod': None},
    {'name': 'Hunter\'s Bear Trap',
     'casts': ['Ranger'],
     'level': 1,      
     'description': 'A well-placed shot to the leg leaves your enemy hobbled and bleeding.',      
     'recharge': 86400,
     'source_keyword': 'Martial',
     'accessory_keyword': 'Weapon',
     'damage_keywords': [],     
     'effect_keyword': None,
     'attack_range': 30,
     'max_targets': 1,
     'max_attacks': 1,
     'attack_ability': 'DEX',
     'attack_mod': 0,
     'defense_ability': 'AC',
     'damage_die': None,
     'damage_dice': None,     
     'damage_weapon_multiplier': 2,
     'damage_ability_mod': 'DEX'},
    {'name': 'Deft Strike',
     'casts': ['Rogue'],
     'level': 1,      
     'description': 'A final lunge brings you into an advantageous position.',      
     'recharge': 30,
     'source_keyword': 'Martial',
     'accessory_keyword': 'Weapon',
     'damage_keywords': [],     
     'effect_keyword': None,
     'attack_range': 0,
     'max_targets': 1,
     'max_attacks': 1,
     'attack_ability': 'DEX',
     'attack_mod': 0,
     'defense_ability': 'AC',
     'damage_die': None,
     'damage_dice': None,     
     'damage_weapon_multiplier': 1,
     'damage_ability_mod': 'DEX'},
    {'name': 'Torturous Strike',
     'casts': ['Rogue'],
     'level': 1,      
     'description': 'If you twist the blade in the wound just so, you can make your enemy howl in pain.',      
     'recharge': 3600,
     'source_keyword': 'Martial',
     'accessory_keyword': 'Weapon',
     'damage_keywords': [],     
     'effect_keyword': None,      
     'attack_range': 0,
     'max_targets': 1,
     'max_attacks': 1,
     'attack_ability': 'DEX',
     'attack_mod': 0,
     'defense_ability': 'AC',
     'damage_die': None,
     'damage_dice': None,     
     'damage_weapon_multiplier': 2,
     'damage_ability_mod': 'DEX'},  
    {'name': 'Trick Strike',
     'casts': ['Rogue'],
     'level': 1,      
     'description': 'Through a series of feints and lures, you maneuver your foe right where you want him.',      
     'recharge': 86400,
     'source_keyword': 'Martial',
     'accessory_keyword': 'Weapon',
     'damage_keywords': [],     
     'effect_keyword': None,      
     'attack_range': 0,
     'max_targets': 1,
     'max_attacks': 1,
     'attack_ability': 'DEX',
     'attack_mod': 0,
     'defense_ability': 'AC',
     'damage_die': None,
     'damage_dice': None,     
     'damage_weapon_multiplier': 3,
     'damage_ability_mod': 'DEX'},
    {'name': 'Magic Missile',
     'casts': ['Wizard'],
     'level': 1,      
     'description': 'You launch a silvery bolt of force at an enemy.',      
     'recharge': 30,
     'source_keyword': 'Arcane',
     'accessory_keyword': 'Implement',
     'damage_keywords': ['Force'],
     'effect_keyword': None,
     'attack_range': 30,
     'max_targets': 1,
     'max_attacks': 1,
     'attack_ability': 'INT',
     'attack_mod': 0,
     'defense_ability': 'REF',
     'damage_die': 4,
     'damage_dice': 2,
     'damage_weapon_multiplier': None,     
     'damage_ability_mod': 'INT'},
    {'name': 'Burning Hands',
     'casts': ['Wizard'],
     'level': 1,      
     'description': 'A fierce burst of flame erupts from your hands and scorches nearby foes.',      
     'recharge': 3600,
     'source_keyword': 'Arcane',
     'accessory_keyword': 'Implement',
     'damage_keywords': ['Fire'],
     'effect_keyword': None,
     'attack_range': 0,
     'max_targets': 5,
     'max_attacks': 1,
     'attack_ability': 'INT',
     'attack_mod': 0,
     'defense_ability': 'REF',
     'damage_die': 6,
     'damage_dice': 2,
     'damage_weapon_multiplier': None,     
     'damage_ability_mod': 'INT'},
    {'name': 'Acid Arrow',
     'casts': ['Wizard'],
     'level': 1,      
     'description': 'A shimmering arrow of green, glowing liquid streaks to your target and bursts in a spray of sizzling acid.',      
     'recharge': 86400,
     'source_keyword': 'Arcane',
     'accessory_keyword': 'Implement',
     'damage_keywords': ['Acid'],
     'effect_keyword': None,
     'attack_range': 30,
     'max_targets': 4,
     'max_attacks': 1,
     'attack_ability': 'INT',
     'attack_mod': 0,
     'defense_ability': 'REF',
     'damage_die': 8,
     'damage_dice': 2,
     'damage_weapon_multiplier': None,     
     'damage_ability_mod': 'INT'}]
     
######################## METHODS #############################################
##############################################################################
def seedRaces():
    """Primes the datastore with Race data.
    """
    logging.info('###################### seedRaces() #######################')
    races = []
    for x in RACE_DATA:
        logging.info('################## x = '+str(x)+' ####################')
        abilities = []
        skills = []
        defenses = []
        for a in x['ability_bonuses']:
            abilities.append(a)
        for a in x['skill_mods']:
            skills.append(a)            
        for a in x['defense_mods']:
            defenses.append(a)            
        mods = {
                models.SKILLS_KEY: skills,
                models.DEFENSES_KEY: defenses}
        bonuses = {models.ABILITIES_KEY: abilities}  
                             
        race = models.Race(key_name = x['name'],
                           name = x['name'],
                           motto = x['motto'],
                           size = x['size'],
                           speed = x['speed'],
                           min_height = x['min_height'],
                           max_height = x['max_height'],
                           min_weight = x['min_weight'],                           
                           max_weight = x['max_weight'],
                           mods = mods,
                           bonuses = bonuses)
        races.append(race)
    
    db.put(races)                         
    return
    
def seedCasts():
    """Primes the datastore with Race data.
    """
    logging.info('###################### seedCasts() #######################')
    casts = []
    for x in CAST_DATA:
        logging.info('################## x = '+str(x)+' ####################')
        skills = []
        abilities = []
        trainable_skills = []
        defenses = []
        armor_profs = []
        for a in x['ability_mods']:
            abilities.append(a)
        for a in x['skill_mods']:
            skills.append(a)            
        for a in x['defense_mods']:
            defenses.append(a)  
        mods = {models.ABILITIES_KEY: abilities,
                models.SKILLS_KEY: skills,
                models.DEFENSES_KEY: defenses}
        for a in x['skills']:
            trainable_skills.append(a)           
        for a in x['armor_profs']:
            armor_profs.append(a)           
 
        cast = models.Cast(key_name = x['name'],
                           name = x['name'],
                           motto = x['motto'],
                           hit_point_base = x['hit_point_base'],
                           hit_point_level = x['hit_point_level'],
                           surge_recharge = x['surge_recharge'],
                           base_skill = x['base_skill'],
                           skills = trainable_skills,
                           mods = mods,
                           armor_proficiencies = armor_profs)
        casts.append(cast)
    
    db.put(casts)                         
    return
    
def seedNPCs():
    """Primes the datastore with Monsters.  Rawwwr!!
    """
    logging.info('###################### seedWeapons() #####################')    
    npcs = []
    for x in monster.MONSTER_DATA:
        logging.info('################## x = '+str(x)+' ####################') 
        languages = []
        keywords = []
        items = []
        artifacts = []
        immunities = []
        for a in x['languages']:
            languages.append(a)
        for a in x['keywords']:
            keywords.append(a)    
        for i in x['immunities']:
            immunities.append(i)
        
        npc = models.NonPlayerCharacter(name = x['name'],
                                        level = x['level'],
                                        race = x['race'],
                                        alignment = x['alignment'],
                                        size = x['size'],
                                        experience = x['experience'],
                                        speed = x['speed'],
                                        items = items,
                                        actions = x['actions'],
                                        hit_points = x['hit_points'],
                                        scores = x['scores'],
                                        description = x['description'],
                                        origin = x['origin'],
                                        category = x['category'],
                                        languages = languages,
                                        keywords = keywords,
                                        artifacts = artifacts,
                                        role = x['role'],
                                        challenge = x['challenge'],
                                        resist = x['resist'],
                                        vulnerable = x['vulnerable'],
                                        immunities = immunities)
        
        npcs.append(npc)
    db.put(npcs)
    return                                    
    
def seedWeapons():
    """Primes the datastore with Weapons data.
    """
    logging.info(TRACE+'seedWeapons()')
    weapons = []
    for x in WEAPON_DATA:
        logging.info(TRACE+'seedWeapons():: x = '+str(x))        
        casts = []
        attributes = []
        for a in x['casts']:
            casts.append(a)
        for a in x['attributes']:
            attributes.append(a)  
        
        weapon = models.Weapon(key_name = x['name'],
                               name = x['name'],
                               level = x['level'],
                               slot = x['slot'],
                               cost = x['cost'],
                               weight = x['weight'],
                               magic = x['magic'],
                               power = x['power'],
                               damage_die = x['damage_die'],
                               damage_dice = x['dice'],
                               group = x['group'],
                               attributes = attributes,
                               casts = casts,
                               short_range = x['short_range'],
                               long_range = x['long_range'],
                               proficiency = x['prof'])          
        
        weapon.json = getJSONItem(models.WPN, weapon)
        weapons.append(weapon)
    
    db.put(weapons)    
    return    

def seedAttacks():
    """Primes the datastore with Attacks data.
    """
    logging.info(TRACE+'seedAttacks()')
    attacks = []   
         
    for x in ATTACK_DATA:    
        logging.info(TRACE+'seedAttacks():: x = '+str(x))
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
                               effect_keyword = x['effect_keyword'],
                               casts = casts,
                               attack_range = x['attack_range'],
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

def seedPlayerParty():
    """Primes the datastore with a PlayerParty.
    """
    logging.info(TRACE+'seedPlayerParty()')   
    log = {'encounters': 
                {'total': 23, 'uniques': 2, 'start_time': time.time(),
                'last_encounter': {'time_since': time.time(), 'checks': 9}}
          } 
    leader = models.PlayerCharacter.get_by_id(32)    
    members = [leader.key()]  
    location = db.GeoPt(001, 001)
    player_party = models.PlayerParty(location = location,
                                      log = log,
                                      json = None,
                                      leader = leader,
                                      members = members)
    
    db.put(player_party)
    return                                      
    
def getJSONPower(model_name, model):
    json = {'name': model.name, 'description': model.description, 
            'recharge': model.recharge, 'level': model.level, 
            'source_keyword': model.source_keyword, 'casts': model.casts,
            'effect_keyword': model.effect_keyword}
    
    # Construct JSON specific to the subclass        
    if model_name == models.ATT:
        json['damage_keywords'] = model.damage_keywords
        json['accessory_keyword'] = model.accessory_keyword
        json['attack_range'] = model.attack_range
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
                   
def getJSONItem(model_name, model):
    json = {'name': model.name, 'description': model.description, 
            'level': model.level, 'slot': model.slot, 'cost': model.cost,
            'casts': model.casts, 'weight': model.weight, 
            'magic': model.magic}
    if model.power is not None:
        json['power'] = model.power.name        

    # Construct JSON specific to the subclass             
    if model_name == models.WPN:
        json['damage_die'] = model.damage_die
        json['damage_dice'] = model.damage_dice
        json['group'] = model.group
        json['attributes'] = model.attributes
        json['short_range'] = model.short_range
        json['long_range'] = model.long_range
        json['proficiency'] = model.proficiency
        
    elif model_name == models.ARM:
        json['armor_mod'] = model.armor_mod
        json['check_mod'] = model.check_mod
        json['speed_mod'] = model.speed_mod
                            
    elif model_name == models.IMP:
        json['category'] = model.category
    
    elif model_name == models.GEA:  
        json['foo'] = model.foo
        
    return json    
                         