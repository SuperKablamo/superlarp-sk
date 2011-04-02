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
import time

from google.appengine.ext import db
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

def rollEncounter(player_party, geo_pt):
    """Creates a random monster encounter.  Returns a NonPlayerParty of
    monsters or None.  The chance of encountering monsters is based on the
    player_party's encounter log.
    """ 
    logging.info(TRACE+'rollEncounter()')
    # Determine likelyhood of encounter ...
    '''
    {'encounters': {'total': 23, 'uniques': 2, 'start_time': POSIX
                   'last_encounter': {'time_since': POSIX, 'checks': 9}}}
    '''
    log = player_party.log
    checks = log['encounters']['last_encounter']['checks']
    player_party.log['encounters']['last_encounter']['checks'] = checks + 1
    mod = checks*2
    r = utils.roll(100, 1)
    if r > 97: unique = True
    else: unique = False
    r = r + mod 
    
    # There is an Encounter :)
    if r >= 75:
        # Update the Encounter Log ...
        player_party.log['encounters']['total'] += 1
        last_encounter = {'time_since': time.time(), 'checks': 0}
        player_party.log['encounters']['last_encounter'] = last_encounter
        
        monster_party = models.NonPlayerParty(location = geo_pt, 
                                              monsters = [],
                                              json = {'monsters': []})
        
        # Get number of PCs and the average level of the Party ...
        party_size = len(player_party.members)
        members = db.get(player_party.members)
        total = 0
        for m in members:
            total = total + m.level
        avg_level = total/party_size
        logging.info(TRACE+'rollEncounter():: avg_level = '+str(avg_level))

        # Get the appropriate Monster table for the Party level ...    
        monster_level = MONSTER_XP_LEVELS[avg_level]
        logging.info(TRACE+'rollEncounter():: monster_level = '+str(monster_level))
        
        # Get the XP total for this Encounter
        xp_total = monster_level[models.STAN]*party_size    
        
        # Roll Monster Encounter template   
        if unique:
            r = 6
        else:    
            r = utils.roll(5, 1)
        
        entities = []    
        ######################################################################
        # Minions Minions Minions!
        if r == 1:
            logging.info(TRACE+'rollEncounter():: Minions Minions Minions!')              
            q = db.Query('NonPlayerCharacter', key_only=True)
            q.filter('role =', models.MIN)
            q.filter('challenge = ', models.STAN)
            q.filter('level = ', avg_level)
            q.filter('unique =', False)
            npc_keys = q.fetch(100)
            r = utils.roll(len(npc_keys), 1)
            npc_key = npc_keys[r]
            npc = db.get(npc_key)
            monster_party_size = party_size*4
            for i in monster_party_size:
                minion = db.Monster(npc = npc_key,
                                    json = character.getJSONNonPlayer(npc))
                                    
                entities.append(minion)

        ######################################################################        
        # Solo boss - uh-oh.                        
        elif r == 2:  
            logging.info(TRACE+'rollEncounter():: Solo boss - uh-oh!')              
            q = db.Query('NonPlayerCharacter', key_only=True)
            q.filter('challenge = ', models.SOLO)
            q.filter('level = ', avg_level)
            q.filter('unique =', False)            
            npc_keys = q.fetch(100)
            r = utils.roll(len(npc_keys), 1)
            npc_key = npc_keys[r]
            npc = db.get(npc_key)
            solo = db.Monster(npc = npc_key,
                              json = character.getJSONNonPlayer(npc))
                                
            entities.append(solo)

        ######################################################################        
        # Minions plus Mini-boss - oh noze!   
        elif r == 3:
            logging.info(TRACE+'rollEncounter():: Minions + Mini-boss!')                
            # Get Minions
            q = db.Query('NonPlayerCharacter', key_only=True)
            q.filter('role =', models.MIN)
            q.filter('challenge = ', models.STAN)
            q.filter('level = ', avg_level)
            q.filter('unique =', False)            
            npc_keys = q.fetch(100)
            r = utils.roll(len(npc_keys), 1)
            npc_key = npc_keys[r]
            npc = db.get(npc_key)
            minion_party_size = party_size*4
            if party_size > 1:
                minion_party_size -= 4
            for i in minion_party_size:
                minion = db.Monster(npc = npc_key,
                                    json = character.getJSONNonPlayer(npc))
                                    
                entities.append(minion)
            
            # Get Mini-boss
            q = db.Query('NonPlayerCharacter', key_only=True)
            q.filter('role !=', models.MIN)
            q.filter('challenge = ', models.ELIT)
            q.filter('level = ', avg_level)
            q.filter('unique =', False)            
            npc_keys = q.fetch(100)
            r = utils.roll(len(npc_keys), 1)
            npc_key = npc_keys[r]
            npc = db.get(npc_key)
            elite = db.Monster(npc = npc_key,
                               json = character.getJSONNonPlayer(npc))
                                    
            entities.append(elite)            
                
        ######################################################################
        # There's one for everyone.                
        elif r == 4:  
            logging.info(TRACE+'rollEncounter():: There\'s one for everyone!')  
            
                         
            foo = 1
            
            
            
        ######################################################################
        # Easy pickings.            
        elif r == 5:
            logging.info(TRACE+'rollEncounter():: Easy pickings!')        
            if avg_level > 2:
                avg_level -= 2
                    
            # Get Minions
            q = db.Query('NonPlayerCharacter', key_only=True)
            q.filter('role =', models.MIN)
            q.filter('challenge = ', models.STAN)
            q.filter('level = ', avg_level)
            q.filter('unique =', False)            
            npc_keys = q.fetch(100)
            r = utils.roll(len(npc_keys), 1)
            npc_key = npc_keys[r]
            npc = db.get(npc_key)
            minion_party_size = party_size*4
            if party_size > 1:
                minion_party_size -= 4
            for i in minion_party_size:
                minion = db.Monster(npc = npc_key,
                                    json = character.getJSONNonPlayer(npc))
                
                entities.append(minion)                    
            
            # Get Standards if the Player Party level is high enough            
            if not avg_lvl < 3:
                q = db.Query('NonPlayerCharacter', key_only=True)
                q.filter('role !=', models.MIN)
                q.filter('challenge = ', models.STAN)
                q.filter('level = ', avg_level)
                q.filter('unique =', False)            
                npc_keys = q.fetch(100)
                r = utils.roll(len(npc_keys), 1)
                npc_key = npc_keys[r]
                npc = db.get(npc_key)
                standard_party_size = 1
                if party_size > 3:
                    standard_party_size = 2
                for i in standard_party_size:
                    monster = db.Monster(npc = npc_key,
                                         json = character.getJSONNonPlayer(npc))
                                    
                    entities.append(monster)

        ######################################################################        
        elif r == 6: # Unique NPC.
            logging.info(TRACE+'rollEncounter():: Unique NPC')
            player_party.log['encounters']['uniques'] += 1            
            q = db.Query('NonPlayerCharacter', key_only=True)
            q.filter('level = ', avg_level)
            q.filter('unique =', True)            
            npc_keys = q.fetch(100)
            r = utils.roll(len(npc_keys), 1)
            npc_key = npc_keys[r]
            npc = db.get(npc_key)
            solo = db.Monster(npc = npc_key,
                              json = character.getJSONNonPlayer(npc))
                            
            entities.append(solo)
            
            # More than 1 Player? Throw in some Minions and make it a Party!
            if party_size > 1:
                q = db.Query('NonPlayerCharacter', key_only=True)
                q.filter('role =', models.MIN)
                q.filter('challenge = ', models.STAN)
                q.filter('level = ', avg_level)
                q.filter('unique =', False)            
                npc_keys = q.fetch(100)
                r = utils.roll(len(npc_keys), 1)
                npc_key = npc_keys[r]
                npc = db.get(npc_key)
                minion_party_size = party_size*4
                for i in minion_party_size:
                    minion = db.Monster(npc = npc_key,
                                        json = character.getJSONNonPlayer(npc))

                    entities.append(minion)                    

    else:
        return None            
    
    entities.append(player_party)
    db.put(entities) # IDs assigned

    # Need a new loop to get monster JSON after IDs are created ... 
    for e in entities:
        if e.class_name() == models.MON:
            monster_json = monster.getJSONMonster(e)
            monster_party.json['monsters'].append(monster_json)
    
    return monster_party     

