# ============================================================================
# Copyright (c) 2011, SuperKablamo, LLC.
# All rights reserved.
# info@superkablamo.com
#
# Models.py defines the Data and Models for the game world.
#
# ============================================================================

############################# GAE IMPORTS ####################################
##############################################################################
import logging

from django.utils import simplejson
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.ext.db import polymodel

############################# CONSTANTS ######################################
##############################################################################
ABILITIES_KEY = 'abilities'
SKILLS_KEY = 'skills'
DEFENSES_KEY = 'defenses'
ABILITY_MOD = 'Ability'
SCORE_KEYS = [ABILITIES_KEY, SKILLS_KEY, DEFENSES_KEY]

ABILITY_KEYS = ['STR', 'CON', 'DEX', 'INT', 'WIS', 'CHA']

SKILL_KEYS = ['Acrobatics', 'Arcana', 'Athletics', 'Bluff', 'Diplomacy',
              'Dungeoneering', 'Endurance', 'Heal', 'History', 'Insight',
              'Intimidate', 'Nature', 'Perception', 'Religion', 'Stealth',
              'Streetwise', 'Thievery']   
          
DEFENSE_KEYS = ['AC', 'FORT', 'REF', 'WILL']

ABILITY_MODIFIERS = {'1': -5, '2': -4, '3': -4, '4': -3, '5': -3, '6': -2, 
                     '7': -2, '8': -1, '9': -1, '10': 0, '11': 0, '12': 1,
                     '13': 1, '14': 2, '15': 2, '16': 3, '17': 3, '18': 4,
                     '19': 4, '20': 5, '21': 5, '22': 6, '23': 6, '24': 7,
                     '25': 7, '26': 8, '27': 8}
                
ALIGNMENTS = ['Good', 'Lawful good', 'Unaligned', 'Evil', 'Chaotic Evil']  

# Model names for convienence 
PC = 'PlayerCharacter'
NPC = 'NonPlayerCharacter'
MON = 'Monster'
WPN = 'Weapon'
ARM = 'Armor'
IMP = 'Implement'
POT = 'Potion'
RIN = 'Ring'
ART = 'Artifact'
GEA = 'Gear'
ATT = 'Attack'  
UTL = 'Utility'   
HEL = 'Heal'     

# NPC Roles
ART = 'Artillery'
BRU = 'Brute'
CON = 'Controller'
LUR = 'Lurker'
MIN = 'Minion'
SKI = 'Skirmisher'
SOL = 'Soldier'

# NPC Challenge
STAN = 'Standard'
ELIT = 'Elite'
SOLO = 'Solo'
LEAD = 'Leader'       
     
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
    speed = db.IntegerProperty(required=True)
    items = db.ListProperty(db.Key, required=True, default=None)
    hit_points = JSONProperty(required=True) # {"hp": 10, "surge": 2, "recharge": 10800}
    scores = JSONProperty(required=True)  #  {"abilities": {"STR": {"score": 10, "mod": 1, "mods": [{"origin": "Singing Sword", "mod": 1}, {"origin": "Dwarf", "mod": 1}]}}, "skills": {"Acrobatics": {"score": 10, "mod": 1, "mods": [{"origin": "trained", "mod": 5}, {"origin": "DEX", "mod": 1}]}}}
    languages = db.StringListProperty(required=True, default=None) 
    immunities = db.StringListProperty(required=True, default=None) 
    resist = JSONProperty(required=False, default=None) # {'Fire': 10, 'Necrotic': 10}
    vulnerable = JSONProperty(required=False, default=None) # {'Radiant': 5}
        
class PlayerCharacter(Character):
    cast = db.StringProperty(required=True)
    height = db.IntegerProperty(required=True)
    weight = db.IntegerProperty(required=True)
    powers = db.ListProperty(db.Key, required=True, default=None)
    equipped = db.ListProperty(db.Key, required=True, default=None)
    purse = JSONProperty(required=True) # {"copper": 800, "silver": 500, "gold": 90, "platinum": 4, "gems": 86}

class Player(PlayerCharacter):
    user = db.UserProperty(required=False)
    @property
    def parties(self):
        return PlayerParty.all().filter('members', self.key())
        
class PlayerCharacterTemplate(PlayerCharacter):
    template_id = db.IntegerProperty(required=True)            
    
class NonPlayerCharacter(Character):    
    description = db.TextProperty(required=True)
    origin = db.StringProperty(required=True)
    category = db.StringProperty(required=True)
    keywords = db.StringListProperty(required=True, default=None) 
    actions = JSONProperty(required=True, default=None)      
    artifacts = db.StringListProperty(required=True, default=None) 
    role = db.StringProperty(required=True)
    challenge = db.StringProperty(required=True, default=STAN)

class NonPlayerCharacterTemplate(NonPlayerCharacter):
    template_id = db.IntegerProperty(required=True)   
    unique = db.BooleanProperty(required=True, default=False) # Is there only 1
    active = db.BooleanProperty(required=True, default=False) # Is one on the map?
    
class Monster(NonPlayerCharacter): 
    user = db.UserProperty(required=False)
    @property
    def parties(self):
        return NonPlayerParty.all().filter('monsters', self.key())
##############################################################################
    
