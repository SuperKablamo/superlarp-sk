#
# Copyright 2010 SuperKablamo, LLC
# info@superkablamo.com
#

import logging

from django.utils import simplejson
from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.ext.db import polymodel

############################# CONSTANTS ######################################
##############################################################################
ABILITIES_KEY = 'abilities'
SKILLS_KEY = 'skills'
DEFENSES_KEY = 'defenses'

ABILITY_KEYS = ['STR', 'CON', 'DEX', 'INT', 'WIS', 'CHA']

SKILL_KEYS = ['Acrobatics', 'Arcana', 'Athletics', 'Bluff', 'Diplomacy',
              'Dungeoneering', 'Endurance', 'Heal', 'History', 'Insight',
              'Intimidate', 'Nature', 'Perception', 'Religion', 'Stealth',
              'Streetwise', 'Thievery']   
          
DEFENSE_KEYS = ['AC', 'FORT', 'REF', 'WILL']

############################# CUSTOM PROPERTIES ##############################
##############################################################################   
class JSONProperty(db.TextProperty):
    def validate(self, value):
        return value
 
    def get_value_for_datastore(self, model_instance):
        result = super(JSONProperty, self).get_value_for_datastore(model_instance)
        result = simplejson.dumps(result)
        return db.Text(result)
	 
    def make_value_from_datastore(self, value):
        try:
            value = simplejson.loads(str(value))
        except:
            pass

        return super(JSONProperty, self).make_value_from_datastore(value)

############################# DATASTORE MODELS ###############################
##############################################################################

class UserPrefs(db.Model): # user.user_id() s is key_name
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)

################# CHARACTERS #################################################
class Character(polymodel.PolyModel):
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)    
    name = db.StringProperty(required=True)
    level = db.IntegerProperty(required=True, default=1)
    race = db.StringProperty(required=True)
    alignment = db.StringProperty(required=True)
    size = db.StringProperty(required=True)
    experience = db.IntegerProperty(required=True, default=0)
    hit_points = db.IntegerProperty(required=True)
    speed = db.IntegerProperty(required=True)
    powers = db.ListProperty(db.Key, required=True, default=None)
    items = db.ListProperty(db.Key, required=True, default=None)
    equipped = db.ListProperty(db.Key, required=True, default=None)
    scores = JSONProperty(required=True)  #  {"abilities": {"STR": {"score": 10, "mod": 1, "mods": [{"origin": "Singing Sword", "mod": 1}, {"origin": "Dwarf", "mod": 1}]}}, "skills": {"Acrobatics": {"score": 10, "mod": 1, "mods": [{"origin": "trained", "mod": 5}, {"origin": "DEX", "mod": 1}]}}}
       
        
class PlayerCharacter(Character):
    cast = db.StringProperty(required=True)
    height = db.IntegerProperty(required=True)
    weight = db.IntegerProperty(required=True)
    
class NonPlayerCharacter(Character):    
    origin = db.StringProperty(required=True)
    category = db.StringProperty(required=True)
    keywords = db.StringListProperty(required=True, default=None)    
    treasure = db.ReferenceProperty(required=True)
##############################################################################
    
class Skills(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)    
    pc = db.ReferenceProperty(PlayerCharacter, required=True) # The Player Character   
    acrobatics = db.IntegerProperty(required=True)
    arcana = db.IntegerProperty(required=True)
    athletics = db.IntegerProperty(required=True)
    bluff = db.IntegerProperty(required=True)
    diplomacy = db.IntegerProperty(required=True)
    dungeoneering = db.IntegerProperty(required=True)
    endurance = db.IntegerProperty(required=True)
    heal = db.IntegerProperty(required=True)
    history = db.IntegerProperty(required=True)
    insight = db.IntegerProperty(required=True)
    intimidate = db.IntegerProperty(required=True)
    nature = db.IntegerProperty(required=True)
    perception = db.IntegerProperty(required=True)
    religion = db.IntegerProperty(required=True)
    stealth = db.IntegerProperty(required=True)
    streetwise = db.IntegerProperty(required=True)
    thievery = db.IntegerProperty(required=True)

########### BONUSES ##########################################################
class Bonus(polymodel.PolyModel):
    bonus = db.IntegerProperty(required=True, default=1) # Positive modifier   
        
class AbilityBonus(Bonus):
    ability = db.StringProperty(required=True) # Applies to an Ability

class DefenseBonus(Bonus):
    ability = db.StringProperty(required=True) # Applies to an Defense

class ResistenceBonus(Bonus):
    damage_keyword = db.StringProperty(required=True) # Applies to a Damage

class SkillBonus(Bonus):
    skill = db.StringProperty(required=True)            
##############################################################################

############### POWERS #######################################################
class Power(polymodel.PolyModel):
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)    
    name = db.StringProperty(required=True)
    recharge = db.IntegerProperty(required=True) # Seconds to recharge
    level = db.IntegerProperty(required=True) # Level requirement
    source_keyword = db.StringProperty(required=False) 
    effect_keyword = db.StringProperty(required=False) 
    cast = db.StringListProperty(required=True, default=None) # Allowed Casts
    mods = JSONProperty(required=True)
    
