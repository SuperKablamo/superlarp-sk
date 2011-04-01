# ============================================================================
# Copyright (c) 2011, SuperKablamo, LLC.
# All rights reserved.
# info@superkablamo.com
#
# Loot.py defines the Data and Methods for providing treasure to the game
# world.
#
# ============================================================================

############################# SK IMPORTS #####################################
############################################################################## 
from utils import roll

############################# GAE IMPORTS ####################################
##############################################################################
import logging

from random import choice

######################## METHODS #############################################
##############################################################################
def loot(level):
    """Creates random loot for a level.
    {
     'coins': {'coin': 'gp', 'amount': 100}, 
     'gems': [{'gp': 100, 'type': 'Ruby'}, {'gp': 1000, 'type': 'Diamond'}],
     'item': item.json
    }
    """
    logging.info('METHOD:: loot()')
    treasure = TREASURE[level]
    loot = {'coins': None, 'gems': None, 'item': None}
    
    # Coins
    coins_roll = roll(100, 1)
    logging.info('VALUE:: coins_roll = '+str(coins_roll))
    coins = treasure['coins']
    for x in coins:
        range_ = x['range']
        logging.info('VALUE:: coin range_ = '+str(range_))
        if coins_roll <= range_:
            dice = x['dice']
            die = x['die']
            if dice > 0:
                coin = x['coin']
                base = x['base']
                multiplier = roll(die, dice) 
                amount = multiplier*base
                loot['coins'] = {'coin': coin, 'amount': amount}
    
    # Gems
    gems_roll = roll(100, 1)
    logging.info('VALUE:: gems_roll = '+str(gems_roll))
    gems = treasure['gems']
    for x in gems:   
        range_ = x['range']
        logging.info('VALUE:: gem range_ = '+str(range_))   
        if gems_roll <= range_:
            dice = x['dice']
            die = x['die']
            if dice > 0:
                number_of_gems = roll(die, dice)
                gems = []
                for i in number_of_gems:
                    gem_type_roll = roll(100, 1)
                    for g in GEMS:
                        range_ = g['range']
                        if gem_type_roll <= range_:
                            gem_value = roll(g['dice'], g['die'])
                            gem_value = gem_value*g['base']
                            gem_type = choice(g['gem'])
                            gem = {'gp': gem_value, 'type': gem_type}
                            gems.append(gem)
                
                loot['gems'] = gems
                           
    # Item
    items_roll = roll(100, 1)
    logging.info('VALUE:: items_roll = '+str(items_roll))
    items = treasure['items']
    for x in items:       
        range_ = x['range']
        logging.info('VALUE:: items range_ = '+str(range_))   
        if items_roll <= range_:    
            dice = x['dice']
            die = x['die']
            if dice > 0:
                item_level_mod = roll(die, dice)
                item_level = item_level_mod + level - 1
                item_class_roll = roll(100, 1)
                item_class = None
                if item_class_roll <= 30:
                    item_class = models.Weapon
                elif item_class_roll <= 50:
                    item_class = models.Armor                                        
                elif item_class_roll <= 80:
                    item_class = models.Potion
                elif item_class_roll <= 90:
                    item_class = models.Implement                 
                elif item_class_roll <= 95:
                    item_class = models.Gear
                elif item_class_roll <= 99:
                    item_class = models.Artifact                                                            
                elif item_class_roll <= 100:
                    item_class = models.Ring
                
                query = item_class.all()
                query.filter('level =', item_level)
                item_choices = query.fetch(1000)
                random_item = choice(item_choices)
                loot['item'] = random_item.json
                                    
    return loot            


