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
import csv

# Items that people might not care about
#questionable = ['egg', 'star piece']
questionable = ['egg']

def pluralize(mystr):
    if mystr[-1] == 's':
        suffix = "es"
    else:
        suffix = "s"
    return mystr + suffix

def calcBoxPrice(prices, box, compare, noegg):
    total = 0
    for item, count in box['items']:
        if not (item in questionable and noegg):
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
            if item == "incubator" or item == "super incubator":
                box['inc_count'] += count
                # Assume only one kind of incubator per box
                box['inc_type'] = item
        if box['pass_count']:
            box['perpass_price'] = float(box['price']) / box['pass_count']
        if box['inc_count']:
            box['perinc_price'] = float(box['price']) / box['inc_count']
        if box['pass_count'] and box['inc_count']:
            box['fix_price'] = (float(box['price']) - (60 * box['pass_count'])) / box['inc_count']
    
    # Find cheapest deals
    boxes_with_passes = [(name, box) for name, box in boxes.items() if box['pass_count'] > 0]
    boxes_with_incs = [(name, box) for name, box in boxes.items() if box['inc_count'] > 0]
    boxes_with_both = [(name, box) for name, box in boxes.items() if box['inc_count'] > 0 and box['pass_count'] > 0]
    
    if boxes_with_passes:
        best_for_pass = min(boxes_with_passes, key=lambda (x,y):y['perpass_price'])
        fd.write("---\n\n")
        fd.write("If you **only care about Raid Passes** and don't want Incubators, the best deal is **{0:.1f} coins/pass**, from the {1}.\n\n".format(best_for_pass[1]['perpass_price'], best_for_pass[0].title()))
    if boxes_with_incs:
        best_for_inc = min(boxes_with_incs, key=lambda (x,y):y['perinc_price'])
        fd.write("---\n\n")
        fd.write("If you **only care about Incubators** and don't want Raid Passes, the best deal is **{0:.1f} coins/{1}**, from the {2}.\n\n".format(best_for_inc[1]['perinc_price'], best_for_inc[1]['inc_type'].title(), best_for_inc[0].title()))
    if boxes_with_both:
        best_for_both = min(boxes_with_both, key=lambda (x,y):y['fix_price'])
        fd.write("---\n\n")
        fd.write("If you **want both raid passes and incubators**, the best deal is **60 coins/pass, {0:.1f} coins/{1}**, from the {2}.\n\n".format(best_for_both[1]['fix_price'], best_for_both[1]['inc_type'].title(), best_for_both[0].title()))
    
    # Go through each box
    for name in boxnames:
        box = boxes[name]
        fd.write("---\n\n")
        fd.write("## {0} ({1} coins)\n\n".format(name.title(), box['price']))
        #fd.write("Item|Value per item (best sale)|Total Value (best sale)|Value per item (full price)|Total Value (full price)\n")
        #fd.write("-|-|-|-|-\n")
        
        questionable_t = []
        
        # Check for questionable items
        for item, count in box['items']:
            if item in questionable:
                questionable_t.append(pluralize(prices[item]['name'] if 'name' in prices[item] else item).title())
        
        fd.write("Item|Value per item|Total Value")
        if questionable_t:
            fd.write("|Total Value (ignore {0})\n".format("/".join([pluralize(item) for item in questionable])))
            fd.write("-|-|-|-\n")
        else:
            fd.write("\n")
            fd.write("-|-|-\n")
        questionable_s = " or ".join(questionable_t)
        
        pass_count = box['pass_count']
        incubator_count = box['inc_count']
        
        for item, count in box['items']:
            item_name = prices[item]['name'] if 'name' in prices[item] else item
            #fd.write("{0} {1}|{2}|{3}|{4}|{5}\n".format(count, item_name.title(), prices[item]['sale'], count * prices[item]['sale'], prices[item]['full'], count * prices[item]['full']))
            fd.write("{0} {1}|{2}|{3}".format(count, item_name.title(), prices[item][compare], count * prices[item][compare]))
            if questionable_t:
                fd.write("|{0}\n".format(count * noegg_prices[item][compare]))
            else:
                fd.write("\n")
        fd.write("**Total**||**{0}**".format(box['total']))
        if questionable_t:
            fd.write("|**{0}**\n\n".format(box['noegg_total']))
        else:
            fd.write("\n\n")
        
        # Price per item for items which people want to optimize
        pass_hist_low = 1480 / 24.0
        inc_hist_low = 1480 / 17.0
        fix_hist_low = 640 / 12.0
        
        print_pass = pass_count > 0 and float(box['price']) / pass_count <= prices['pass']['full']
        print_inc = incubator_count > 0 and float(box['price']) / incubator_count <= prices['super incubator']['full']
        
        if print_pass:
            listjoin = ", or" if print_inc else ""
            eff_price = float(box['price']) / pass_count
            fd.write("* **{0:.1f} coins/pass.** {1}{2}\n\n".format(eff_price, getPercOfEffPriceStr(eff_price, pass_hist_low), listjoin))
        if print_inc:
            listjoin = ", or" if pass_count > 0 else ""
            eff_price = float(box['price']) / incubator_count
            fd.write("* **{0:.1f} coins/{1}.** {2}{3}\n\n".format(eff_price, box['inc_type'], getPercOfEffPriceStr(eff_price, inc_hist_low), listjoin))
        if pass_count > 0 and incubator_count > 0:
            eff_price = (float(box['price']) - (60 * pass_count)) / incubator_count
            fd.write("* If you were to value **raid passes at 60 coins** a piece, you would be paying **{0:.1f} coins/{1}** {2}\n\n".format(eff_price, box['inc_type'].title(), getPercOfEffPriceStr(eff_price, fix_hist_low)))
        
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
            # Try removing questionable items
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