class Attack(Power):
    damage_keyword = db.StringListProperty(required=True, default=None)
    accessory_keyword = db.StringProperty(required=False)
    attack_range = db.IntegerProperty(required=True, default=0)
    attack_ability = db.StringProperty(required=True) # Attacker ability
    attack_mod = db.IntegerProperty(required=True, default=0) # Attack bonus
    defense_ability = db.StringProperty(required=True) # Defender ability
    hit_weapon_multiplier = db.IntegerProperty(required=True, default=1)
    hit_ability_bonus = db.StringProperty(required=False) 
    effect = db.StringProperty(required=False)
    max_targets = db.IntegerProperty(required=True, default=1)
    max_attacks = db.IntegerProperty(required=True, default=1)
    
class Utility(Power):
    foo = db.StringProperty(required=False)

class Heal(Power):
    hit_points =  db.IntegerProperty(required=True) # Hit Points healed
    effect_range = db.IntegerProperty(required=True, default=1)
##############################################################################
    
############### ITEMS ########################################################    
class Item(polymodel.PolyModel):
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)    
    name = db.StringProperty(required=True)
    level = db.IntegerProperty(required=True, default=1) # Level requirement
    description = db.TextProperty(required=False)
    slot = db.StringProperty(required=False) # Body slot this item occupies
    cost = db.IntegerProperty(required=True)
    weight = db.IntegerProperty(required=True, default=0)
    magic = db.BooleanProperty(required=True, default=False)    
    cast = db.StringListProperty(required=True, default=None) # Allowed Casts  
    power = db.ReferenceProperty(required=False) # Inherent Power
    mods = JSONProperty(required=True)
    
class Weapon(Item):
    attack_mod = db.IntegerProperty(required=True) # Modifier to attack roll
    damage_die = db.IntegerProperty(required=True) # Type of die to roll
    dice = db.IntegerProperty(required=True) # Number of dice to roll
    group = db.StringListProperty(required=True)
    attributes = db.StringListProperty(required=True)
    short_range = db.IntegerProperty(required=True, default=0)
    long_range = db.IntegerProperty(required=True, default=0)
    
class Armor(Item):
    armor_mod = db.IntegerProperty(required=True) # Modifier to armor
    check_mod = db.IntegerProperty(required=True) # Modifier to skill checks
    speed_mod = db.IntegerProperty(required=True) # Modifier to speed
    
class Implement(Item):
    category = db.StringProperty(required=True) # Staff, Rod, Orb ...
        
class Gear(Item):                    
    foo = db.StringProperty(required=False)  
##############################################################################          

class Guild(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)   
    owner = db.ReferenceProperty(PlayerCharacter, required=True)
    leaders = db.ListProperty(db.Key, required=True, default=None) 
    name = db.StringProperty(required=True)
    motto = db.StringProperty(required=False)
    description = db.TextProperty(required=False)
    members = db.ListProperty(db.Key, required=True, default=None)
    experience = db.IntegerProperty(required=True, default=0)
    alignment = db.StringProperty(required=True)
    mods = JSONProperty(required=True)
    
class Cast(db.Model):
    name = db.StringProperty(required=True)
    motto = db.StringProperty(required=True)    
    hit_point_base = db.IntegerProperty(required=True) 
    hit_point_level = db.IntegerProperty(required=True)
    base_skill = db.StringProperty(required=True)
    skills = db.StringListProperty(required=True, default=None)
    mods = JSONProperty(required=True) # {"skills": [], "abilities": [], "defenses": [{'origin': 'Wizard', 'type': 'FORT', 'mod': 1}, {'origin': 'Wizard', 'type': 'REF', 'mod': 1}]}      
    
class Race(db.Model):
    name = db.StringProperty(required=True)
    motto = db.StringProperty(required=True)
    size = db.StringProperty(required=True)
    speed = db.IntegerProperty(required=True)
    min_height = db.IntegerProperty(required=True)
    max_height = db.IntegerProperty(required=True)
    min_weight = db.IntegerProperty(required=True)
    max_weight = db.IntegerProperty(required=True)
    languages = db.StringListProperty(required=True, default=None)  
    mods = JSONProperty(required=True) # {"skills": [{'origin': 'Human', 'type': "Dungeoneering", 'mod': 2}, {'origin': 'Human', 'type': Endurance", 'mod': 2}], "abilities": [{'origin': 'Human', 'type': "CON", 'mod': 2}, {'origin': 'Human', 'type': "WIS", 'mod': 2}], "defenses": []}      

class Treasure(db.Model):
    level = db.IntegerProperty(required=True, default=1) # Level requirement           
    items = db.ListProperty(db.Key, required=True, default=None)          
    gold = db.IntegerProperty(required=True)
