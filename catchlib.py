######################################################
#
#    catchlib.py
#
#  Library that supplies functions for
#  calculating catch rates.
#
######################################################

import math
import json
import distutils.util

global levelToCpm
global catchRate
levelToCpm = None
catchRate = None

def parse_ball_type(ball_type):
    # Try to understand ball type.
    
    # Premier ball == regular ball.
    # Also accept words like "regular" or "normal"
    if ball_type.lower() == "regular" or ball_type.lower() == "normal" or "poke" in ball_type.lower() or "premier" in ball_type.lower():
        ball_index = 0
    elif "great" in ball_type.lower():
        ball_index = 1
    elif "ultra" in ball_type.lower():
        ball_index = 2
    else:
        try:
            # If that didn't work, test if they gave us the ball type directly as an int
            ball_index = int(ball_type)
        except:
            print "Couldn't understand ball type \"{0}\"!".format(ball_type)
            sys.exit(1)
    
    return ball_index

def parse_berry_type(berry_type):
    # Try to understand berry type.
    
    # Indicate no berry with words like "none" or "no"
    if berry_type.lower() == "pinap" or berry_type.lower() == "pinap berry" or berry_type.lower() == "nanab" or berry_type.lower() == "nanab berry" or berry_type.lower() == "none" or berry_type.lower() == "no":
        berry_index = 0
    elif berry_type.lower() == "razz" or berry_type.lower() == "razz berry":
        berry_index = 1
    elif berry_type.lower() == "grb" or berry_type.lower() == "golden razz" or berry_type.lower() == "golden razz berry":
        berry_index = 2
    else:
        try:
            # If that didn't work, test if they gave us the berry type directly as an int
            berry_index = int(berry_type)
        except:
            print "Couldn't understand berry type \"{0}\"!".format(berry_type)
            sys.exit(1)
    
    return berry_index

def calcCatch(base, level, throw_type, ball, berry, curve, medal, ball_count, can_flee):
    global levelToCpm
    global catchRate
    
    if not levelToCpm:
        levelToCpmName = "level-to-cpm.json"
        
        levelToCpmFile = open(levelToCpmName, "r")
        levelToCpm = json.load(levelToCpmFile)
        levelToCpmFile.close()
    
    if not catchRate:
        catchRateName = "catch_flee.json"
        
        catchRateFile = open(catchRateName, "r")
        catchRate = json.load(catchRateFile)
        catchRateFile.close()
    
    # Translate 'base' if it is a Pokemon species name.
    # Otherwise, assume it's a catch rate as a float
    try:
        base = catchRate[base.capitalize()]['catch'] / 100.0
    except KeyError:
        base = float(base)
    
    # Parse ball type.
    ball_index = parse_ball_type(ball)
    
    # Parse berry type.
    berry_index = parse_berry_type(berry)
    
    level = float(level)
    
    # Interpret curve argument as a boolean
    curve = distutils.util.strtobool(curve)
    
    # 0 - No medal
    # 1 - Bronze
    # 2 - Silver
    # 3 - Gold
    # For mixed-type Pokemon, average out the two medals.
    # e.g. Articuno with gold flying and silver ice medal is 2.5
    medal = float(medal)
    
    ball_count = int(ball_count)
    
    # Interpret can_flee argument as a string
    # representation of a boolean, if necessary
    try:
        can_flee = distutils.util.strtobool(can_flee)
    except:
        pass
    
    # Convert throw type into a radius.
    # If type is a string, try to match it
    # to the game's types (use the radius for each modifier)
    
    # 'none' throw (meaning you missed the circle)
    # counts as 1.0 radius
    if throw_type.lower() == "none":
        radius = 1.0
    # 'nice' throw is over 0.7 radius
    elif throw_type.lower() == "nice":
        radius = 0.85
    # 'great' throw is 0.7-0.3 radius
    elif throw_type.lower() == "great":
        radius = 0.50
    # 'excellent' throw is under 0.3 radius
    elif throw_type.lower() == "excellent":
        radius = 0.15
    else:
        try:
            # If that didn't work, test if they gave us the radius directly as a float
            radius = float(throw_type)
        except:
            print "Couldn't understand throw type \"{0}\"!".format(throw_type)
            sys.exit(1)
    
    cpm = levelToCpm[str(level)]
    
    # Ball multipliers (normal, great, ultra)
    ball_multi = [1.0, 1.5, 2.0]
    # Berry multipliers (none, razz, grb)
    berry_multi = [1.0, 1.5, 2.5]
    # Curve ball has 1.7 multiplier
    curve_multi = 1.0 if curve == 0 else 1.7
    # Medal bonus
    medal_multi = 1.0 + (medal / 10)
    
    # Throw multiplier
    throw_multi = 2.0 - radius
    
    # Calculate final multipliers and catch rate for the throw
    multi = ball_multi[ball_index] * berry_multi[berry_index] * throw_multi * curve_multi * medal_multi
    catch = 1 - math.pow(1 - (base / (2 * cpm)), multi)
    cumu_catch = (1 - math.pow(1 - catch, ball_count))
    
    return catch, cumu_catch

