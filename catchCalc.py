#!/usr/bin/env python
######################################################
#
#    catchCalc.py
#
#  Calculate chances of catching a Pokemon.
#
#  Usage: calcCatch.py <species name or catch rate> <Pokemon level> <throw bonus> <ball type> <berry type> <curve ball> <medal type> <ball count> <allow flee>
#
######################################################

from __future__ import print_function

import sys
import optparse

import catchlib

def main(argv=None):
    usage="calcCatch.py <species name or catch rate> <Pokemon level> <throw bonus> <ball type> <berry type> <curve ball> <medal type> <ball count> <allow flee>"
    parser = optparse.OptionParser(usage=usage)
    
    (options, args) = parser.parse_args()
    
    # Get arguments
    try:
        base, level, throw_type, ball, berry, curve, medal, ball_count, can_flee = args
    except ValueError:
        print("ERROR: Invalid number of arguments")
        print(usage)
        return 1
    
    catch, cumu_catch = catchlib.calcCatch(base, level, throw_type, ball, berry, curve, medal, ball_count, can_flee)
    print("individual catch is {0:2}%".format(catch * 100))
    
    if ball_count != 0:
        print("cumulative catch chance is {0:2}%".format(cumu_catch * 100))
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

