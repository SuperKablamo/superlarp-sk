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
    '''Returns a randomly generated, level appropriate treasure package.  
    Result is a dictionary of loot items
    '''   
    return loot.loot(level)    
    
def rollAttack(attacker, defender, attack):
    '''Resolves an attack and returns the damage result as a dictionary:
    {'damage': 10, 'keyword': 'Fire', 'status': 'Hit'}
    '''        
    _trace = TRACE+'rollAttack():: '
    logging.info(_trace)
    damage_keywords = attack['damage_keywords']
    json = {'damage': 0, 'keywords': damage_keywords, 'status': 'Hit'}
    
    # Roll Attack, natural 20 is a Hit
    attack_roll = utils.roll(20, 1)
    if attack_roll != 20:
        mod_attack_roll = attack_roll + attack['attack_mod']
        logging.info(_trace+'attack_roll = '+attack_roll)
        logging.info(_trace+'mod_attack_roll = '+mod_attack_roll)
    
        # Get Defense Score
        defense = attack['defense_ability']
        defense_score = defender['scores']['defenses'][defense]['score']
        logging.info(_trace+'defense_score = '+defense_score)     
    
        # Evaluate Hit
        if modattack_roll < defense_score:
            json['status'] = 'Miss'
    
    # Roll Damage
    damage_dice = attack['damage_dice'] 
    damage_die = attack['damage_die']
    damage_mod = attack['damage_mod']
    damage = 0
    if damage_die != 0:
        damage = utils.roll(damage_die, damage_dice)
    damage += damage_mod
    
    # Calculate Defenses
    immune_to = defender['immune']
    resists =  defender['resist']
    vulnerable_to = defender['vulnerable']
    damage_keyword = None
    for d in damage_keywords:
        
        # No Damage if Defender has immunity
        if d in immune_to:
            status = 'Immune to '+d
            json['status'] = status
            return json        
        
        # Reduced Damage for resistence
        resist_keys = resists.keys()
        if d in resist_keys:
            mod = resists[d]
            damage -= mod
        
        # Increased Damage for vulnerability
        vulnerable_keys = vulnerable_to.keys()
        if d in vulnerable_keys:
            mod = vulnerable_to[d]
            damage += mod
    
    # Damage cannot be less than 0
    if damage < 0:
        damage = 0    
    
    json['damage'] = damage
    return json
    
