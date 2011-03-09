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
ABILITIES = ['strength', 'constitution', 'dexterity', 
             'intelligence', 'wisdom', 'charisma']

SKILLS = ['acrobatics', 'arcana', 'athletics', 'bluff', 'diplomacy',
          'dungeoneering', 'endurance', 'heal', 'history', 'insight',
          'intimidate', 'nature', 'perception', 'religion', 'stealth',
          'streetwise', 'thievery']             
    
RACE_DATA = [
    {'name': 'Dwarf',
     'motto': 'Masters of stone and iron, dauntless and unyielding in the face of adversity.',
     'ability_bonuses': [{'Constitution': 2}, {'Wisdom': 2}],    
     'skill_bonuses': [{'Dungeoneering': 2}, {'Endurance': 2}],    
     'defense_bonuses': [],              
     'size': 'Medium',
     'speed': 5,
     'min_height': 51,
     'max_height': 57,
     'min_weight': 160,
     'max_weight': 220},
    {'name': 'Elf',
     'motto': 'Quick, wary archers who freely roam the forests and wilds.',
     'ability_bonuses': [{'Dexterity': 2}, {'Wisdom': 2}],  
     'skill_bonuses': [{'Nature': 2}, {'Perception': 2}], 
     'defense_bonuses': [],               
     'size': 'Medium',
     'speed': 7,
     'min_height': 64,
     'max_height': 74,
     'min_weight': 130,
     'max_weight': 170},
    {'name' : 'Halfling',
     'motto': 'Quick and resourceful wanderers, small in stature but great in courage.',
     'ability_bonuses': [{'Dexterity': 2}, {'Charisma': 2}],   
     'skill_bonuses': [{'Acrobatics': 2}, {'Thievery': 2}], 
     'defense_bonuses': [],            
     'size': 'Small',
     'speed': 6,
     'min_height': 46,
     'max_height': 50,
     'min_weight': 75,
     'max_weight': 85},
    {'name': 'Human',
     'motto': 'Ambitious, driven, pragmatic - a race of heroes, and also a race of villians.',
     'ability_bonuses': [{'Constitution': 2}, {'Intelligence': 2}],
     'skill_bonuses': [],  
     'defense_bonuses': [{'Fortitude': 1}, {'Reflex': 1}, {'Will': 1}],           
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
     'base_skill': 'Religion',
     'skills': ['Arcana', 'Diplomacy', 'Heal', 'History', 'Insight'],
     'defense_bonuses': [{'Will': 2}] },
    {'name': 'Ranger',
     'motto': 'I\'ll get the one in the back.  That\'s one hobgoblin who\'ll regret lifting a bow.',
     'hit_point_base': 12,
     'hit_point_level': 5,
     'base_skill': 'Nature',
     'skills': ['Acrobatics', 'Athletics', 'Dungeoneering', 'Endurance', 'Heal', 'Perception', 'Stealth'],
     'defense_bonuses': [{'Fortitude': 1}, {'Reflex': 1}] },     
    {'name': 'Rogue',
     'motto': 'You look surprised to see me.  If you\'d been paying attention, you might still be alive.',
     'hit_point_base': 12,
     'hit_point_level': 5,
     'base_skill': 'Stealth',
     'skills': ['Acrobatics', 'Athletics', 'Bluff', 'Dungeoneering', 'Insight', 'Intimidate', 'Perception', 'Streetwise', 'Thievery'],
     'defense_bonuses': [{'Reflex': 2}] },     
    {'name': 'Wizard',
     'motto': 'I am the fire that burns, the choking fog, the storm that rains devastation on our foes.',
     'hit_point_base': 10,
     'hit_point_level': 4,
     'base_skill': 'Arcana',
     'skills': ['Diplomacy', 'Dungeoneering', 'History', 'Insight', 'Nature', 'Religion'],
     'defense_bonuses': [{'Will': 2}] },  
    {'name': 'Fighter',
     'motto': 'You\'ll have to deal with me first, dragon!',
     'hit_point_base': 15,
     'hit_point_level': 6,
     'base_skill': 'Athletics',
     'skills': ['Endurance', 'Heal', 'Intimidate', 'Streetwise'],
     'defense_bonuses': [{'Fortitude': 2}] },  
    {'name': 'Barbarian',
     'motto': 'My strength is the fury of the wild.',
     'hit_point_base': 15,
     'hit_point_level': 6,
     'base_skill': 'Endurance',
     'skills': ['Acrobatics', 'Athletics', 'Heal', 'Intimidate', 'Nature', 'Perception'],
     'defense_bonuses': [{'Fortitude': 2}] }]     
     
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
        for a in x['skill_bonuses']:
            skills.append(a)            
        for a in x['defense_bonuses']:
            defenses.append(a)            
        bonuses = {'abilities':abilities,'skills':skills,'defenses':defenses}            
        race = models.Race(key_name=x['name'],
                           name=x['name'],
                           motto=x['motto'],
                           size=x['size'],
                           speed=x['speed'],
                           min_height=x['min_height'],
                           max_height=x['max_height'],
                           min_weight=x['min_weight'],                           
                           max_weight=x['max_weight'],
                           bonuses=bonuses)
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
        defenses = []
        skills = []
        for a in x['defense_bonuses']:
            defenses.append(a)            
        bonuses = {'defenses':defenses} 
        for a in x['skills']:
            skills.append(a)           
        cast = models.Cast(key_name=x['name'],
                           name=x['name'],
                           motto=x['motto'],
                           hit_point_base=x['hit_point_base'],
                           hit_point_level=x['hit_point_level'],
                           base_skill=x['base_skill'],
                           skills=skills,
                           bonuses=bonuses)
        casts.append(cast)
    
    db.put(casts)                         
    return


"""
{'name': 'Barbarian',
 'motto': 'My strength is the fury of the wild.',
 'hit_point_base': 15,
 'hit_point_level': 6,
 'base_skill': 'Endurance',
 'skills': ['Acrobatics', 'Athletics', 'Heal', 'Intimidate', 'Nature', 'Perception'],
 'defense_bonuses': [{'Fortitude': 2}] }]

 class Cast(db.Model):
     name = db.StringProperty(required=True)
     motto = db.StringProperty(required=True)    
     bonuses = JSONProperty(required=True)
     resistence_bonuses = JSONProperty(required=True)
     hit_point_base = db.IntegerProperty(required=True) 
     hit_point_level = db.IntegerProperty(required=True)
     base_skill = db.StringProperty(required=True)
     skills = db.StringListProperty(required=True, default=None)

"""

        