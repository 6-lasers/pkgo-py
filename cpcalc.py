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

from __future__ import print_function

import os
import sys
import argparse
import json

import pkgo_data
import pkgo_pkmn
import pkgo_appraise

# Append path of this script to the path of
# config files which we're loading.
# Assumes that config files will always live in the same directory.
dataDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "gameData")

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="text file containing CP information")
    parser.add_argument("--power", action="store_true", help="find power up needed to narrow")
    
    args = parser.parse_args()
    
    inputFileName = args.file
    
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
    
    pks = []
    
    cnt = 1
    for line in lines:
        # Skip empty lines, comments
        if line == "\n" or line[0] == "#":
            continue
        
        # Convert lines to PKMN
        pk = {}
        
        start_lvl = None
        
        #print(line.split())
        pk = pkgo_pkmn.PKMNFromStr(line)
        # try:
            # pk = pkgo_pkmn.PKMNFromStr(line)
        # except:
            # splitline = line.split()
            # pk = pkgo_pkmn.PKMNFromStr(" ".join(splitline[:-1]))
            # start_lvl = splitline[-1]
        
        pk['cp'] = pkgo_pkmn.calcCPForPKMN(pk, True)
        pk['hp'] = pkgo_pkmn.calcHPForPKMN(pk)
        
        # Check IVs for each appraisal
        print("PKMN {0} (Lvl. {1} {2} CP {3} HP {4})".format(cnt, pk['level'], pk['spec'], pk['cp'], pk['hp']))
        print("(ATK {0} DEF {1})".format(pkgo_pkmn.calcATKForPKMN(pk), pkgo_pkmn.calcDEFForPKMN(pk)))
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
            
            print("To level from {0} to {1}, you need:".format(start_lvl, pk['level']))
            print("{0} dust and {1} candies.".format(dustCost, candyCost))
        
        pks.append(pk)
        cnt += 1
    
    if args.power:
        locked_pks = []
        while True:
            seen = set()
            if not any((pk['hp'], pk['cp']) in seen or seen.add((pk['hp'], pk['cp'])) for pk in pks):
                break
            for pk in pks:
                pk['level'] += 0.5
                pk['cp'] = pkgo_pkmn.calcCPForPKMN(pk)
                pk['hp'] = pkgo_pkmn.calcHPForPKMN(pk)
        """
        while True:
            first = pks[0]
            if not all(first['cp'] == pk['cp'] and first['hp'] == pk['hp'] for pk in pks):
                break
            for pk in pks:
                pk['level'] += 0.5
                pk['cp'] = pkgo_pkmn.calcCPForPKMN(pk)
                pk['hp'] = pkgo_pkmn.calcHPForPKMN(pk)
        
        print("First unique")
        for pk in pks:
            print("PKMN {0} (Lvl. {1} {2} CP {3} HP {4})".format(cnt, pk['level'], pk['spec'], pk['cp'], pk['hp']))
        
        while True:
            seen = set()
            if not any((pk['hp'], pk['cp']) in seen or seen.add((pk['hp'], pk['cp'])) for pk in pks):
                break
            for pk in pks:
                pk['level'] += 0.5
                pk['cp'] = pkgo_pkmn.calcCPForPKMN(pk)
                pk['hp'] = pkgo_pkmn.calcHPForPKMN(pk)
        
        print("All unique")
        for pk in pks:
            print("PKMN {0} (Lvl. {1} {2} CP {3} HP {4})".format(cnt, pk['level'], pk['spec'], pk['cp'], pk['hp']))
        """
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

