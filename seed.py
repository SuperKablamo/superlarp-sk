#
# Copyright 2010 SuperKablamo, LLC
# info@superkablamo.com
#

############################# SK IMPORTS #####################################
############################################################################## 
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
     'description': 'Masters of stone and iron, dauntless and unyielding in the face of adversity.',
     'ability_bonuses': [{'Constitution': 2}, {'Wisdom': 2}],     
     'size': 'Medium',
     'speed': 5,
     'min_height': 51,
     'max_height': 57,
     'min_weight': 160,
     'max_weight': 220},
    {'name': 'Elf',
     'description': 'Quick, wary archers who freely roam the forests and wilds.',
     'ability_bonuses': [{'Dexterity': 2}, {'Wisdom': 2}],     
     'size': 'Medium',
     'speed': 7,
     'min_height': 64,
     'max_height': 74,
     'min_weight': 130,
     'max_weight': 170},
    {'name' : 'Halfling',
     'description': 'Quick and resourceful wanderers, small in staturs but great in courage.',
     'ability_bonuses': [{'Dexterity': 2}, {'Charisma': 2}],   
     'size': 'Small',
     'speed': 6,
     'min_height': 46,
     'max_height': 50,
     'min_weight': 75,
     'max_weight': 85},
    {'name': 'Human',
     'description': 'Ambitious, driven, pragmatic - a race of heroes, and also a race of villians.',
     'ability_bonuses': [{'Constitution': 2}, {'Intelligence': 2}],
     'size': 'Medium',
     'speed': 6,
     'min_height': 66,
     'max_height': 74,
     'min_weight': 135,
     'max_weight' : 220}]
     
CAST_DATA = [
    {'name': 'Cleric',
     'description': 'Have courage, my friends!  Pelor favors us today!',
     'hit_point_base': 12,
     'hit_point_level': 5,
     'base_skill': 'Religion',
     'skills': ['Arcana', 'Diplomacy', 'Heal', 'History', 'Insight'],
     'defense_bonuses': [{'Will': 2}] },
    {'name': 'Ranger',
     'description': 'I\'ll get the one in the back.  That\'s one hobgoblin who\'ll regret lifting a bow.',
     'hit_point_base': 12,
     'hit_point_level': 5,
     'base_skill': 'Nature',
     'skills': ['Acrobatics', 'Athletics', 'Dungeoneering', 'Endurance', 'Heal', 'Perception', 'Stealth'],
     'defense_bonuses': [{'Fortitude': 1}, {'Reflex': 1}] },     
    {'name': 'Rogue',
     'description': 'You look surprised to see me.  If you\'d been paying attention, you might still be alive.',
     'hit_point_base': 12,
     'hit_point_level': 5,
     'base_skill': 'Stealth',
     'skills': ['Acrobatics', 'Athletics', 'Bluff', 'Dungeoneering', 'Insight', 'Intimidate', 'Perception', 'Streetwise', 'Thievery'],
     'defense_bonuses': [{'Reflex': 2}] },     
    {'name': 'Wizard',
     'description': 'I am the fire that burns, the choking fog, the storm that rains devastation on our foes.',
     'hit_point_base': 10,
     'hit_point_level': 4,
     'base_skill': 'Arcana',
     'skills': ['Diplomacy', 'Dungeoneering', 'History', 'Insight', 'Nature', 'Religion'],
     'defense_bonuses': [{'Will': 2}] },  
    {'name': 'Fighter',
     'description': 'You\'ll have to deal with me first, dragon!',
     'hit_point_base': 15,
     'hit_point_level': 6,
     'base_skill': 'Athletics',
     'skills': ['Endurance', 'Heal', 'Intimidate', 'Streetwise'],
     'defense_bonuses': [{'Fortitude': 2}] },  
    {'name': 'Barbarian',
     'description': 'My strength is the fury of the wild.',
     'hit_point_base': 15,
     'hit_point_level': 6,
     'base_skill': 'Endurance',
     'skills': ['Acrobatics', 'Athletics', 'Heal', 'Intimidate', 'Nature', 'Perception'],
     'defense_bonuses': [{'Fortitude': 2}] }]     
     
######################## METHODS #############################################
##############################################################################
def seedRaces():
    for x in RACE_DATA:
        models.
    
    return
    
def seedCasts():
    return


        