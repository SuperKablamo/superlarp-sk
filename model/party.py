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
import models
import rules

from settings import *
from utils import roll

############################# GAE IMPORTS ####################################
##############################################################################
import logging

from google.appengine.ext import db

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

def createJSONParty(character, location):       
    '''Creates a new Party for the Character, and Returns a JSON 
    representation of the Party.
    '''
    _trace = TRACE+'createJSONParty() '
    logging.info(_trace)
    log = {'encounters': 
           {'total': 0, 'uniques': 0, 'start_time': POSIX
            'last_encounter': {'time_since': POSIX, 'checks': 0}}}
            
    party = models.PlayerParty(location = location,
                               leader = character,
                               members = [character.key()],
                               log = log)
    
    updates = [party,character]
    db.put(updates)
    json = {'key': str(party.key()), 'leader_key': str(party.leader.key()), 
            'location': str(location), 'members': [str(party.leader.key())]}
                         
    return json

def getJSONQuest(party, player, geo_loc):
    '''Returns any events, parties, and traps found at the PlayerParties 
    location.
    '''
    quest = rules.rollEncounter(party, geo_loc)
    return quest 
    
######################## DATA ################################################
##############################################################################
