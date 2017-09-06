#!/usr/bin/env python
######################################################
#
#    ivcalc.py
#
#  Calculate IVs
#
#  Usage: ivcalc.py <input.txt> <directory with Pokemon Go data files>
#
######################################################

import os
import sys
import optparse
import json

import yaml

import pkgo_data
import pkgo_pkmn
import pkgo_appraise


def main(argv=None):
    usage="Usage: ivcalc.py <input.txt> <directory with Pokemon Go data files>"
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
    
    baseStatsFile = open(baseStatsName, "r")
    pkgo_data.baseStats = yaml.load(baseStatsFile)
    baseStatsFile.close()
    
    dustJsonFile = open(dustJsonName, "r")
    pkgo_data.dustJson = json.load(dustJsonFile)
    dustJsonFile.close()
    
    levelToCpmFile = open(levelToCpmName, "r")
    pkgo_data.levelToCpm = json.load(levelToCpmFile)
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
        appr = pkgo_appraise.lineToAppr(line)
        
        # Check IVs for each appraisal
        print "PKMN {0} ({1} CP {2}):".format(cnt, appr['spec'], appr['cp'])
        pkarr = pkgo_appraise.matchApprIVs(appr)
        for pk in pkarr:
            print "Possible match: {0}".format(pkgo_pkmn.PKMNToStr(pk))
        
        cnt += 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

