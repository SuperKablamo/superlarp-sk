#
# Copyright 2010 SuperKablamo, LLC
# info@superkablamo.com
#

############################# SK IMPORTS #####################################
############################################################################## 
import models
import rules
import seed

from settings import *

############################# GAE IMPORTS ####################################
##############################################################################
import os
import logging
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
    {'name': 'Long Sword',
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
    {'name': 'Short Sword',
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
     
NPC_DATA = [
    {'name': 'Kobold Minion',
     'level': 1,
     'race': 'Kobold',
     'alignment': 'Evil',
     'size': 'Small',
     'experience': 25,
     'speed': 6,
     'items': [],
     'actions': {'weapons': [{
                    'name': 'Javelin',
                    'attack_mod': 5,
                    'defense_ability': 'AC',
                    'damage_dice': 1,
                    'damage_die': 4,
                    'damage_mod': 0,
                    'damage_keywords': [],
                    'category': 'Simple Melee',
                    'short_range': 0,
                    'long_range': 0,
                    'magic': False
                    }],
                'powers': [],
                'heal': []
                },
     'hit_points': {'hp': 1},
     'scores': {'abilities': {
                    'STR': {'score': 8, 'mod': -1}, 
                    'CON': {'score': 12, 'mod': 1}, 
                    'DEX': {'score': 16, 'mod': 3}, 
                    'INT': {'score': 9, 'mod': -1}, 
                    'WIS': {'score': 12, 'mod': 1}, 
                    'CHA': {'score': 10, 'mod': 0}},
                'defenses': {
                    'AC': {'score': 15},
                    'FORT': {'score': 11},
                    'REF': {'score': 13},
                    'WILL': {'score': 11}}
                },      
     'description': 'Kobolds are short, reptilian humanoids with cowardly and sadistic tendencies.  A kobold\'s scaly skin ranges from dark rusty brown to a rusty black color. It has glowing red eyes. Its tail is nonprehensile. Kobolds wear ragged clothing, favoring red and orange. A kobold is 2 to 2.5 feet tall and weighs 35 to 45 pounds. Kobolds speak Draconic with a voice that sounds like that of a yapping dog.',             
     'origin': 'Natural',
     'category': 'Humanoid',
     'languages': ['Common', 'Draconic'],
     'keywords': []},
    {'name': 'Kobold Skirmisher',
     'level': 1,
     'race': 'Kobold',
     'alignment': 'Evil',
     'size': 'Small',
     'experience': 100,
     'speed': 6,
     'actions': {'weapons': [{
                    'name': 'Spear',
                    'attack_mod': 6,
                    'defense_ability': 'AC',
                    'damage_dice': 1,
                    'damage_die': 8,
                    'damage_mod': 0,
                    'damage_keywords': [],
                    'category': 'Simple Melee',
                    'short_range': 0,
                    'long_range': 0,
                    'magic': False
                    }],
                'powers': [],
                'heal': []
                },     
     'hit_points': {'hp': 27},
     'scores': {'abilities': {
                    'STR': {'score': 8, 'mod': -1}, 
                    'CON': {'score': 11, 'mod': 0}, 
                    'DEX': {'score': 16, 'mod': 3}, 
                    'INT': {'score': 6, 'mod': -2}, 
                    'WIS': {'score': 10, 'mod': 0}, 
                    'CHA': {'score': 15, 'mod': 2}
                    },
                'defenses': {
                    'AC': {'score': 15},
                    'FORT': {'score': 11},
                    'REF': {'score': 14},
                    'WILL': {'score': 13}
                    }
                },   
     'description': 'Kobolds are short, reptilian humanoids with cowardly and sadistic tendencies.  A kobold\'s scaly skin ranges from dark rusty brown to a rusty black color. It has glowing red eyes. Its tail is nonprehensile. Kobolds wear ragged clothing, favoring red and orange. A kobold is 2 to 2.5 feet tall and weighs 35 to 45 pounds. Kobolds speak Draconic with a voice that sounds like that of a yapping dog.',             
     'origin': 'Natural',
     'category': 'Humanoid',
     'languages': ['Common', 'Draconic'],
     'keywords': []},
    {'name': 'Bugbear Warrior',
     'level': 5,
     'race': 'Goblin',
     'alignment': 'Evil',
     'size': 'Medium',
     'experience': 200,
     'speed': 6,
     'actions': {'weapons': [{
                    'name': 'Morningstar',
                    'attack_mod': 7,
                    'defense_ability': 'AC',
                    'damage_dice': 1,
                    'damage_die': 12,
                    'damage_mod': 6,
                    'damage_keywords': [],
                    'category': 'Simple Melee',
                    'short_range': 0,
                    'long_range': 0,
                    'magic': False
                    }],
                'powers': [{
                    'name': 'Skullthumper',
                    'recharge': 3600,
                    'source_keyword': 'Martial',
                    'accessory_keyword': 'Weapon',
                    'damage_keywords': [],     
                    'effect_keyword': None,
                    'attack_range': 0,
                    'max_targets': 1,
                    'max_attacks': 1,
                    'attack_mod': 5,
                    'defense_ability': 'FORT',
                    'damage_dice': 1,  
                    'damage_die': 12,   
                    'damage_mod': 6
                    }],
                'heal': []
                },
     'hit_points': {'hp': 76},
     'scores': {'abilities': {
                    'STR': {'score': 20, 'mod': 7}, 
                    'CON': {'score': 16, 'mod': 5}, 
                    'DEX': {'score': 16, 'mod': 5}, 
                    'INT': {'score': 10, 'mod': 2}, 
                    'WIS': {'score': 14, 'mod': 4}, 
                    'CHA': {'score': 10, 'mod': 2}
                    },
                'defenses': {
                    'AC': {'score': 18},
                    'FORT': {'score': 17},
                    'REF': {'score': 15},
                    'WILL': {'score': 14}
                    }
                },   
     'description': 'Bugbears are big, tough Goblins.',             
     'origin': 'Natural',
     'category': 'Humanoid',
     'languages': ['Common', 'Goblin'],
     'keywords': []},
    {'name': 'Goblin Minion',
     'level': 1,
     'race': 'Goblin',
     'alignment': 'Evil',
     'size': 'Small',
     'experience': 25,
     'speed': 6,
     'actions': {'weapons': [{
                    'name': 'Short Sword',
                    'attack_mod': 5,
                    'defense_ability': 'AC',
                    'damage_dice': 1,
                    'damage_die': 4,
                    'damage_mod': 0,
                    'damage_keywords': [],
                    'category': 'Simple Melee',
                    'short_range': 0,
                    'long_range': 0,
                    'magic': False
                    }],
                'powers': [],
                'heal': []
                },
     'hit_points': {'hp': 1},
     'scores': {'abilities': {
                    'STR': {'score': 14, 'mod': 2}, 
                    'CON': {'score': 13, 'mod': 1}, 
                    'DEX': {'score': 17, 'mod': 3}, 
                    'INT': {'score': 8, 'mod': -1}, 
                    'WIS': {'score': 12, 'mod': 1}, 
                    'CHA': {'score': 8, 'mod': -1}
                    },
                'defenses': {
                    'AC': {'score': 16},
                    'FORT': {'score': 12},
                    'REF': {'score': 14},
                    'WILL': {'score': 11}
                    }
                },   
     'description': 'A goblin stands 3 to 3.5 feet tall and weigh 40 to 45 pounds. Its eyes are usually dull and glazed, varying in color from red to yellow. A goblin\'s skin color ranges from yellow through any shade of orange to a deep red; usually all members of a single tribe are about the same color. Goblins wear clothing of dark leather, tending toward drab, soiled-looking colors. Goblins speak Goblin; those with Intelligence scores of 12 or higher also speak Common.',             
     'origin': 'Natural',
     'category': 'Humanoid',
     'languages': ['Common', 'Goblin'],
     'keywords': []},
    {'name': 'Hill Giant',
     'level': 13,
     'race': 'Giant',
     'alignment': 'Chaotic Evil',
     'size': 'Large',
     'experience': 800,
     'speed': 8,
     'actions': {'weapons': [{
                    'name': 'Greatclub',
                    'attack_mod': 15,
                    'defense_ability': 'AC',
                    'damage_dice': 1,
                    'damage_die': 10,
                    'damage_mod': 5,
                    'damage_keywords': [],
                    'category': 'Simple Melee',
                    'short_range': 0,
                    'long_range': 0,
                    'magic': False},
                    {
                    'name': 'Rock',
                    'attack_mod': 15,
                    'defense_ability': 'AC',
                    'damage_dice': 2,
                    'damage_die': 6,
                    'damage_mod': 5,
                    'damage_keywords': [],
                    'category': 'Improvised Melee',
                    'short_range': 30,
                    'long_range': 60,
                    'magic': False
                    }],
                'powers': [{
                    'name': 'Sweeping Club',
                    'recharge': 3600,
                    'source_keyword': 'Martial',
                    'accessory_keyword': 'Weapon',
                    'damage_keywords': [],     
                    'effect_keyword': None,
                    'attack_range': 0,
                    'max_targets': 2,
                    'max_attacks': 1,
                    'attack_mod': 15,
                    'defense_ability': 'AC',
                    'damage_dice': 1,  
                    'damage_die': 10,   
                    'damage_mod': 5
                    }],
                'heal': []    
                },
     'hit_points': {'hp': 159},
     'scores': {'abilities': {
                    'STR': {'score': 21, 'mod': 11}, 
                    'CON': {'score': 19, 'mod': 10}, 
                    'DEX': {'score': 8, 'mod': 5}, 
                    'INT': {'score': 7, 'mod': 4}, 
                    'WIS': {'score': 12, 'mod': 7}, 
                    'CHA': {'score': 9, 'mod': 5}
                    },
                 'defenses': {
                    'AC': {'score': 25},
                    'FORT': {'score': 27},
                    'REF': {'score': 21},
                    'WILL': {'score': 23}
                    }
                 },   
     'description': 'Skin color among hill giants ranges from light tan to deep ruddy brown. Their hair is brown or black, with eyes the same color. Hill giants wear layers of crudely prepared hides with the fur left on. They seldom wash or repair their garments, preferring to simply add more hides as their old ones wear out. Adults are about 10.5 feet tall and weigh about 1,100 pounds. Hill giants can live to be 200 years old.',             
     'origin': 'Natural',
     'category': 'Humanoid',
     'languages': ['Giant'],     
     'keywords': ['Giant']},
    {'name': 'Skeleton Minion',
     'level': 1,
     'race': 'Skeleton',
     'alignment': 'Unaligned',
     'size': 'Medium',
     'experience': 25,
     'speed': 6,
     'actions': {'weapons': [{
                    'name': 'Longsword',
                    'attack_mod': 6,
                    'defense_ability': 'AC',
                    'damage_dice': 1,
                    'damage_die': 4,
                    'damage_mod': 0,
                    'damage_keywords': [],
                    'category': 'Military Melee',
                    'short_range': 0,
                    'long_range': 0,
                    'magic': False},
                    {
                    'name': 'Shortbow',
                    'attack_mod': 6,
                    'defense_ability': 'AC',
                    'damage_dice': 1,
                    'damage_die': 4,
                    'damage_mod': 0,
                    'damage_keywords': [],
                    'category': 'Military Ranged',
                    'short_range': 30,
                    'long_range': 60,
                    'magic': False}],
                 'powers': [],
                 'heal': []
                  },
      'hit_points': {'hp': 1},
      'scores': {'abilities': {
                    'STR': {'score': 15, 'mod': 2}, 
                    'CON': {'score': 13, 'mod': 1}, 
                    'DEX': {'score': 17, 'mod': 3}, 
                    'INT': {'score': 3, 'mod': -4}, 
                    'WIS': {'score': 14, 'mod': 2}, 
                    'CHA': {'score': 3, 'mod': -4}
                    },
                'defenses': {
                     'AC': {'score': 16},
                     'FORT': {'score': 13},
                     'REF': {'score': 14},
                     'WILL': {'score': 13}
                     }
                },   
      'description': 'Skeletons are the animated bones of the dead, mindless automatons that obey the orders of their evil masters.  A skeleton is seldom garbed in anything more than the rotting remnants of any clothing or armor it was wearing when slain.  A skeleton does only what it is ordered to do.  It can draw no conclusions of its own and takes no initiative.  Because of this limitation, its instructions must always be simple.  A skeleton attacks until destroyed.',             
      'origin': 'Natural',
      'category': 'Animate',
      'languages': [],     
      'keywords': ['Undead']},
     {'name': 'Adult Red Dragon',
      'level': 15,
      'race': 'Dragon',
      'alignment': 'Evil',
      'size': 'Large',
      'experience': 6000,
      'speed': 8,
      'actions': {'weapons': [{
                    'name': 'Bite',
                    'attack_mod': 22,
                    'defense_ability': 'AC',
                    'damage_dice': 5,
                    'damage_die': 6,
                    'damage_mod': 7,
                    'damage_keywords': ['Fire'],
                    'category': 'Unarmed Melee',
                    'short_range': 0,
                    'long_range': 0,
                    'magic': False},
                    {
                    'name': 'Claw',
                    'attack_mod': 22,
                    'defense_ability': 'AC',
                    'damage_dice': 2,
                    'damage_die': 8,
                    'damage_mod': 7,
                    'damage_keywords': ['Fire'],
                    'category': 'Unarmed Melee',
                    'short_range': 0,
                    'long_range': 0,
                    'magic': False}],
                'powers': [{
                    'name': 'Breath of Fire',
                    'recharge': 3600,
                    'source_keyword': 'Arcane',
                    'accessory_keyword': None,
                    'damage_keywords': ['Fire'],     
                    'effect_keyword': None,
                    'attack_range': 30,
                    'max_targets': 5,
                    'max_attacks': 1,
                    'attack_mod': 20,
                    'defense_ability': 'REF',
                    'damage_dice': 2,  
                    'damage_die': 12,   
                    'damage_mod': 6                   
                }],
                'heal': []
                },
       'hit_points': {'hp': 1},
       'scores': {'abilities': {
                     'STR': {'score': 15, 'mod': 2}, 
                     'CON': {'score': 13, 'mod': 1}, 
                     'DEX': {'score': 17, 'mod': 3}, 
                     'INT': {'score': 3, 'mod': -4}, 
                     'WIS': {'score': 14, 'mod': 2}, 
                     'CHA': {'score': 3, 'mod': -4}
                     },
                  'defenses': {
                     'AC': {'score': 16},
                     'FORT': {'score': 13},
                     'REF': {'score': 14},
                     'WILL': {'score': 13}
                     }
                  },   
       'description': 'The small scales of a wyrmling red dragon are a bright glossy scarlet, making the dragon easily spotted by predators and hunters, so it stays underground and does not venture outside until it is more able to take care of itself. Toward the end of young age, the scales turn a deeper red, and the glossy texture is replaced by a smooth, dull finish. As the dragon grows older, the scales become large, thick, and as strong as metal. The neck frill and wings are an ash blue or purple-gray toward the edges, becoming darker with age. The pupils of a red dragon fade as it ages; the oldest red dragons have eyes that resemble molten lava orbs.',             
       'origin': 'Natural',
       'category': 'Magical Beast',
       'languages': ['Common', 'Draconic'],     
       'keywords': ['Dragon']},       
    ]     
    
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
    for x in NPC_DATA:
        logging.info('################## x = '+str(x)+' ####################') 
        languages = []
        keywords = []
        items = []
        artifacts = []
        for a in x['languages']:
            languages.append(a)
        for a in x['keywords']:
            keywords.append(a)    
        
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
                                        artifacts = artifacts)
        
        npcs.append(npc)
    db.put(npcs)
    return                                    
    
def seedWeapons():
    """Primes the datastore with Weapons data.
    """
    logging.info('###################### seedWeapons() #####################')
    weapons = []
    for x in WEAPON_DATA:
        logging.info('################## x = '+str(x)+' ####################')        
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
    logging.info('###################### seedAttacks() ######################')
    attacks = []   
         
    for x in ATTACK_DATA:    
        logging.info('################## x = '+str(x)+' ####################')
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
                         