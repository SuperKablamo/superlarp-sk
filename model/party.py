# ============================================================================
# Copyright (c) 2011, SuperKablamo, LLC.
# All rights reserved.
# info@superkablamo.com
#
# party.py defines the Data and Methods for providing access to Party 
# resources as well as actions Characters can invoke, as a member of a Party,
# on other Parties and their members.
#
# ============================================================================

############################# SK IMPORTS #####################################
############################################################################## 
from utils import roll

############################# GAE IMPORTS ####################################
##############################################################################
import logging


######################## METHODS #############################################
##############################################################################
def getJSONParty(party):
    '''Returns a JSON representation of a Party.
    '''
    _trace = TRACE+'getJSONParty() '
    logging.info(_trace) 
       
    return
    
def updateJSONParty(party, *characters):
    '''Updates a Party with one or more Characters, and Returns a JSON 
    representation of the Party.
    '''
    _trace = TRACE+'updateJSONParty() '
    logging.info(_trace)
    
    return

def createJSONParty(character):       
    '''Creates a new Party for the Character, and Returns a JSON 
    representation of the Party.
    '''
    _trace = TRACE+'createJSONParty() '
    logging.info(_trace)
    
    return
    
######################## DATA ################################################
##############################################################################