######################## DATA ################################################
##############################################################################
TREASURE = [
    {'1': { 
        'coins': [ 
            {'range': 14, 'dice': 0, 'die': 0, 'coin': '', 'base': 0},
            {'range': 29, 'dice': 1, 'die': 6, 'coin': 'cp', 'base': 1000},
            {'range': 52, 'dice': 1, 'die': 8, 'coin': 'sp', 'base': 100},
            {'range': 95, 'dice': 2, 'die': 8, 'coin': 'gp', 'base': 10},
            {'range': 100, 'dice': 1, 'die': 4, 'coin': 'pp', 'base': 10}                                                
            ],
        'gems': [
            {'range': 90, 'dice': 0, 'die': 0},
            {'range': 95, 'dice': 1, 'die': 1},
            {'range': 100, 'dice': 1, 'die': 2}        
            ],
        'items': [ # Die roll determines level modifier for item
            {'range': 71, 'dice': 0, 'die': 0},
            {'range': 95, 'dice': 1, 'die': 1},
            {'range': 100, 'dice': 1, 'die': 2},        
            ]
        }        
    },
    {'2': {
        'coins': [
            {'range': 13, 'dice': 0, 'die': 0, 'coin': '', 'base': 0},
            {'range': 23, 'dice': 1, 'die': 10, 'coin': 'cp', 'base': 1000},
            {'range': 43, 'dice': 2, 'die': 10, 'coin': 'sp', 'base': 100},
            {'range': 95, 'dice': 4, 'die': 10, 'coin': 'gp', 'base': 10},
            {'range': 100, 'dice': 2, 'die': 8, 'coin': 'pp', 'base': 10}                                                
            ],
        'gems': [
            {'range': 81, 'dice': 0, 'die': 0},
            {'range': 95, 'dice': 1, 'die': 3},
            {'range': 100, 'dice': 1, 'die': 4}        
            ],
        'items': [
            {'range': 49, 'dice': 0, 'die': 0},
            {'range': 85, 'dice': 1, 'die': 1},
            {'range': 100, 'dice': 1, 'die': 2},        
            ]    
        }
    },
    {'3': {
        'coins': [
            {'range': 11, 'dice': 0, 'die': 0, 'coin': '', 'base': 0},
            {'range': 21, 'dice': 2, 'die': 10, 'coin': 'cp', 'base': 1000},
            {'range': 41, 'dice': 4, 'die': 8, 'coin': 'sp', 'base': 100},
            {'range': 95, 'dice': 1, 'die': 4, 'coin': 'gp', 'base': 100},
            {'range': 100, 'dice': 1, 'die': 10, 'coin': 'pp', 'base': 10}                                                
            ],
        'gems': [
            {'range': 77, 'dice': 0, 'die': 0},
            {'range': 95, 'dice': 1, 'die': 3},
            {'range': 100, 'dice': 1, 'die': 4}        
            ],
        'items': [
            {'range': 49, 'dice': 0, 'die': 0},
            {'range': 79, 'dice': 1, 'die': 2},
            {'range': 100, 'dice': 1, 'die': 3},
            ]    
        }
    },
    {'4': {
        'coins': [
            {'range': 11, 'dice': 0, 'die': 0, 'coin': '', 'base': 0},
            {'range': 21, 'dice': 3, 'die': 10, 'coin': 'cp', 'base': 1000},
            {'range': 41, 'dice': 4, 'die': 12, 'coin': 'sp', 'base': 1000},
            {'range': 95, 'dice': 1, 'die': 6, 'coin': 'gp', 'base': 100},
            {'range': 100, 'dice': 1, 'die': 8, 'coin': 'pp', 'base': 10}                                                
            ],
        'gems': [
            {'range': 70, 'dice': 0, 'die': 0},
            {'range': 95, 'dice': 1, 'die': 4},
            {'range': 100, 'dice': 1, 'die': 5}        
            ],
        'items': [
            {'range': 42, 'dice': 0, 'die': 0},
            {'range': 62, 'dice': 1, 'die': 2},
            {'range': 100, 'dice': 1, 'die': 3},        
            ]    
        }
    },
    {'5': {
        'coins': [
            {'range': 10, 'dice': 0, 'die': 0, 'coin': '', 'base': 0},
            {'range': 19, 'dice': 1, 'die': 4, 'coin': 'cp', 'base': 10000},
            {'range': 38, 'dice': 1, 'die': 6, 'coin': 'sp', 'base': 1000},
            {'range': 95, 'dice': 1, 'die': 8, 'coin': 'gp', 'base': 100},
            {'range': 100, 'dice': 1, 'die': 10, 'coin': 'pp', 'base': 10}                                                
            ],
        'gems': [
            {'range': 60, 'dice': 0, 'die': 0},
            {'range': 95, 'dice': 1, 'die': 4},
            {'range': 100, 'dice': 1, 'die': 5}        
            ],
        'items': [
            {'range': 57, 'dice': 0, 'die': 0},
            {'range': 67, 'dice': 1, 'die': 2},
            {'range': 100, 'dice': 1, 'die': 3},        
            ]    
        }
    },
    {'6': {
        'coins': [
            {'range': 10, 'dice': 0, 'die': 0, 'coin': '', 'base': 0},
            {'range': 18, 'dice': 1, 'die': 6, 'coin': 'cp', 'base': 10000},
            {'range': 37, 'dice': 1, 'die': 8, 'coin': 'sp', 'base': 1000},
            {'range': 95, 'dice': 1, 'die': 10, 'coin': 'gp', 'base': 100},
            {'range': 100, 'dice': 1, 'die': 12, 'coin': 'pp', 'base': 10}                                                
            ],
        'gems': [
            {'range': 56, 'dice': 0, 'die': 0},
            {'range': 92, 'dice': 1, 'die': 4},
            {'range': 100, 'dice': 1, 'die': 5}        
            ],
        'items': [
            {'range': 54, 'dice': 0, 'die': 0},
            {'range': 59, 'dice': 1, 'die': 2},
            {'range': 99, 'dice': 1, 'die': 3},    
            {'range': 100, 'dice': 1, 'die': 4},             
            ]    
        }
    },                                
    {'7': {
        'coins': [
            {'range': 11, 'dice': 0, 'die': 0, 'coin': '', 'base': 0},
            {'range': 18, 'dice': 1, 'die': 10, 'coin': 'cp', 'base': 10000},
            {'range': 35, 'dice': 1, 'die': 12, 'coin': 'sp', 'base': 1000},
            {'range': 93, 'dice': 2, 'die': 6, 'coin': 'gp', 'base': 100},
            {'range': 100, 'dice': 3, 'die': 4, 'coin': 'pp', 'base': 10}                                                
            ],
        'gems': [
            {'range': 48, 'dice': 0, 'die': 0},
            {'range': 88, 'dice': 1, 'die': 4},
            {'range': 100, 'dice': 1, 'die': 5}        
            ],
        'items': [
            {'range': 51, 'dice': 0, 'die': 0},
            {'range': 97, 'dice': 1, 'die': 3},
            {'range': 100, 'dice': 1, 'die': 4},        
            ]    
        }
    },
    {'8': {
        'coins': [
            {'range': 10, 'dice': 0, 'die': 0, 'coin': '', 'base': 0},
            {'range': 15, 'dice': 1, 'die': 12, 'coin': 'cp', 'base': 10000},
            {'range': 29, 'dice': 2, 'die': 6, 'coin': 'sp', 'base': 1000},
            {'range': 87, 'dice': 2, 'die': 8, 'coin': 'gp', 'base': 100},
            {'range': 100, 'dice': 3, 'die': 6, 'coin': 'pp', 'base': 10}                                                
            ],
        'gems': [
            {'range': 45, 'dice': 0, 'die': 0},
            {'range': 85, 'dice': 1, 'die': 6},
            {'range': 100, 'dice': 1, 'die': 7}        
            ],
        'items': [
            {'range': 48, 'dice': 0, 'die': 0},
            {'range': 96, 'dice': 1, 'die': 3},
            {'range': 100, 'dice': 1, 'die': 4},        
            ]    
        }
    }] 

