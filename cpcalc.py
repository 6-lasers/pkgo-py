#!/usr/bin/env python
######################################################
#
#    cpcalc.py
#
#  Calculate CP of a Pokemon species with the given level and IVs.
#
#  Usage: cpcalc.py <input.txt>
#
######################################################

import os
import sys
import optparse
import json

import pkgo_data
import pkgo_pkmn
import pkgo_appraise

# Append path of this script to the path of
# config files which we're loading.
# Assumes that config files will always live in the same directory.
dataDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "gameData")

def main(argv=None):
    usage="Usage: cpcalc.py <input.txt>"
    parser = optparse.OptionParser(usage=usage)
    
    (options, args) = parser.parse_args()
    
    # Get arguments
    try:
        inputFileName, = args
    except ValueError:
        print "ERROR: Invalid number of arguments"
        print usage
        return 1
    
    baseStatsName = os.path.join(dataDir, "baseStats.json")
    dustJsonName = os.path.join(dataDir, "dust-to-level.json")
    levelToCpmName = os.path.join(dataDir, "level-to-cpm.json")
    candyJsonName = os.path.join(dataDir, "level-to-candy.json")
    
    baseStatsFile = open(baseStatsName, "r")
    pkgo_data.baseStats = json.load(baseStatsFile)
    baseStatsFile.close()
    
    dustJsonFile = open(dustJsonName, "r")
    pkgo_data.dustJson = json.load(dustJsonFile)
    dustJsonFile.close()
    
    levelToCpmFile = open(levelToCpmName, "r")
    pkgo_data.levelToCpm = json.load(levelToCpmFile)
    levelToCpmFile.close()
    
    candyJsonFile = open(candyJsonName, "r")
    candyJson = json.load(candyJsonFile)
    candyJsonFile.close()
    
    inputFile = open(inputFileName, "r")
    lines = inputFile.readlines()
    inputFile.close()
    
    cnt = 1
    for line in lines:
        # Skip empty lines, comments
        if line == "\n" or line[0] == "#":
            continue
        
        # Convert lines to PKMN
        pk = {}
        
        start_lvl = None
        
        try:
            pk = pkgo_pkmn.PKMNFromStr(line)
        except:
            splitline = line.split()
            pk = pkgo_pkmn.PKMNFromStr(" ".join(splitline[:-1]))
            start_lvl = splitline[-1]
        
        pk['cp'] = pkgo_pkmn.calcCPForPKMN(pk)
        pk['hp'] = pkgo_pkmn.calcHPForPKMN(pk)
        
        # Check IVs for each appraisal
        print "PKMN {0} (Lvl. {1} {2} CP {3} HP {4})".format(cnt, pk['level'], pk['spec'], pk['cp'], pk['hp'])
        if start_lvl:
            dustCost = 0
            candyCost = 0
            
            reverseDustJson = dict()
            for cost in pkgo_data.dustJson:
                for level in pkgo_data.dustJson[cost]:
                    reverseDustJson[level] = int(cost)
            
            tmpLvl = float(start_lvl)
            while tmpLvl != pk['level']:
                dustCost += reverseDustJson[tmpLvl]
                candyCost += candyJson[str(tmpLvl)]
                tmpLvl += 0.5
            
            print "To level from {0} to {1}, you need:".format(start_lvl, pk['level'])
            print "{0} dust and {1} candies.".format(dustCost, candyCost)
        
        cnt += 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

