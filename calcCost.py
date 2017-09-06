#!/usr/bin/env python
######################################################
#
#    calcCost.py
#
#  Calculate dust and candy costs to power up Pokemon
#  from one level to another.
#
#  Usage: script.py <start level> <end level>
#
######################################################

import os
import sys
import optparse
import json

def main(argv=None):
    usage="script.py <start level> <end level>"
    parser = optparse.OptionParser(usage=usage)
    
    (options, args) = parser.parse_args()
    
    # Get arguments
    try:
        startLvl, endLvl = args
    except ValueError:
        print "ERROR: Invalid number of arguments"
        print usage
        return 1
    
    startLvl = float(startLvl)
    endLvl = float(endLvl)
    
    dustJsonName = os.path.join(os.getcwd(), "dust-to-level.json")
    candyJsonName = os.path.join(os.getcwd(), "level-to-candy.json")
    
    dustJsonFile = open(dustJsonName, "r")
    dustJson = json.load(dustJsonFile)
    dustJsonFile.close()
    
    candyJsonFile = open(candyJsonName, "r")
    candyJson = json.load(candyJsonFile)
    candyJsonFile.close()
    
    dustCost = 0
    candyCost = 0
    
    reverseDustJson = dict()
    for cost in dustJson:
        for level in dustJson[cost]:
            reverseDustJson[level] = int(cost)
    
    tmpLvl = startLvl
    while tmpLvl != endLvl:
        dustCost += reverseDustJson[tmpLvl]
        candyCost += candyJson[str(tmpLvl)]
        tmpLvl += 0.5
    
    print "To level from {0} to {1}, you need:".format(startLvl, endLvl)
    print "{0} dust and {1} candies.".format(dustCost, candyCost)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

