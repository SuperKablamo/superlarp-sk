# ============================================================================
# Copyright (c) 2011, SuperKablamo, LLC.
# All rights reserved.
# info@superkablamo.com
#
#
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
    Result is a dictionary: {} 

    """   
    return loot.loot(level)    
    
def rollAttack(attacker, defender, weapon):
    """Resolves an attack and returns the damage result as a dictionary:
    {'damage': 10, type: 'Fire'}
    """    
    
    return damage

    