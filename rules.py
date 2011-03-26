#
# Copyright 2010 SuperKablamo, LLC
# info@superkablamo.com
#

############################# SK IMPORTS #####################################
############################################################################## 

from settings import *

############################# GAE IMPORTS ####################################
##############################################################################
import logging

from random import randrange

######################## METHODS #############################################
##############################################################################
def roll(sides=20, number=1):
    """Returns the result of a die/dice roll.
    """
    return sum(randrange(sides)+1 for die in range(number))
    
def rollLoot(level=1): 
    """Returns a randomly generated, level appropriate treasure package as a 
    JSON Result.
    """   
    r = roll(100, 1)
    
    
    
    return loot

def rollAttack(attacker, defender, weapon):
    """Resolves an attack and returns the damage result as a dictionary:
    {'damage': 10, type: 'Fire'}.
    """    
    
    return damage

    