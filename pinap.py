#!/usr/bin/env python
######################################################
#
#    pinap.py
#
#  Calculate the breakpoint at which to throw Pinaps
#  to maximize candy from a raid boss.
#
#  Usage: pinap.py <species name or catch rate> <Pokemon level> <throw bonus> <curve ball> <medal type> <ball count> <will transfer>
#
######################################################

import sys
import optparse
import distutils.util

import catchlib

def main(argv=None):
    usage="calcCatch.py <species name or catch rate> <Pokemon level> <throw bonus> <curve ball> <medal type> <ball count> <will transfer>"
    parser = optparse.OptionParser(usage=usage)
    
    (options, args) = parser.parse_args()
    
    # Get arguments
    try:
        base, level, throw_type, curve, medal, ball_count, will_transfer = args
    except ValueError:
        print "ERROR: Invalid number of arguments"
        print usage
        return 1
    
    # Interpret "will_transfer" argument as a boolean
    will_transfer = distutils.util.strtobool(will_transfer)
    
    candy_award = 3
    transfer_award = 0
    if will_transfer:
        transfer_award = 1
    
    # Store breakpoint with and without transfer
    opt_candy = 0
    opt_candy_index = 0
    
    # Loop from 0 to <number of balls> to find the breakpoint
    for i in range(int(ball_count) + 1):
        print "====Start GRB with {0} balls remaining====".format(i)
        
        # Calculate catch rates
        p_catch, p_cumu_catch = catchlib.calcCatch(base, level, throw_type, "premier", "pinap", curve, medal, int(ball_count) - i, False)
        grb_catch, grb_cumu_catch = catchlib.calcCatch(base, level, throw_type, "premier", "grb", curve, medal, i, False)
        grb_adjusted_catch = (1 - p_cumu_catch) * grb_cumu_catch
        print "Pinap catch rate: {0:2}%, GRB catch rate: {1:2}%".format(p_cumu_catch * 100, grb_adjusted_catch * 100)
        total_catch = p_cumu_catch + grb_adjusted_catch
        print "Total catch rate: {0:2}%".format(total_catch * 100)
        
        # Calculate expected candy
        exp_candy = (((2 * candy_award) + transfer_award) * p_cumu_catch) + ((candy_award + transfer_award) * grb_adjusted_catch)
        print "Expected candies: {0:2}".format(exp_candy)
        
        if exp_candy > opt_candy:
            opt_candy = exp_candy
            opt_candy_index = i
    
    # Final recommendation
    print "Start GRB when you have {0} balls left".format(opt_candy_index)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

