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
import argparse
import json
import copy

def calcBoxPrice(prices, box, compare, noegg):
    total = 0
    for item, count in box['items']:
        if not (item in ['egg', 'star piece'] and noegg):
            total += count * prices[item][compare]
    return total

def getPercOfEffPriceStr(eff_price, hist_low):
    percent_of_eff_price = (eff_price / hist_low) - 1
    ret = ""
    
    if percent_of_eff_price > 0.0:
        ret = "({0:.1%} more than historical low)".format((eff_price / hist_low) - 1)
    elif percent_of_eff_price < 0.0:
        ret = "({0:.1%} **less** than historical low)".format(-1 * ((eff_price / hist_low) - 1))
    else:
        ret = "(Equal to historical low!)"
    
    return ret

def dump_sale_info(fd, prices, noegg_prices, boxes, boxnames, compare):
    # Write header
    fd.write("## Overall Verdict (tl;dr)\n\n")
    fd.write(" ".join("**{0}** <box analysis>.".format(name.title()) for name in boxnames) + "\n\n")
    fd.write("**See table at the bottom of the post for justifications of item valuation.**\n\n")
    
    # Count passes, incubators
    for name, box in boxes.items():
        box['pass_count'] = 0
        box['inc_count'] = 0
        box['perpass_price'] = 0
        box['perinc_price'] = 0
        box['fix_price'] = 0
        for item, count in box['items']:
            if item == "pass":
                box['pass_count'] = count
                box['perpass_price'] = float(box['price']) / count
            if item == "incubator" or item == "super incubator":
                box['inc_count'] = count
                box['perinc_price'] = float(box['price']) / count
                # Assume only one kind of incubator per box
                box['inc_type'] = item
        if box['pass_count'] and box['inc_count']:
            box['fix_price'] = (float(box['price']) - (60 * box['pass_count'])) / box['inc_count']
    
    # Find cheapest deals
    #for name, box in boxes.items():
    ax = min(boxes.items(), key=lambda (x,y):y['perpass_price'])
    bx = min(boxes.items(), key=lambda (x,y):y['perinc_price'])
    cx = min(boxes.items(), key=lambda (x,y):y['fix_price'])
    
    fd.write("---\n\n")
    fd.write("If you **only care about Raid Passes** and don't want Incubators, the best deal is **{0:.1f} coins/pass**, from the {1}.\n\n".format(ax[1]['perpass_price'], ax[0].title()))
    fd.write("---\n\n")
    fd.write("If you **only care about Incubators** and don't want Raid Passes, the best deal is **{0:.1f} coins/{1}**, from the {2}.\n\n".format(bx[1]['perinc_price'], cx[1]['inc_type'].title(), bx[0].title()))
    fd.write("---\n\n")
    fd.write("If you **want both raid passes and incubators**, the best deal is **60 coins/pass, {0:.1f} coins/{1}**, from the {2}.\n\n".format(cx[1]['fix_price'], cx[1]['inc_type'].title(), cx[0].title()))
    
    # Go through each box
    for name in boxnames:
        box = boxes[name]
        fd.write("---\n\n")
        fd.write("## {0} ({1} coins)\n\n".format(name.title(), box['price']))
        #fd.write("Item|Value per item (best sale)|Total Value (best sale)|Value per item (full price)|Total Value (full price)\n")
        #fd.write("-|-|-|-|-\n")
        fd.write("Item|Value per item|Total Value|Total Value (ignore eggs/star pieces)\n")
        fd.write("-|-|-|-\n")
        
        has_egg = False
        has_star_piece = False
        
        pass_count = box['pass_count']
        incubator_count = box['inc_count']
        
        for item, count in box['items']:
            item_name = prices[item]['name'] if 'name' in prices[item] else item
            if item == "egg":
                has_egg = True
            if item == "star piece":
                has_star_piece = True
            #fd.write("{0} {1}|{2}|{3}|{4}|{5}\n".format(count, item_name.title(), prices[item]['sale'], count * prices[item]['sale'], prices[item]['full'], count * prices[item]['full']))
            fd.write("{0} {1}|{2}|{3}|{4}\n".format(count, item_name.title(), prices[item][compare], count * prices[item][compare], count * noegg_prices[item][compare]))
        fd.write("**Total**||**{0}**|**{1}**\n\n".format(box['total'], box['noegg_total']))
        
        # Price per item for items which people want to optimize
        pass_hist_low = 1480 / 24.0
        inc_hist_low = 480 / 4.0
        fix_hist_low = 760 / 12.0
        if pass_count > 0:
            listjoin = ", or" if incubator_count > 0 else ""
            eff_price = float(box['price']) / pass_count
            fd.write("* **{0:.1f} coins/pass.** {1}{2}\n\n".format(eff_price, getPercOfEffPriceStr(eff_price, pass_hist_low), listjoin))
        if incubator_count > 0:
            listjoin = ", or" if pass_count > 0 else ""
            eff_price = float(box['price']) / incubator_count
            fd.write("* **{0:.1f} coins/{1}.** {2}{3}\n\n".format(eff_price, box['inc_type'], getPercOfEffPriceStr(eff_price, inc_hist_low), listjoin))
        if pass_count > 0 and incubator_count > 0:
            raidfix_price = (float(box['price']) - (60 * pass_count)) / incubator_count
            fd.write("* If you were to value **raid passes at 60 coins** a piece, you would be paying **{0:.1f} coins/Super Incubator** {1}\n\n".format(raidfix_price, getPercOfEffPriceStr(eff_price, fix_hist_low)))
        
        # Items that people might not care about
        
        questionable = []
        if has_egg:
            questionable.append("Lucky Eggs")
        if has_star_piece:
            questionable.append("Star Pieces")
        questionable_s = " or ".join(questionable)
        # If there are no questionable items, just print the simple summary
        if not questionable_s:
            if box['total'] < box['price']:
                fd.write("Box is **{0} coins loss** of value ({1:.1%} extra).\n\n".format(box['price'] - box['total'], float(box['price']) / box['total'] - 1))
            else:
                fd.write("Box is **{0} coins gain** in value ({1:.1%} off).\n\n".format(box['total'] - box['price'], 1 - float(box['price']) / box['total']))
        # Otherwise, consider effects of removing questionable items
        else:
            # If total is already worse, just quit
            if box['total'] < box['price']:
                fd.write("Box is **{0} coins loss** of value ({1:.1%} extra) *even if you want {2}*. Not recommended.\n\n".format(box['price'] - box['total'], float(box['price']) / box['total'] - 1, questionable_s))
            # Try removing eggs and Star Pieces
            else:
                if box['total'] > box['price']:
                    fd.write("Box is **{0} coins gain** in value ({1:.1%} off) if you want {2}.".format(box['total'] - box['price'], 1 - float(box['price']) / box['total'], questionable_s))
                elif box['total'] == box['price']:
                    fd.write("Box is **a fair value** if you want {0}.".format(questionable_s))
                if box['noegg_total'] < box['price']:
                    fd.write(" If you don't want those, it is a **{0} coins loss** in value ({1:.1%} extra).\n\n".format(box['price'] - box['noegg_total'], float(box['price']) / box['noegg_total'] - 1))
                elif box['noegg_total'] == box['price']:
                    fd.write(" If you don't want those, it is a **a fair value**.\n\n")
                else:
                    fd.write(" If you don't want those, it's still a **{0} coins gain** in value ({1:.1%} off).\n\n".format(box['noegg_total'] - box['price'], 1 - float(box['price']) / box['noegg_total']))
        
        fd.write("**Verdict**: \n\n")
    
    fd.write("""---

### Pricing calculations

Most prices compared against their 'usual' sale prices. See table for details.

If applicable, Star Pieces and Lucky Eggs valued at 0 in the third column, just in case you personally don't want them.

Item|Value per item|Justification
-|-|-
**Premium Raid Pass**|100|Hasn't been a sale price on Passes since June so I value them at full price
**Incubator/Super Incubator**|150|In most cases, Regular/Super Incubator perform the same function so I value them both the same.
**Lucky Egg**|25|Back when they used to do half-price Lucky Egg sales, this was the best price.
**Star Piece**|50|This was the price the one time they did a Star Piece-only bundle.
**Incense/Lure Module**|0|These can be useful, but they are bundled for free with so many boxes, so I value them as 'extras'
**Consumables (balls, berries, potions)**|0|They can be obtained for free, so I don't value them. I try to highlight in my summary if a box might be a good deal if you need these items.""")