If applicable, {0} valued at 0 in the third column, just in case you personally don't want them.

Item|Value per item|Justification
-|-|-
**Premium Raid Pass**|100|Sales on Premium Passes are relatively rare so I value them at full price
**Incubator/Super Incubator**|150|In most cases, Regular/Super Incubator perform the same function so I value them both the same.
**Lucky Egg**|50|Best price for a Lucky Egg-only bundle in the shop.
**Star Piece**|50|This was the price the one time they did a Star Piece-only bundle.
**Incense/Lure Module**|0|These can be useful, but they are bundled for free with so many boxes, so I value them as 'extras'
**Consumables (balls, berries, potions)**|0|They can be obtained for free, so I don't value them. I try to highlight in my summary if a box might be a good deal if you need these items.""".format("/".join([pluralize(prices[item]['name'] if 'name' in prices[item] else item).title() for item in questionable])))

def compare_boxes(fd, prices, boxes, box1, box2):
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
    
    nothingS = not columnS
    nothingL = not columnL
    
    ratioStr = "" if ratio == 1 else "{0}x ".format(ratio)
    fd.write("**{0}{1}**|**{2}**\n".format(ratioStr, sbox.title(), lbox.title()))
    fd.write("-|-\n")
    while columnS:
        item, count = columnS.pop()
        if item == "price":
            strS = "Save {0} coins".format(count)
        else:
            item_name = prices[item]['name'] if 'name' in prices[item] else item
            strS = "+{0} {1}".format(count, item_name.title())
        if columnL:
            item, count = columnL.pop()
            count *= -1
            if item == "price":
                strL = "Save {0} coins".format(count)
            else:
                item_name = prices[item]['name'] if 'name' in prices[item] else item
                strL = "+{0} {1}".format(count, item_name.title())
        else:
            if nothingL:
                strL = "Literally nothing"
                nothingL = False
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
            strL = "+{0} {1}".format(count, item_name.title())
        if nothingS:
            strS = "Literally nothing"
            nothingS = False
        else:
            strS = "-"
        fd.write("{0}|{1}\n".format(strS, strL))


def main(argv=None):
    usage="sale.py <args>"
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="text file containing sale information")
    parser.add_argument("--compare_box", nargs=2, metavar=("<box1>", "<box2>"), help="compare two boxes")
    parser.add_argument("--compare_full", help="Compare against full prices instead of best known sale", action="store_true", dest="full")
    parser.add_argument("--reddit", metavar="<file.txt>", help="Write Markdown-formatted post to a file")
    parser.add_argument("--csv", metavar="<boxes.csv>", help="Write boxes in CSV format to a file")
    parser.add_argument("--csv_in", help="Take input in CSV format matching /u/DetectiveMargie's spreadsheet", action="store_true")
    
    arguments = parser.parse_args()
    
    boxnames = []
    boxes = {}
    curname = ""
    
    with open(arguments.file, "r") as f:
        if arguments.csv_in:
            reader = csv.DictReader(f)
            for row in reader:
                curname = row['Box'].lower() + " box"
                boxes[curname] = dict({'items':[]})
                boxnames.append(curname)
                boxes[curname]['price'] = int(row['Cost'])
                
                for item in ['Super Incubator','Incubator','Incense','Star Piece','Max Revive','Max Potion']:
                    if row[item]:
                        boxes[curname]['items'].append((item.lower(), int(row[item])))
                if row['Raid Pass']:
                    boxes[curname]['items'].append(("pass", int(row["Raid Pass"])))
                if row['Lucky Egg']:
                    boxes[curname]['items'].append(("egg", int(row["Lucky Egg"])))
                if row['Lure Module']:
                    boxes[curname]['items'].append(("lure", int(row["Lure Module"])))
        else:
            lines = f.readlines()
            
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
    
    with open(os.path.join("gameData", "shopPrices.json"), "r") as f:
        prices = json.load(f)
    
    noegg_prices = copy.deepcopy(prices)
    for item in questionable:
        noegg_prices[item]['full'] = 0
        noegg_prices[item]['sale'] = 0
    
    compare = 'full' if arguments.full else 'sale'
    
    # Output list
    for name,box in boxes.items():
        box['total'] = calcBoxPrice(prices, box, compare, False)
        box['noegg_total'] = calcBoxPrice(prices, box, compare, True)
    if arguments.csv:
        with open(arguments.csv, "w") as f:
            writer = csv.DictWriter(f, fieldnames=['Event','Start Date','Box','Cost','super incubator','incubator','pass','incense','lure','egg','star piece','poke ball','great ball','ultra ball','pinap','Razz Berry','Max Revive','Max Potion','','Value per unit cost','Rank','Value/cost with limited space','Rank with limited space','Alternate value/cost','Alternate rank','Raw market value/cost','Raw market value rank','Percentage discount','"% discount, limited space"','Alternate % discount','% discount relative to market'])
            for name, box in boxes.items():
                writer.writerow(dict(box['items'] + [('Box', name.split()[0].capitalize()), ('Cost', box['price'])]))
        
    if arguments.reddit:
        with open(arguments.reddit, "w") as fd:
            dump_sale_info(fd, prices, noegg_prices, boxes, boxnames, compare)
    else:
        dump_sale_info(sys.stdout, prices, noegg_prices, boxes, boxnames, compare)
    
    if arguments.compare_box:
        box1, box2 = arguments.compare_box
        compare_boxes(sys.stdout, prices, boxes, box1, box2)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

