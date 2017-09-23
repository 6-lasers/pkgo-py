#!/usr/bin/env python
######################################################
#
#    pinap.py
#
#  Calculate the breakpoint at which to throw Pinaps
#  to maximize candy from a raid boss.
#
#  Usage: pinap.py <species name or catch rate> <Pokemon level> <throw bonus> <ball type> <curve ball> <medal type> <ball count>
#
######################################################

import sys
import optparse

import catchlib

def main(argv=None):
    usage="calcCatch.py <species name or catch rate> <Pokemon level> <throw bonus> <ball type> <curve ball> <medal type> <ball count>"
    parser = optparse.OptionParser(usage=usage)
    
    (options, args) = parser.parse_args()
    
    # Get arguments
    try:
        base, level, throw_type, ball, curve, medal, ball_count = args
    except ValueError:
        print "ERROR: Invalid number of arguments"
        print usage
        return 1
    
    # Store breakpoint with and without transfer
    opt_candy = 0
    opt_candy_transfer = 0
    opt_candy_index = 0
    opt_candy_index_transfer = 0
    
    # Loop from 0 to <number of balls> to find the breakpoint
    for i in range(int(ball_count) + 1):
        print "====Start GRB on ball {0}====".format(i)
        
        # Calculate catch rates
        p_catch, p_cumu_catch = catchlib.calcCatch(base, level, throw_type, ball, "pinap", curve, medal, int(ball_count) - i, False)
        grb_catch, grb_cumu_catch = catchlib.calcCatch(base, level, throw_type, ball, "grb", curve, medal, i, False)
        grb_adjusted_catch = (1 - p_cumu_catch) * grb_cumu_catch
        print "Pinap catch rate: {0:2}%, GRB catch rate: {1:2}%".format(p_cumu_catch * 100, grb_adjusted_catch * 100)
        total_catch = p_cumu_catch + grb_adjusted_catch
        print "Total catch rate: {0:2}%".format(total_catch * 100)
        
        # Calculate expected candy
        exp_candy = (6 * p_cumu_catch) + (3 * grb_adjusted_catch)
        exp_candy_transfer = (7 * p_cumu_catch) + (4 * grb_adjusted_catch)
        print "Expected candies: {0:2}, (if transferring) {1:2}".format(exp_candy, exp_candy_transfer)
        
        if exp_candy > opt_candy:
            opt_candy = exp_candy
            opt_candy_index = i
        if exp_candy_transfer > opt_candy_transfer:
            opt_candy_transfer = exp_candy_transfer
            opt_candy_index_transfer = i
    
    # Final recommendation
    print "Start GRB on ball {0} if transferring, else {1}".format(opt_candy_index_transfer, opt_candy_index)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

