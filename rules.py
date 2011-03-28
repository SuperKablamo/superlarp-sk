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
import loot

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

def rollPerception(player, location):
    """Checks for any NPCs or PCs that the player can perceive.  Returns a 
    list of 0 or more characters as a dictionary.
    """
    return result     

def logBattle(*characters, location, loot):
    """Stores a summary of a battle. 
    """
    return True
    