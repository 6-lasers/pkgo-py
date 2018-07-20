#!/usr/bin/env python
######################################################
#
#    sale.py
#
#  <description>
#
#  Usage: sale.py <args>
#
######################################################

from __future__ import print_function

import os
import sys
import optparse
import json
import copy

def calcBoxPrice(prices, box, compare, noegg):
    total = 0
    for item, count in box['items']:
        if not (item in ['egg', 'star piece'] and noegg):
            total += count * prices[item][compare]
    return total

def main(argv=None):
    usage="sale.py <args>"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("--compare_full", help="Compare against full prices instead of best known sale", action="store_true", dest="full")
    parser.add_option("--reddit", help="Write Markdown-formatted post to a file", dest="reddit")
    
    (options, args) = parser.parse_args()
    
    # Get arguments
    try:
        args, = args
    except ValueError:
        print("ERROR: Invalid number of arguments")
        print(usage)
        return 1
    
    with open(args, "r") as f:
        lines = f.readlines()
    
    with open(os.path.join("gameData", "shopPrices.json"), "r") as f:
        prices = json.load(f)
    
    noegg_prices = copy.deepcopy(prices)
    noegg_prices['egg']['full'] = 0
    noegg_prices['egg']['sale'] = 0
    noegg_prices['star piece']['full'] = 0
    noegg_prices['star piece']['sale'] = 0
    
    compare = 'full' if options.full else 'sale'
    
    boxnames = []
    boxes = {}
    curname = ""
    for line in lines:
        if line[0] == "!":
            splitline = line.strip().rsplit(None, 1)
            curname = splitline[0][1:].lower()
            boxes[curname] = dict({'items':[]})
            boxnames.append(curname)
            boxes[curname]['price'] = int(splitline[1])
        else:
            splitline = line.strip().split(None, 1)
            if splitline:
                count = int(splitline[0])
                item = splitline[1].lower()
                boxes[curname]['items'].append((item, count))
    
    # Output list
    for name,box in boxes.items():
        box['total'] = calcBoxPrice(prices, box, compare, False)
        box['noegg_total'] = calcBoxPrice(prices, box, compare, True)
    if options.reddit:
        with open(options.reddit, "w") as fd:
            for name in boxnames:
                pass_count = 0
                incubator_count = 0
                
                box = boxes[name]
                fd.write("---\n\n")
                fd.write("## {0} ({1} coins)\n\n".format(name.title(), box['price']))
                #fd.write("Item|Value per item (best sale)|Total Value (best sale)|Value per item (full price)|Total Value (full price)\n")
                #fd.write("-|-|-|-|-\n")
                fd.write("Item|Value per item|Total Value|Total Value (ignore eggs/star pieces)\n")
                fd.write("-|-|-|-\n")
                
                has_egg = False
                has_star_piece = False
                for item, count in box['items']:
                    item_name = prices[item]['name'] if 'name' in prices[item] else item
                    if item == "pass":
                        pass_count = count
                    if item == "incubator" or item == "super incubator":
                        incubator_count = count
                        # Assume only one kind of incubator per box
                        incubator_type = item
                    if item == "egg":
                        has_egg = True
                    if item == "star piece":
                        has_star_piece = True
                    #fd.write("{0} {1}|{2}|{3}|{4}|{5}\n".format(count, item_name.title(), prices[item]['sale'], count * prices[item]['sale'], prices[item]['full'], count * prices[item]['full']))
                    fd.write("{0} {1}|{2}|{3}|{4}\n".format(count, item_name.title(), prices[item][compare], count * prices[item][compare], count * noegg_prices[item][compare]))
                fd.write("**Total**||**{0}**|**{1}**\n\n".format(box['total'], box['noegg_total']))
                
                # Price per item for items which people want to optimize
                if pass_count > 0:
                    fd.write("**{0:.1f} coins/pass.** ".format(float(box['price']) / pass_count))
                if incubator_count > 0:
                    fd.write("**{0:.1f} coins/{1}.** ".format(float(box['price']) / incubator_count, incubator_type))
                
                # Items that people might not care about
                
                questionable = []
                if has_egg:
                    questionable.append("Lucky Eggs")
                if has_star_piece:
                    questionable.append("Star Pieces")
                questionable_s = " or ".join(questionable)
                # If total is already worse, just quit
                if box['total'] < box['price']:
                    fd.write("Box is **{0} coins loss** of value *even if you want {1}*. Not recommended.\n\n".format(box['price'] - box['total'], questionable_s))
                # Try removing eggs and Star Pieces
                else:
                    if box['total'] > box['price']:
                        fd.write("Box is **{0} coins gain** in value if you want {1}.".format(box['total'] - box['price'], questionable_s))
                    elif box['total'] == box['price']:
                        fd.write("Box is **a fair value** if you want {0}.".format(questionable_s))
                    if box['noegg_total'] < box['price']:
                        fd.write(" If you don't want those, it is a **{0} coins loss** in value.\n\n".format(box['price'] - box['noegg_total']))
                    elif box['noegg_total'] == box['price']:
                        fd.write(" If you don't want those, it is a **a fair value**.\n\n")
                    else:
                        fd.write(" If you don't want those, it's still a **{0} coins gain** in value.\n\n".format(box['noegg_total'] - box['price']))
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

