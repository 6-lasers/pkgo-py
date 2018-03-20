#!/usr/bin/env python
######################################################
#
#    perfectCalc.py
#
#  Calculation all possible CP that could mean 100% IV
#
#  Usage: perfectCalc.py <perfectCalc.py <PKMN species (or 'all')> [-f <file name>]
#
######################################################

from __future__ import print_function

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

def _print(str, f):
    if f:
        f.write(str + "\n")
    else:
        print(str)

def main(argv=None):
    usage="perfectCalc.py <PKMN species (or 'all')> [-f <file name>]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("--file", "-f", help="File to write output to. If omitted, prints to stdout.")
    
    (options, args) = parser.parse_args()
    
    # Get arguments
    try:
        specSelect, = args
    except ValueError:
        print("ERROR: Invalid number of arguments")
        print(usage)
        return 1
    
    outputFile = open(options.file, "w") if options.file else None
    
    baseStatsName = os.path.join(dataDir, "baseStats.json")
    dustJsonName = os.path.join(dataDir, "dust-to-level.json")
    levelToCpmName = os.path.join(dataDir, "level-to-cpm.json")
    
    baseStatsFile = open(baseStatsName, "r")
    pkgo_data.baseStats = json.load(baseStatsFile)
    baseStatsFile.close()
    
    dustJsonFile = open(dustJsonName, "r")
    pkgo_data.dustJson = json.load(dustJsonFile)
    dustJsonFile.close()
    
    levelToCpmFile = open(levelToCpmName, "r")
    pkgo_data.levelToCpm = json.load(levelToCpmFile)
    levelToCpmFile.close()
    
    specIndexFile = open(os.path.join(dataDir, "specIndex.json"))
    specIndex = json.load(specIndexFile)
    specIndexFile.close()
    
    # If not 'all', it's a single Pokemon species name
    if specSelect != "all":
        pkarr = []
        pkarr.append(dict({
            'spec' : specSelect,
            'ivsta' : 15,
            'ivatk' : 15,
            'ivdef' : 15
        }))
    # If it is 'all', grab list of all species
    else:
        pkarr = [dict({
            'spec' : foo,
            'ivsta' : 15,
            'ivatk' : 15,
            'ivdef' : 15
        }) for foo in specIndex['index']]
    # In either case, we constructed a mon definition
    # which is 100% IV, but didn't fill in the level yet
    
    # Print header
    _print("Species,{0}".format(",".join(["L" + str(i) for i in range(1, 36)])), outputFile)
    # List is fixed size, so pre-declare it to save
    # some trivial amount of processing power
    cparr = [None] * 35
    # For each species in the list
    for pk in pkarr:
        # For each level 1-35 (inclusive)
        for i in range(1, 36):
            # Fill in level
            pk['level'] = float(i)
            # Calculate CP and save in array
            cparr[i - 1] = pkgo_pkmn.calcCPForPKMN(pk)
        # Print array to stdout
        _print("{0},{1}".format(pk['spec'].capitalize(), ",".join([str(cp) for cp in cparr])), outputFile)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