def rollEncounter(player_party, geo_pt):
    '''Creates a random monster encounter.  Returns a NonPlayerParty of
    monsters or None.  The chance of encountering monsters is based on the
    player_party's encounter log.
    ''' 
    _trace = TRACE+'rollEncounter():: '
    logging.info(_trace)

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
    logging.info(_trace+'r = '+str(r))     
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
        logging.info(_trace+'avg_level = '+str(avg_level))
        
        # Get the appropriate Monster table for the Party level ...    
        monster_level = MONSTER_XP_LEVELS[avg_level]
        logging.info(_trace+'monster_level = '+str(monster_level))
        
        # Get XP target for the encounter based on party level and size ...
        party_xp = monster_level[models.STAN]*party_size   
        logging.info(_trace+'party_xp = '+str(party_xp))
        
        # Roll Monster Encounter template   
        if unique:
            r = 10
        else:    
            # Change die sides to exclude results from monster generator
            
            # Low level
            if avg_level < 3:
                r = utils.roll(8, 1) 
                
            # Higher level includes Solo encounters           
            else:
                r = utils.roll(9, 1) 
        
        logging.info(_trace+'r = '+str(r))
        
        ### TEST ROLL - uncomment to test a specific roll
        #r = 3
        ###
        
        entities = []    
        ######################################################################
        # Minions Minions Minions!
        if r == 1 or r == 2:
            logging.info(_trace+'Minions Minions Minions!')              

            #  Randomly adjust level to create more variety ...
            if avg_level > 3:
                r = utils.roll(5, 1)
                logging.info(_trace+'r = '+str(r)) 
                level_mod = 0
                if r == 1:
                    level_mod = +2
                if r == 2:
                    level_mod = +1
                if r == 3:
                    level_mod = 0
                if r == 4:
                    level_mod = -1
                if r == 5:
                    level_mod = -2
                
                avg_level += level_mod        
                logging.info(_trace+'new avg_level = '+avg_level) 
            
            # Get Minion XP and # of Minions for this level ...
            minion_xp = MONSTER_XP_LEVELS[avg_level][models.MIN]
            npc_party_size = party_xp/minion_xp
            logging.info(_trace+'npc_party_size = '+str(npc_party_size)) 
                        
            q = db.Query(models.NonPlayerCharacter, keys_only=True)                    
            q.filter('role = ', models.MIN)
            q.filter('challenge =', models.STAN)
            q.filter('level =', avg_level)
            q.filter('unique =', False)
            npc_keys = q.fetch(100)
            logging.info(_trace+'# npc_keys = '+str(len(npc_keys)))              
            r = utils.roll(len(npc_keys), 1)
            logging.info(_trace+'r = '+str(r))  
            npc_key = npc_keys[r]
            npc = db.get(npc_key)
            for i in str(npc_party_size):
                m = models.Monster(npc = npc_key,
                                   json = character.getJSONNonPlayer(npc))
                                    
                entities.append(m)


                
        ######################################################################
        # There's one for everyone.                
        elif r == 3 or r == 4:  
            logging.info(_trace+'There\'s one for everyone!')  
            logging.info(_trace+'monster_level = '+str(monster_level[models.STAN]))
            q = db.Query(models.NonPlayerCharacter, keys_only=True)
            q.filter('challenge =', models.STAN)
            q.filter('experience =', monster_level[models.STAN])
            q.filter('level =', avg_level)
            q.filter('unique =', False)    
            logging.info(_trace+'query = '+str(q))             
            npc_keys = q.fetch(100)         
            r = utils.roll(len(npc_keys), 1)
            logging.info(_trace+'r = '+str(r))
            npc_key = npc_keys[r-1]
            npc = db.get(npc_key)
            monster_party_size = party_size
            for i in str(monster_party_size):
                m = models.Monster(npc = npc_key,
                                   json = character.getJSONNonPlayer(npc))
                                    
                entities.append(m)            

        ######################################################################        
        # Minions plus Mini-boss - oh noze!   
        elif r == 5 or r == 6:
            logging.info(_trace+'Minions + Mini-boss!')                
            boss_level = avg_level + 2        
            logging.info(_trace+'boss_level = '+boss_level)

            # Get Mini-boss
            q = db.Query(models.NonPlayerCharacter, keys_only=True)
            q.filter('challenge =', models.LEAD)
            q.filter('level =', boss_level)
            q.filter('unique =', False)            
            npc_keys = q.fetch(100)
            logging.info(_trace+'# npc_keys = '+str(len(npc_keys)))                
            r = utils.roll(len(npc_keys), 1)
            logging.info(_trace+'r = '+str(r))              
            npc_key = npc_keys[r]
            npc = db.get(npc_key)
            elite = models.Monster(npc = npc_key,
                                   json = character.getJSONNonPlayer(npc))
                                    
            entities.append(elite)            
            
            # Get Minions
            race = elite.race
            q = db.Query(models.NonPlayerCharacter, keys_only=True)
            q.filter('role =', models.MIN)
            q.filter('challenge =', models.STAN)
            q.filter('level =', avg_level)
            q.filter('unique =', False)    
            q.filter('race =', race)                      
            npc_keys = q.fetch(100)
            logging.info(_trace+'# npc_keys = '+str(len(npc_keys)))              
            r = utils.roll(len(npc_keys), 1)
            logging.info(_trace+'r = '+str(r))
            npc_key = npc_keys[r]
            npc = db.get(npc_key)

            # Get Minion XP and # of Minions for this level ...
            minion_xp = MONSTER_XP_LEVELS[avg_level][models.MIN]
            npc_party_size = party_xp/minion_xp
            logging.info(_trace+'npc_party_size = '+str(npc_party_size))

            for i in str(npc_party_size):
                m = models.Monster(npc = npc_key,
                                   json = character.getJSONNonPlayer(npc))
                                    
                entities.append(m)
                        
        ######################################################################
        # Dungeon Master party.            
        elif r == 7 or r == 8:
            logging.info(_trace+'You made the DM angry!') 
            # Return a set monster party  ...

        ######################################################################        
        # Solo boss - uh-oh.                        
        elif r == 9:  
            logging.info(_trace+'Solo boss - uh-oh!')              
            #  Randomly adjust level to create more variety ...
            if avg_level > 1:
                r = utils.roll(3, 1)
                level_mod = 0  
                if r == 1:
                    level_mod = -1
                if r == 2:
                    level_mod = 0
                if r == 3:
                    level_mod = 1             
                avg_level += level_mod        
                logging.info(_trace+'new avg_level = '+avg_level)
                                
            q = db.Query(models.NonPlayerCharacter, keys_only=True)
            q.filter('challenge =', models.SOLO)
            q.filter('level =', avg_level)
            q.filter('unique =', False)            
            npc_keys = q.fetch(100)
            r = utils.roll(len(npc_keys), 1)
            npc_key = npc_keys[r]
            npc = db.get(npc_key)
            solo = models.Monster(npc = npc_key,
                                  json = character.getJSONNonPlayer(npc))
                                
            entities.append(solo)  
     


            
        ######################################################################        
        elif r == 10: # Unique NPC.
            logging.info(_trace+'Unique NPC')
            player_party.log['encounters']['uniques'] += 1            
            q = db.Query(models.NonPlayerCharacter, keys_only=True)
            q.filter('level =', avg_level)
            q.filter('unique =', True)            
            npc_keys = q.fetch(100)
            logging.info(_trace+'# npc_keys = '+str(len(npc_keys)))              
            r = utils.roll(len(npc_keys), 1)
            logging.info(_trace+'r = '+str(r))
            npc_key = npc_keys[r]
            npc = db.get(npc_key)
            solo = models.Monster(npc = npc_key,
                                  json = character.getJSONNonPlayer(npc))
                            
            entities.append(solo)
            
            # More than 1 Player? Throw in some Minions and make it a Party!
            if party_size > 1:
                q = db.Query(models.NonPlayerCharacter, keys_only=True)
                q.filter('role =', models.MIN)
                q.filter('challenge =', models.STAN)
                q.filter('level =', avg_level)
                q.filter('unique =', False)            
                npc_keys = q.fetch(100)
                r = utils.roll(len(npc_keys), 1)
                npc_key = npc_keys[r]
                npc = db.get(npc_key)
                minion_party_size = party_size*4
                for i in minion_party_size:
                    m = modles.Monster(npc = npc_key,
                                       json = character.getJSONNonPlayer(npc))

                    entities.append(m)                    

    else:
        return None            
    
    db.put(entities) # IDs assigned

    # Need a new loop to get monster JSON after IDs are created ... 
    for e in entities:
        monster_json = monster.getJSONMonster(e)
        monster_party.json['monsters'].append(monster_json)

    parties = [player_party, monster_party]        
    db.put(parties)
    return monster_party     

def logBattle(location, loot, *characters):
    '''Stores a summary of a battle. 
    '''
    return True

######################## DATA ################################################
##############################################################################    

MONSTER_XP_LEVELS = [
    None,
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
