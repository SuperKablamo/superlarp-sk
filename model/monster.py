# ============================================================================
# Copyright (c) 2011, SuperKablamo, LLC.
# All rights reserved.
# info@superkablamo.com
#
# monster.py 
# ============================================================================

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

######################## METHODS #############################################
##############################################################################
def getMonsterJSON(monster):
    logging.info(TRACE+'getMonsterJSON()')
    json = monster.json
    json['id'] = monster.key().id()
    json['npc_id'] = monster.npc.key().id()
    return json