GEMS = [
        {'range': 25, 'dice': 4, 'die': 4, 'base': 1,  
        'gem': ['Moss Agate', 'Blue Quartz', 'Hematite', 'Lapis Lazuli', 
               'Malachite', 'Obsidian', 'Tiger Eye Turquoise', 'Rose', 'Pearl']    
        },
        {'range': 50, 'dice': 2, 'die': 4, 'base': 10,  
        'gem': ['Bloodstone', 'Carnelian', 'Rock Crystal', 'Citrine', 'Iolite',
               'Jasper', 'Moonstone', 'Onyx', 'Peridot', 'Star Rose Quartz',
               'Zircon']    
        },
        {'range': 70, 'dice': 4, 'die': 4, 'base': 10,  
        'gem': ['Amber', 'Amethyst', 'Chrysoberyl', 'Coral', 'Jade', 
               'Golden Pearl', 'Pink Pearl', 'Silver Pearl', 'Red Garnet']    
        },
        {'range': 90, 'dice': 2, 'die': 4, 'base': 100,  
        'gem': ['Alexandrite', 'Aquamarine', 'Violet Garnet', 'Black Pearl',
               'Deep Blue Spinel', 'Golden Yellow Topaz']    
        },
        {'range': 99, 'dice': 4, 'die': 4, 'base': 100,  
        'gem': ['Emerald', 'White Opal', 'Black Opal', 'Fire Opal', 
               'Blue Sapphire', 'Blue Star Sapphire', 'Star Ruby']    
        },
        {'range': 100, 'dice': 2, 'die': 4, 'base': 1000,  
        'gem': ['Clearest Bright Green Emerald', 'Blue Diamond', 
               'Canary Diamond', 'Pink Diamond', 'Brown Diamond', 
               'White Diamond', 'Jacinth']    
        }
    ]