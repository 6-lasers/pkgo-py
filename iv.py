#!/usr/bin/env python
######################################################
#
#    iv.py
#
#  Calculate IVs
#
#  Usage: iv.py <input.txt> <directory with Pokemon Go data files>
#
######################################################

import os
import sys
import optparse
import math
import json

import yaml

# pkmn has:
# hp, cp, IVs, species, base stats, definite level
# appraisal has:
# hp, cp, species, base stats, level range, hmin/max, imin, gmin/max

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

# Max IV is 15
maxIV = 15

# Calculate CP
def calcCP(sta, atk, defe, lvl):
    cpm = levelToCpm[str(lvl)]
    return int(max(10, math.floor(atk * math.pow(defe, 0.5) * math.pow(sta, 0.5) * math.pow(cpm, 2) / 10)))

# Calculate HP
def calcHP(sta, lvl):
    cpm = levelToCpm[str(lvl)]
    return int(max(10, math.floor(cpm * sta)))

def PKMNToStr(pk):
    ivsum = pk['ivsta'] + pk['ivatk'] + pk['ivdef']
    return "Level {0}, IVs {1:2}, {2:2}, {3:2}, total {4:2} ({5:.1%}) ({1:x}{2:x}{3:x})".format(pk['level'], pk['ivsta'], pk['ivatk'], pk['ivdef'], ivsum, ivsum / 45.0)

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
def matchApprIVs(appr, baseStats):
    basesta, baseatk, basedef = tuple(baseStats[appr['spec']])
    
    # Array of possible Pokemon
    pkarr = []
    
    for level in appr['levels']:
        # Brute force
        for ivsta in range(appr['imin'], maxIV + 1):
            # Quick exit if STA value doesn't match HP
            ehp = calcHP(basesta + ivsta, level)
            if ehp == int(appr['hp']):
                for ivatk in range(appr['imin'], maxIV + 1):
                    for ivdef in range(appr['imin'], maxIV + 1):
                        # Exit if appraisal sanity check fails
                        if not checkIVsFitAppr(appr, ivsta, ivatk, ivdef):
                            continue
                        
                        ecp = calcCP(basesta + ivsta, baseatk + ivatk, basedef + ivdef, level)
                        
                        # Exit if IV's don't match CP
                        if ecp == int(appr['cp']):
                            ivsum = ivsta + ivatk + ivdef
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
# <name> <iv> <hp> <power up cost (in 100s)> <overall appraisal> <highest stat appraisal> <highest stat type> <(optional) hatched/powered>
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
    appr['levels'] = dustJson[cost]
    # Filter out half-levels if not powered up
    if not flags or 'p' not in flags:
        appr['levels'] = filter(lambda x:isinstance(x,int), appr['levels'])
    
    # If hatched
    if flags and 'h' in flags:
        # and not powered up, level is 20
        if 'p' not in flags:
            appr['levels'] = ["20"]
        # Hatched IVs cannot be lower than 10
        appr['hmin'] = max(10, appr['hmin'])
        appr['imin'] = 10
    
    return appr

def main(argv=None):
    usage="Usage: iv.py <input.txt> <directory with Pokemon Go data files>"
    parser = optparse.OptionParser(usage=usage)
    
    (options, args) = parser.parse_args()
    
    # Get arguments
    try:
        inputFileName, dataDir = args
    except ValueError:
        print "ERROR: Invalid number of arguments"
        print usage
        return 1
    
    baseStatsName = os.path.join(dataDir, "baseStats.yml")
    dustJsonName = os.path.join(dataDir, "dust-to-level.json")
    levelToCpmName = os.path.join(dataDir, "level-to-cpm.json")
    
    global baseStats
    global dustJson
    global levelToCpm
    
    baseStatsFile = open(baseStatsName, "r")
    baseStats = yaml.load(baseStatsFile)
    baseStatsFile.close()
    
    dustJsonFile = open(dustJsonName, "r")
    dustJson = json.load(dustJsonFile)
    dustJsonFile.close()
    
    levelToCpmFile = open(levelToCpmName, "r")
    levelToCpm = json.load(levelToCpmFile)
    levelToCpmFile.close()
    
    
    inputFile = open(inputFileName, "r")
    lines = inputFile.readlines()
    inputFile.close()
    
    cnt = 1
    for line in lines:
        # Skip empty lines, comments
        if line == "\n" or line[0] == "#":
            continue
        
        # Convert lines to appraisals
        appr = lineToAppr(line)
        
        # Check IVs for each appraisal
        print "PKMN {0} ({1} CP {2}):".format(cnt, appr['spec'], appr['cp'])
        pkarr = matchApprIVs(appr, baseStats)
        for pk in pkarr:
            print "Possible match: {0}".format(PKMNToStr(pk))
        
        cnt += 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

