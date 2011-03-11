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
    
     #----   CHANGE BONUS TO MOD -------
    
    
RACE_DATA = [
    {'name': 'Dwarf',
     'motto': 'Masters of stone and iron, dauntless and unyielding in the face of adversity.',
     'ability_mods': [{'origin': 'Dwarf', 'type': 'CON', 'mod': 2}, {'origin': 'Dwarf', 'type': 'WIS', 'mod': 2}],    
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
     'ability_mods': [{'origin': 'Elf', 'type': 'DEX', 'mod': 2}, {'origin': 'Elf', 'type': 'WIS', 'mod': 2}],  
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
     'ability_mods': [{'origin': 'Halfling', 'type': 'DEX', 'mod': 2}, {'origin': 'Halfling', 'type': 'CHA', 'mod': 2}],   
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
     'ability_mods': [{'origin': 'Human', 'type': 'CON', 'mod': 2}, {'origin': 'Human', 'type': 'INT', 'mod': 2}],
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
     'defense_mods': [{'origin': 'Cleric', 'type': 'WILL', 'mod': 2}] },
    {'name': 'Ranger',
     'motto': 'I\'ll get the one in the back.  That\'s one hobgoblin who\'ll regret lifting a bow.',
     'hit_point_base': 12,
     'hit_point_level': 5,
     'surge_recharge': 14400,     
     'base_skill': 'Nature',
     'skills': ['Acrobatics', 'Athletics', 'Dungeoneering', 'Endurance', 'Heal', 'Perception', 'Stealth'],
     'ability_mods': [],      
     'skill_mods': [],     
     'defense_mods': [{'origin': 'Ranger', 'type': 'FORT', 'mod': 1}, {'origin': 'Ranger', 'type': 'REF', 'mod': 1}] },     
    {'name': 'Rogue',
     'motto': 'You look surprised to see me.  If you\'d been paying attention, you might still be alive.',
     'hit_point_base': 12,
     'hit_point_level': 5,
     'surge_recharge': 14400,     
     'base_skill': 'Stealth',
     'skills': ['Acrobatics', 'Athletics', 'Bluff', 'Dungeoneering', 'Insight', 'Intimidate', 'Perception', 'Streetwise', 'Thievery'],
     'ability_mods': [],      
     'skill_mods': [],     
     'defense_mods': [{'origin': 'Rogue', 'type': 'REF', 'mod': 2}] },     
    {'name': 'Wizard',
     'motto': 'I am the fire that burns, the choking fog, the storm that rains devastation on our foes.',
     'hit_point_base': 10,
     'hit_point_level': 4,
     'surge_recharge': 14400,          
     'base_skill': 'Arcana',
     'skills': ['Diplomacy', 'Dungeoneering', 'History', 'Insight', 'Nature', 'Religion'],
     'ability_mods': [],      
     'skill_mods': [],     
     'defense_mods': [{'origin': 'Wizard', 'type': 'WILL', 'mod': 2}] },  
    {'name': 'Fighter',
     'motto': 'You\'ll have to deal with me first, dragon!',
     'hit_point_base': 15,
     'hit_point_level': 6,
     'surge_recharge': 9600,
     'base_skill': 'Athletics',
     'skills': ['Endurance', 'Heal', 'Intimidate', 'Streetwise'],
     'ability_mods': [],      
     'skill_mods': [],     
     'defense_mods': [{'origin': 'Fighter', 'type': 'FORT', 'mod': 2}] },  
    {'name': 'Barbarian',
     'motto': 'My strength is the fury of the wild.',
     'hit_point_base': 15,
     'hit_point_level': 6,
     'surge_recharge': 10800,     
     'base_skill': 'Endurance',
     'skills': ['Acrobatics', 'Athletics', 'Heal', 'Intimidate', 'Nature', 'Perception'],
     'ability_mods': [],      
     'skill_mods': [],     
     'defense_mods': [{'origin': 'Barbarian', 'type': 'FORT', 'mod': 2}] }]     
     
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
        for a in x['ability_mods']:
            abilities.append(a)
        for a in x['skill_mods']:
            skills.append(a)            
        for a in x['defense_mods']:
            defenses.append(a)            
        mods = {models.ABILITIES_KEY: abilities,
                   models.SKILLS_KEY: skills,
                   models.DEFENSES_KEY: defenses}
                               
        race = models.Race(key_name = x['name'],
                           name = x['name'],
                           motto = x['motto'],
                           size = x['size'],
                           speed = x['speed'],
                           min_height = x['min_height'],
                           max_height = x['max_height'],
                           min_weight = x['min_weight'],                           
                           max_weight = x['max_weight'],
                           mods = mods)
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
        cast = models.Cast(key_name = x['name'],
                           name = x['name'],
                           motto = x['motto'],
                           hit_point_base = x['hit_point_base'],
                           hit_point_level = x['hit_point_level'],
                           surge_recharge = x['surge_recharge'],
                           base_skill = x['base_skill'],
                           skills = trainable_skills,
                           mods = mods)
        casts.append(cast)
    
    db.put(casts)                         
    return
    