def logBattle(location, loot, *characters):
    """Stores a summary of a battle. 
    """
    return True

######################## DATA ################################################
##############################################################################    

MONSTER_XP_LEVELS = [
    {models.STAN: 100, models.MIN: 25, models.ELIT: 200, models.SOLO: 500},
    {models.STAN: 125, models.MIN: 31, models.ELIT: 250, models.SOLO: 625},
    {models.STAN: 150, models.MIN: 38, models.ELIT: 300, models.SOLO: 750},
    {models.STAN: 175, models.MIN: 44, models.ELIT: 350, models.SOLO: 875},
    {models.STAN: 200, models.MIN: 50, models.ELIT: 400, models.SOLO: 1000},
    {models.STAN: 250, models.MIN: 63, models.ELIT: 500, models.SOLO: 1250},
    {models.STAN: 300, models.MIN: 75, models.ELIT: 600, models.SOLO: 1500},
    {models.STAN: 350, models.MIN: 88, models.ELIT: 700, models.SOLO: 1750},
    {models.STAN: 400, models.MIN: 100, models.ELIT: 800, models.SOLO: 2000},
    {models.STAN: 500, models.MIN: 125, models.ELIT: 1000, models.SOLO: 2500},
    {models.STAN: 600, models.MIN: 150, models.ELIT: 1200, models.SOLO: 3000},
    {models.STAN: 700, models.MIN: 175, models.ELIT: 1400, models.SOLO: 3500},
    {models.STAN: 800, models.MIN: 200, models.ELIT: 1600, models.SOLO: 4000},
    {models.STAN: 1000, models.MIN: 250, models.ELIT: 2000, models.SOLO: 5000},
    {models.STAN: 1200, models.MIN: 300, models.ELIT: 2400, models.SOLO: 6000},
    {models.STAN: 1400, models.MIN: 350, models.ELIT: 2800, models.SOLO: 7000},
    {models.STAN: 1600, models.MIN: 400, models.ELIT: 3200, models.SOLO: 8000},
    {models.STAN: 2000, models.MIN: 500, models.ELIT: 4000, models.SOLO: 10000},
    {models.STAN: 2400, models.MIN: 600, models.ELIT: 4800, models.SOLO: 12000},
    {models.STAN: 2800, models.MIN: 700, models.ELIT: 5600, models.SOLO: 14000},
    {models.STAN: 3200, models.MIN: 800, models.ELIT: 6400, models.SOLO: 16000},
    {models.STAN: 4150, models.MIN: 1038, models.ELIT: 8300, models.SOLO: 20750},
    {models.STAN: 5100, models.MIN: 1275, models.ELIT: 10200, models.SOLO: 25500},
    {models.STAN: 6050, models.MIN: 1513, models.ELIT: 12100, models.SOLO: 30250},
    {models.STAN: 7000, models.MIN: 1750, models.ELIT: 14000, models.SOLO: 35000},
    {models.STAN: 9000, models.MIN: 2250, models.ELIT: 18000, models.SOLO: 45000},
    {models.STAN: 11000, models.MIN: 2750, models.ELIT: 22000, models.SOLO: 55000},
    {models.STAN: 13000, models.MIN: 3250, models.ELIT: 26000, models.SOLO: 65000}]