class Skills(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)    
    pc = db.ReferenceProperty(PlayerCharacter, required=True, collection_name='skills') # The Player Character   
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
    description = db.TextProperty(required=True)
    recharge = db.IntegerProperty(required=True) # Seconds to recharge
    level = db.IntegerProperty(required=True) # Level requirement
    source_keyword = db.StringProperty(required=False) 
    casts = db.StringListProperty(required=True, default=None) # Allowed Casts
    json = JSONProperty(required=False)
    
class Attack(Power):
    damage_keywords = db.StringListProperty(required=True, default=None)
    accessory_keyword = db.StringProperty(required=False)
    ranges = db.IntegerProperty(required=True, default=1000)
    attack_ability = db.StringProperty(required=True) # Attacker ability
    attack_mod = db.IntegerProperty(required=True, default=0) # Attack bonus
    defense_ability = db.StringProperty(required=True) # Defender ability
    damage_weapon_multiplier = db.IntegerProperty(required=False) # Damage multiplier for weapon used
    damage_ability_mod = db.StringProperty(required=False) # Type of damage die to roll
    damage_dice = db.IntegerProperty(required=False) # Number of damage dice to roll
    damage_die = db.IntegerProperty(required=False)
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
    price = db.IntegerProperty(required=True)
    weight = db.IntegerProperty(required=True, default=0)
    magic = db.BooleanProperty(required=True, default=False)    
    casts = db.StringListProperty(required=True, default=None) # Allowed Casts  
    power = db.ReferenceProperty(required=False) # Inherent Power
    category = db.StringProperty(required=False)
    ability_type_bonus = db.StringProperty(required=False)
    ability_bonus = db.IntegerProperty(required=False)    
    json = JSONProperty(required=True)
    
class Weapon(Item):
    damage_die = db.IntegerProperty(required=True) # Type of die to roll
    damage_dice = db.IntegerProperty(required=True) # Number of dice to roll
    group = db.StringProperty(required=True)
    attributes = db.StringListProperty(required=True)
    ranges = db.IntegerProperty(required=True, default=0)
    proficiency = db.IntegerProperty(required=True, default=0)
    attack_bonus = db.IntegerProperty(required=False)
    damage_bonus = db.IntegerProperty(required=False)
    critical_damage_die = db.IntegerProperty(required=False)
    critical_damage_dice = db.IntegerProperty(required=False)    
    defense_type_bonus = db.StringProperty(required=False)
    defense_bonus = db.IntegerProperty(required=False)
    implement = db.BooleanProperty(required=True, default=False)  
    
class Armor(Item):
    bonus = db.IntegerProperty(required=True) # Modifier to armor
    check = db.IntegerProperty(required=True) # Modifier to skill checks
    speed = db.IntegerProperty(required=True) # Modifier to speed
    defense_type_bonus = db.StringProperty(required=False)
    defense_bonus = db.IntegerProperty(required=False)    

class Potion(Item):
    foo = db.StringProperty(required=False)     

class Artifact(Item):
    foo = db.StringProperty(required=False)         
    
class Ring(Item):
    foo = db.StringProperty(required=False)                  
        
class Gear(Item):                    
    foo = db.StringProperty(required=False)  
##############################################################################          

class Guild(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)   
    owner = db.ReferenceProperty(PlayerCharacter, required=True, collection_name='guild')
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
    surge_recharge = db.IntegerProperty(required=True)
    base_skill = db.StringProperty(required=True)
    skills = db.StringListProperty(required=True, default=None)
    armor_proficiencies = db.StringListProperty(required=True, default=None)
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
    mods = JSONProperty(required=True) # {"skills": [{'origin': 'Human', 'type': "Dungeoneering", 'mod': 2}, {'origin': 'Human', 'type': Endurance", 'mod': 2}], "defenses": []}      
    bonuses = JSONProperty(required=True) # {"abilities": [{'origin': 'Human', 'type': "CON", 'mod': 2}, {'origin': 'Human', 'type': "WIS", 'mod': 2}]}

############### Party ########################################################  
class Party(polymodel.PolyModel): # A party of PCs or NPCs
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    location = db.GeoPtProperty(required=True)
    log = JSONProperty(required=False)   
    json = JSONProperty(required=False)        

class PlayerParty(Party):
    leader = db.ReferenceProperty(PlayerCharacter, required=True)
    members = db.ListProperty(db.Key, required=True)
    
class NonPlayerParty(Party):        
    owner = db.UserProperty(required=False) # The id of a user or admin
    monsters = db.ListProperty(db.Key, required=True, default=None)   

############### MAP ##########################################################  
class Pin(polymodel.PolyModel): 
    location = db.GeoPtProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)  
    name = db.IntegerProperty(required=False)  
    description = db.TextProperty(required=False)
    
class Battle(Pin): # The location of a battle      
    attackers = db.ListProperty(db.Key, required=True)    
    defenders = db.ListProperty(db.Key, required=True)  
    winner = db.StringProperty(required=True)

class Capital(Pin):  # The Capital for a Guild     
    guild = db.ReferenceProperty(Guild, required=True)
    
class Dungeon(Pin): # The location of a Dungeon
    owner = db.ReferenceProperty(PlayerCharacter, required=True)

class Event(Pin): # The location of an Event
    start_date = db.DateTimeProperty(required=True)
    end_date = db.DateTimeProperty(required=True)

class Checkin(Pin): # The location of an active Player
    character = db.ReferenceProperty(Character, required=True)
    action = db.StringProperty(required=True)
    
##############################################################################  
