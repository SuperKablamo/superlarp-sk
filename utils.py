# ============================================================================
# Copyright (c) 2011, SuperKablamo, LLC.
# All rights reserved.
# info@superkablamo.com
#
# Utils.py defines the Methods for providing miscellaneous support for routine
# tasks.
#
# ============================================================================
from settings import *

import logging
import random

from google.appengine.ext import db

def roll(sides=20, number=1):
    """Returns the result of a die/dice roll.
    """
    return sum(random.randrange(1, sides+1, 1) for die in range(number))

def strToInt(s):
    """ Returns an integer formatted from a string.  Or 0, if string cannot be
    formatted.
    """
    try:
        i = int(s)
    except ValueError:
        i = 0 
    except TypeError:
        i = 0       
    return i

def parseLocation(location):
    '''Returns a GeoPt from a lat/lon String
    '''
    _trace = TRACE+'parseLocation('+str(location)+') '
    logging.info(_trace)
    s = str.split(str(location), ',')
    logging.info(_trace+'s = '+str(s))
    logging.info(_trace+'s[0] = '+str(s[0]))
    logging.info(_trace+'s[1] = '+str(s[1]))
    geo_loc = db.GeoPt(s[0], s[1])
    return geo_loc        
        
def prefetch_refprops(entities, *props):
    """Dereference Reference Properties to reduce Gets.  See:
    http://blog.notdot.net/2010/01/ReferenceProperty-prefetching-in-App-Engine
    """
    fields = [(entity, prop) for entity in entities for prop in props]
    ref_keys = [prop.get_value_for_datastore(x) for x, prop in fields]
    ref_entities = dict((x.key(), x) for x in db.get(set(ref_keys)))
    for (entity, prop), ref_key in zip(fields, ref_keys):
        prop.__set__(entity, ref_entities[ref_key])
    return entities  

