#
# Copyright 2010 SuperKablamo, LLC
# info@superkablamo.com
#

############################# SK IMPORTS #####################################
############################################################################## 
import models
import utils

from settings import *

############################# GAE IMPORTS ####################################
##############################################################################
import os
import logging

from django.utils import simplejson
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

############################# REQUEST HANDLERS ############################### 
##############################################################################
class APIPlayer(webapp.RequestHandler):
    """Provides API access to Player Character data.  Responses are in JSON.
    """
    def get(self, method):
        logging.info('################### APIPlayer:: get() ################')
    
    def post(self, method):
        logging.info('################## APIPlayer:: post() ################')
        if method == "new": 
            r = createPlayer(self)
        else: r = API404
        return self.response.out.write(simplejson.dumps(r)) 

class APIError(webapp.RequestHandler):
    """Provides basic API error Response in JSON.
    """
    def get(self, foo):
        r = API404
        return self.response.out.write(simplejson.dumps(r)) 

    def post(self, foo):
        r = API404
        return self.response.out.write(simplejson.dumps(r)) 
               
######################## METHODS #############################################
##############################################################################
def createPlayer(self):
    """Creates a new Player Character and returns that character as a JSON
    Response.
    """
    logging.info('###################### createPlayer() ####################')    
    # Build the basic data format for scores and fill base values ...
    abilities = buildScores(self, models.ABILITIES_KEY, models.ABILITY_KEYS)
    skills = buildScores(self, models.SKILLS_KEY, models.SKILL_KEYS)
    defenses = buildScores(self, models.DEFENSES_KEY, models.DEFENSE_KEYS)
    scores = {'abilities': abilities, 'skills': skills, 'defenses': defenses}

    # Update score data with Race and Cast bonuses ...
    race = models.Race.get_by_key_name(self.request.get('race'))
    cast = models.Cast.get_by_key_name(self.request.get('cast'))    
    abilities = addBonuses(self, scores, models.ABILITIES_KEY,
                           race.bonuses, cast.bonuses)    
    skills = addBonuses(self, scores, models.SKILLS_KEY, 
                        race.bonuses, cast.bonuses)  
    defenses = addBonuses(self, scores, models.DEFENSES_KEY, 
                          race.bonuses, cast.bonuses)
    
    player = models.Player(name = self.request.get('name'),
                           level = 1,
                           race = self.request.get('race'),
                           cast = self.request.get('cast'),
                           alignment = self.request.get('alignment'),
                           hit_points = hp,
                           height = self.request.get('height'),
                           weight = self.request.get('weight'),
                           scores = scores)

def buildScores(self, cat_key, attr_keys):
    scores = {}
    for a in attr_keys:
        score = {'score': self.request.get(a), 'mod': 0, 'bonuses': None}
        scores[a] = score
    return scores
    
def addMods(self, scores, cat_key, *mods):
    for m in mods: # Loop through each List of mods ...
        for c in cat_key: # Loop through each category in mod List ...
            if m.c: # If there are mods for that category ...
                for mod in m.c: # Loop through those mods ...
                    name = mod.origin
                    type_ = mod.type
                    mod = mod.mod
                    scores.c.type_.mods.push({'origin':origin, 
                                              'mod': mod, 
                                              'type': type_})

                    total_mod = scores.c.type_.mod
                    total_mod =+ mod
                    scores.c.type_['mod'] = total_mod                 
    
    return scores
                
##############################################################################
##############################################################################
application = webapp.WSGIApplication([(r'/api/character/player/(.*)', APIPlayer),
                                      (r'/api/character/nonplayer/(.*)', APINonPlayer),
                                      (r'/api/(.*)', APIError)
                                     ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