def main(argv=None):
    usage="sale.py <args>"
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="text file containing sale information")
    parser.add_argument("--compare_box", nargs=2, metavar=("<box1>", "<box2>"), help="compare two boxes")
    parser.add_argument("--compare_full", help="Compare against full prices instead of best known sale", action="store_true", dest="full")
    parser.add_argument("--reddit", metavar="<file.txt>", help="Write Markdown-formatted post to a file", dest="reddit")
    
    arguments = parser.parse_args()
    
    with open(arguments.file, "r") as f:
        lines = f.readlines()
    
    with open(os.path.join("gameData", "shopPrices.json"), "r") as f:
        prices = json.load(f)
    
    noegg_prices = copy.deepcopy(prices)
    noegg_prices['egg']['full'] = 0
    noegg_prices['egg']['sale'] = 0
    noegg_prices['star piece']['full'] = 0
    noegg_prices['star piece']['sale'] = 0
    
    compare = 'full' if arguments.full else 'sale'
    
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
    if arguments.reddit:
        with open(arguments.reddit, "w") as fd:
            dump_sale_info(fd, prices, noegg_prices, boxes, boxnames, compare)
    else:
        dump_sale_info(sys.stdout, prices, noegg_prices, boxes, boxnames, compare)
    
    if arguments.compare_box:
        box1, box2 = arguments.compare_box
        if boxes[box1]['price'] <= boxes[box2]['price']:
            sbox = box1
            lbox = box2
        else:
            sbox = box2
            lbox = box1
        
        ratio = int(round(float(boxes[lbox]['price']) / boxes[sbox]['price']))
        
        diffDict = {}
        diffDict['price'] = boxes[lbox]['price'] - (boxes[sbox]['price'] * ratio)
        for item, count in boxes[sbox]['items']:
            diffDict[item] = ratio * count
        for item, count in boxes[lbox]['items']:
            if item in diffDict:
                diffDict[item] -= count
            else:
                diffDict[item] = count * -1
        
        columnS = []
        columnL = []
        for item, count in diffDict.items():
            if count < 0:
                columnL.append((item, count))
            elif count > 0:
                columnS.append((item, count))
        
        columnS.sort(key=lambda x: 999 if x[0] == "price" else prices[x[0]]['sale'])
        columnL.sort(key=lambda x: 999 if x[0] == "price" else prices[x[0]]['sale'])
        
        fd = sys.stdout
        ratioStr = "" if ratio == 1 else "{0}x ".format(ratio)
        fd.write("**{0}{1}**|**{2}**\n".format(ratioStr, sbox.title(), lbox.title()))
        fd.write("-|-\n")
        while columnS:
            item, count = columnS.pop()
            if item == "price":
                strS = "Save {0} coins".format(count)
            else:
                item_name = prices[item]['name'] if 'name' in prices[item] else item
                strS = "{0} {1}".format(count, item_name.title())
            if columnL:
                item, count = columnL.pop()
                count *= -1
                if item == "price":
                    strL = "Save {0} coins".format(count)
                else:
                    item_name = prices[item]['name'] if 'name' in prices[item] else item
                    strL = "{0} {1}".format(count, item_name.title())
            else:
                strL = "-"
            fd.write("{0}|{1}\n".format(strS, strL))
        while columnL:
            item, count = columnL.pop()
            count *= -1
            if item == "price":
                strL = "Save {0} coins".format(count)
            else:
                item_name = prices[item]['name'] if 'name' in prices[item] else item
                strL = "{0} {1}".format(count, item_name.title())
            fd.write("-|{0}\n".format(strL))
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

