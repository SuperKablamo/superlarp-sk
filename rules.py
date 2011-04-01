# ============================================================================
# Copyright (c) 2011, SuperKablamo, LLC.
# All rights reserved.
# info@superkablamo.com
#
# Rules.py defines the Methods for accessing game mechanics and rules.
#
# ============================================================================

############################# SK IMPORTS #####################################
############################################################################## 
import models
import utils

from model import character
from model import loot
from model import monster
from settings import *

############################# GAE IMPORTS ####################################
##############################################################################
import logging

from random import randrange

######################## METHODS #############################################
##############################################################################
    
def rollLoot(level=1): 
    """Returns a randomly generated, level appropriate treasure package.  
    Result is a dictionary of loot items
    """   
    return loot.loot(level)    
    
def rollAttack(attacker, defender, attack):
    """Resolves an attack and returns the damage result as a dictionary:
    {'damage': 10, type: 'Fire'}
    """        
    return damage

def rollEncounter(player, geo_pt, player_party):
    """Checks for any NPCs or PCs that the player can perceive.  Returns a 
    NonPlayerParty.
    """ 
    result = {'players': None, 'npcs': None, 'monster': None}
    
    # Determine likelyhood of encounter ...
    '''
    {'encounter': {'encounters': 23, 'uniques': 2, 'start_time': POSIX
                   'last_encounter': {'time_since': POSIX, 'checks': 9}}}
    '''
    log = player_party.log
    checks = log['encounter']['last_encounter']['checks']
    mod = checks*2
    r = utils.roll(100, 1)
    if r > 97: unique = True
    else: unique = False
    r = r + base 
    
    # There is an Encounter :)
    if r >= 75:
        monster_party = db.NonPlayerParty(location = geo_pt, 
                                          monsters = None,
                                          json = {'monsters': []})
        
        # Get number of PCs and the average level of the Party ...
        party_size = len(player_party.members)
        total = 0
        for m in player_party.members:
            total = total + m.level
        avg_level = total/party_size

        # Get the appropriate Monster table for the Party level ...    
        monster_level = MONSTER_XP_LEVEL[avg_level]

        # Get the XP total for this Encounter
        xp_total = monster_level[models.STAN]*party_size    
        
        # Roll Monster Encounter template   
        if unique:
            r = 6
        else:    
            r = utils.roll(5, 1)
        
        # Minions Minions Minions!
        if r == 1:
            q = Query('NonPlayerCharacter', key_only=True)
            q.filter('role =', models.MIN)
            q.filter('challenge = ', models.STAN)
            q.filter('level = ', avg_level)
            npc_keys = q.fetch(100)
            r = utils.roll(len(npc_keys), 1)
            npc_key = npc_keys[r]
            npc = db.get(npc_key)
            entities = []
            monster_party_size = party_size*4
            for i in monster_party_size:
                minion = db.Monster(npc = npc_key,
                                    json = character.getJSONNonPlayer(npc))
                                    
                entities.append(minion)
                minion_json = monster.getJSONMonster(monster)
                monster_party.json['monsters'].append(minion.json)                    
            db.put(entities)  
        
        # Solo boss - uh-oh.                        
        elif r == 2:  
            q = Query('NonPlayerCharacter', key_only=True)
            q.filter('role =', models.MIN)
            q.filter('challenge = ', models.STAN)
            q.filter('level = ', avg_level)
            npc_keys = q.fetch(100)
            r = utils.roll(len(npc_keys), 1)
            npc_key = npc_keys[r]
            npc = db.get(npc_key)
            entities = []
            monster_party_size = party_size*4
            for i in monster_party_size:
                minion = db.Monster(npc = npc_key,
                                    json = character.getJSONNonPlayer(npc))
                                
                entities.append(minion)
                minion_json = monster.getJSONMonster(monster)
                monster_party.json['monsters'].append(minion.json)                    
            db.put(entities)
        elif r == 3: # Minions plus mini-boss.   
            foo = 1
        elif r == 4: # One for everyone.    
            foo = 1
        elif r == 5: # Easy pickings.
            foo = 1
        elif r == 6: # Unique NPC.
            foo = 1
        
    # TODO updates encounter log and saves
    return monster_party     

