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

    