######################################################
#
#    pkgo_appraise.py
#
#  Libraries for handling Pokemon Go appraisals.
#
######################################################

import math

import pkgo_data
import pkgo_pkmn


# appraisal objects have the following fields:
# hp, cp, species, base stats, level range, hmin/max (highest IV min/max), imin (IV minimum), gmin/max (total IV min/max)

# Appraisal numbers (overall):
#  0-22 "not likely to make headway"
# 23-29 "above average"
# 30-36 "caught my attention
# 37-45 "is a wonder"
gappToMin = [0, 23, 30, 37, 46]
# Appraisal numbers (individual stat):
#  0- 7 "not out of the norm"
#  8-12 "trending to the positive"
# 13-14 "certainly impressed"
#    15 "exceeds my calculations"
happToMin = [0, 8, 13, 15, 16]


# Sanity check that chosen IVs fit the appraisal
def checkIVsFitAppr(appr, ivsta, ivatk, ivdef):
    highstat_map = dict({
        'h': ivsta,
        'a': ivatk,
        'd': ivdef
    })
    
    # Exit if appraisal total check fails
    ivsum = ivsta + ivatk + ivdef
    if ivsum < appr['gmin'] or ivsum >= appr['gmax']:
        return False
    
    hi_val = -1
    for stat in appr['high']:
        # Initialize high value
        if hi_val == -1:
            hi_val = highstat_map[stat]
        # Check all high values equal
        if hi_val != highstat_map[stat]:
            return False
        # Check high values within range
        if hi_val < appr['hmin'] or hi_val >= appr['hmax']:
            return False
    
    # Check non-high values less than high value
    for stat in highstat_map:
        if stat not in appr['high'] and highstat_map[stat] >= hi_val:
            return False
    
    return True

# Match IV values for an appraisal,
# and return an array of possible Pokemon
def matchApprIVs(appr):
    # Array of possible Pokemon
    pkarr = []
    
    basesta, baseatk, basedef = tuple(pkgo_data.baseStats[appr['spec']])
    
    for level in appr['levels']:
        # Brute force
        for ivsta in range(appr['imin'], pkgo_pkmn.maxIV + 1):
            # Quick exit if STA value doesn't match HP
            ehp = pkgo_pkmn.calcHP(basesta + ivsta, level)
            if ehp == int(appr['hp']):
                for ivatk in range(appr['imin'], pkgo_pkmn.maxIV + 1):
                    for ivdef in range(appr['imin'], pkgo_pkmn.maxIV + 1):
                        # Exit if appraisal sanity check fails
                        if not checkIVsFitAppr(appr, ivsta, ivatk, ivdef):
                            continue
                        
                        ecp = pkgo_pkmn.calcCP(basesta + ivsta, baseatk + ivatk, basedef + ivdef, level)
                        
                        # Exit if IV's don't match CP
                        if ecp == int(appr['cp']):
                            pkarr.append(dict({
                                'hp': appr['hp'],
                                'cp': appr['hp'],
                                'spec': appr['spec'],
                                'level': level,
                                'ivsta': ivsta,
                                'ivatk': ivatk,
                                'ivdef': ivdef,
                            }))
    return pkarr

# Convert a line of text to an appraisal. Format is:
# <name> <iv> <hp> <power up cost (in 100s)> <overall appraisal> <highest stat type> <highest stat appraisal> <(optional) hatched/powered>
def lineToAppr(line):
    splitline = line.split()
    
    appr = dict({})
    
    # Check if flags is present as it is optional
    flags = ""
    
    try:
        appr['spec'], appr['cp'], appr['hp'], cost, gapp, appr['high'], happ = tuple(splitline)
    except:
        appr['spec'], appr['cp'], appr['hp'], cost, gapp, appr['high'], happ, flags = tuple(splitline)
    
    # Capitalize species name
    appr['spec'] = appr['spec'].capitalize()
    # Normalize dust cost
    cost = str(int(cost) * 100)
    
    # Determine appraisal minimums and maximums.
    # 'gmin/gmax' refer to the Pokemon's overall quality in appraisal ("is a wonder!")
    # 'hmin/hmax' refer to the 'best attribute' mentioned in appraisal ("stats exceed my calculations")
    appr['gmin'] = gappToMin[int(gapp)]
    appr['gmax'] = gappToMin[int(gapp) + 1]
    appr['hmin'] = happToMin[int(happ)]
    appr['hmax'] = happToMin[int(happ) + 1]
    # By default, IVs can be as low as 0
    appr['imin'] = 0
    
    # Find possible levels
    appr['levels'] = pkgo_data.dustJson[cost]
    # Filter out half-levels if not powered up
    if not flags or 'p' not in flags:
        appr['levels'] = filter(lambda x:x.is_integer(), appr['levels'])
    
    # If hatched
    if flags and 'h' in flags:
        # and not powered up, level is 20
        if 'p' not in flags:
            appr['levels'] = ["20.0"]
        # Hatched IVs cannot be lower than 10
        appr['hmin'] = max(10, appr['hmin'])
        appr['imin'] = 10
    
    return appr