def logBattle(location, loot, *characters):
    """Stores a summary of a battle. 
    """
    return True

######################## DATA ################################################
##############################################################################    

MONSTER_XP_LEVELS = [
    {'1': {models.STAN: 100, models.MIN: 25, models.ELIT: 200, models.SOLO: 500} },
    {'2': {models.STAN: 125, models.MIN: 31, models.ELIT: 250, models.SOLO: 625} },
    {'3': {models.STAN: 150, models.MIN: 38, models.ELIT: 300, models.SOLO: 750} },
    {'4': {models.STAN: 175, models.MIN: 44, models.ELIT: 350, models.SOLO: 875} },
    {'5': {models.STAN: 200, models.MIN: 50, models.ELIT: 400, models.SOLO: 1000} },
    {'6': {models.STAN: 250, models.MIN: 63, models.ELIT: 500, models.SOLO: 1250} },
    {'7': {models.STAN: 300, models.MIN: 75, models.ELIT: 600, models.SOLO: 1500} },
    {'8': {models.STAN: 350, models.MIN: 88, models.ELIT: 700, models.SOLO: 1750} },
    {'9': {models.STAN: 400, models.MIN: 100, models.ELIT: 800, models.SOLO: 2000} },
    {'10': {models.STAN: 500, models.MIN: 125, models.ELIT: 1000, models.SOLO: 2500} },
    {'11': {models.STAN: 600, models.MIN: 150, models.ELIT: 1200, models.SOLO: 3000} },
    {'12': {models.STAN: 700, models.MIN: 175, models.ELIT: 1400, models.SOLO: 3500} },
    {'13': {models.STAN: 800, models.MIN: 200, models.ELIT: 1600, models.SOLO: 4000} },
    {'14': {models.STAN: 1000, models.MIN: 250, models.ELIT: 2000, models.SOLO: 5000} },
    {'15': {models.STAN: 1200, models.MIN: 300, models.ELIT: 2400, models.SOLO: 6000} },
    {'16': {models.STAN: 1400, models.MIN: 350, models.ELIT: 2800, models.SOLO: 7000} },
    {'17': {models.STAN: 1600, models.MIN: 400, models.ELIT: 3200, models.SOLO: 8000} },
    {'18': {models.STAN: 2000, models.MIN: 500, models.ELIT: 4000, models.SOLO: 10000} },
    {'19': {models.STAN: 2400, models.MIN: 600, models.ELIT: 4800, models.SOLO: 12000} },
    {'20': {models.STAN: 2800, models.MIN: 700, models.ELIT: 5600, models.SOLO: 14000} },
    {'21': {models.STAN: 3200, models.MIN: 800, models.ELIT: 6400, models.SOLO: 16000} },
    {'22': {models.STAN: 4150, models.MIN: 1038, models.ELIT: 8300, models.SOLO: 20750} },
    {'23': {models.STAN: 5100, models.MIN: 1275, models.ELIT: 10200, models.SOLO: 25500} },
    {'24': {models.STAN: 6050, models.MIN: 1513, models.ELIT: 12100, models.SOLO: 30250} },
    {'25': {models.STAN: 7000, models.MIN: 1750, models.ELIT: 14000, models.SOLO: 35000} },
    {'26': {models.STAN: 9000, models.MIN: 2250, models.ELIT: 18000, models.SOLO: 45000} },
    {'27': {models.STAN: 11000, models.MIN: 2750, models.ELIT: 22000, models.SOLO: 55000} },
    {'28': {models.STAN: 13000, models.MIN: 3250, models.ELIT: 26000, models.SOLO: 65000} }]

