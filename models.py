# Datastore
import logging
from google.appengine.ext import db
from google.appengine.ext import blobstore

class UserPrefs(db.Model): # user.user_id() s is key_name
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)

################# CHARACTERS #################################################
class Character(db.PolyModel):
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)    
    name = db.StringProperty(required=True)
    level = db.IntegeryPropery(required=True, default=1)
    race = db.StringProperty(required=True)
    alignment = db.StringProperty(required=True)
    size = db.StringProperty(required=True)
    experience = db.IntegerProperty(required=True)
    strength = db.IntegerProperty(required=True)
    constitution = db.IntegerProperty(required=True)
    dexterity = db.IntegerProperty(required=True)
    intelligence = db.IntegerProperty(required=True)
    wisdom = db.IntegerProperty(required=True)
    charisma = db.IntegerProperty(required=True)
    hit_points = db.IntegerProperty(required=True)
    armor = db.IntegerProperty(required=True)
    fortitude = db.IntegerProperty(required=True)
    reflex = db.IntegerProperty(required=True)
    will = db.IntegerProperty(required=True)
    speed = db.IntegerProperty(required=True)
    perception = db.IntegerProperty(required=True)
    powers = db.ListProperty(db.Key, required=True, default=None)
    items = db.ListProperty(db.Key, required=True, default=None)
        
class PC(Character):
    cast = db.StringProperty(required=True)
    height = db.IntegerProperty(required=True)
    weight = db.IntegerProperty(required=True)
    
class NPC(Character):    
    origin = db.StringProperty(required=True)
    category = db.StringProperty(required=True)
    keywords = db.StringListProperty(required=True, default=None)    
    treasure = db.ReferenceProperty(required=True)
##############################################################################
    
class Skills(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)    
    pc = db.ReferenceProperty(PC, required=True) # The Player Character   
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

############### POWERS #######################################################
class Power(db.PolyModel):
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)    
    name = db.StringProperty(required=True)
    recharge = db.IntegerProperty(required=True) # Seconds to recharge
    level = db.IntegerProperty(required=True) # Level requirement
    source_keyword = db.StringProperty(required=False) 
    effect_keyword = db.StringProperty(required=False) 
    cast = db.StringListProperty(required=True, default=None) # Allowed Casts 
    
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
    bonus = db.ReferenceProperty(Bonus, required=True)   

class Heal(Power):
    hit_points =  db.IntegerProperty(required=True) # Hit Points healed
    effect_range = db.IntegerProperty(required=True, default=1)
##############################################################################
    
############### ITEMS ########################################################    
class Item(db.PolyModel):
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)    
    name = db.StringProperty(required=True)
    level = db.IntegerProperty(required=True, default=1) # Level requirement
    description = db.TextProperty(required=False)
    slot = db.StringProperty(required=False) # Body slot this item occupies
    cost = db.IntegerProperty(required=True)
    weight = db.IntegerProperty(required=True, default=0)
    bonuses = db.ListProperty(db.Key, required=True, default=None) 
    magic = db.BooleanProperty(required=True, default=False)    
    cast = db.StringListProperty(required=True, default=None) # Allowed Casts  
    power = db.ReferenceProperty(required=False) # Inherent Power
    
class Weapon(Item):
    attack_mod = db.IntegerProperty(required=True) # Modifier to attack roll
    damage_die = db.IntegerProperty(required=True) # Type of die to roll
    dice = db.IntegerProperty(required=True) # Number of dice to roll
    group = db.StringListProperty(required=True)
    properties = db.StringListProperty(required=True)
    short_range = db.IntegerProperty(required=True, default=0)
    long_range = db.IntegerProperty(required=True, default=0)
    
class Armor(Item):
    armor_mod = db.IntegerProperty(required=True) # Modifier to armor
    check_mod = db.IntegerProperty(required=True) # Modifier to skill checks
    speed_mod = db.IntegerProperty(required=True) # Modifier to speed
    
class Implement(Item):
    category = db.StringProperty(required=True) # Staff, Rod, Orb ...
        
class Gear(Item):                    
    ability_bonus = db.ReferenceProperty(AbilityBonus, required=True)    
##############################################################################          

########### BONUSES ##########################################################
class Bonus(db.PolyModel):
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

class Guild(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)   
    owner = db.ReferenceProperty(PC, required=True)
    leaders = db.ListProperty(db.Key, required=True, default=None) 
    name = db.StringProperty(required=True)
    motto = db.StringProperty(required=False)
    description = db.TextProperty(required=False)
    members = db.ListProperty(db.Key, required=True, default=None)
    bonuses = db.ListProperty(Bonus, required=True, default=None)
    experience = db.IntegerProperty(required=True, default=0)
    alignment = db.StringProperty(required=True)
    
class Cast(db.Model):
    name = db.StringProperty(required=True)
    description = db.TextProperty(required=True)    
    defense_bonuses = db.ListProperty(db.Key, required=True, default=None)
    skill_bonuses = db.ListProperty(db.Key, required=True, default=None)
    resistence_bonuses = db.ListProperty(db.Key, required=True, default=None)
    hit_point_base = db.IntegerProperty(required=True) 
    hit_point_level = db.IntegerProperty(required=True)
    base_skill = db.StringProperty(required=True)
    skills = db.StringListProperty(required=True, default=None)
    
class Race(db.Model):
    name = db.StringProperty(required=True)
    description = db.TextProperty(required=True)
    ability_bonuses = db.ListProperty(db.Key, required=True, default=None)
    skill_bonuses = db.ListProperty(db.Key, required=True, default=None)
    resistence_bonuses = db.ListProperty(db.Key, required=True, default=None)    
    size = db.StringProperty(required=True)
    speed = db.IntegerProperty(required=True)
    min_height = db.IntegerProperty(required=True)
    max_height = db.IntegerProperty(required=True)
    min_weight = db.IntegerProperty(required=True)
    max_weight = db.IntegerProperty(required=True)
    languages = db.StringListProperty(required=True, default=None)    
    
class Build(db.Model):
    pc = db.ReferenceProperty(PC, required=True)
    head = db.ReferenceProperty(Item, required=False)
    arm = db.ReferenceProperty(Item, required=False)
    left_hand = db.ReferenceProperty(Item, required=False)
    right_hand = db.ReferenceProperty(Item, required=False)
    leg = db.ReferenceProperty(Item, required=False)
    feet = db.ReferenceProperty(Item, required=False)
    waist = db.ReferenceProperty(Item, required=False)
    neck = db.ReferenceProperty(Item, required=False)
    rings = db.ListProperty(db.Key, required=True, default=None)     

class Treasure(db.Model):
    level = db.IntegerProperty(required=True, default=1) # Level requirement           
    items = db.ListProperty(db.Key, required=True, default=None)          
    gold = db.IntegerProperty(required=True)