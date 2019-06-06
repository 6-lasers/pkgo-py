#!/usr/bin/env python3
######################################################
#
#    boxCsvToJson.py
#
#  <description>
#
#  Usage: boxCsvToJson.py <args>
#
#  Copyright (C) 2017  Microsoft Corporation
#  All Rights Reserved
#  Confidential and Proprietary
#
######################################################

from __future__ import print_function

import sys
import argparse

import os
import copy
import io
import csv
import json
import datetime

# Items that people might not care about
#questionable = ['egg', 'star piece']
questionable = ['egg']

def date_from_ordinal(datestr):
    return [int(x) for x in datestr.split("-")]

def convertBoxFormat(box):
    #Super Incubator,Incubator,Raid Pass,Incense,Lure Module,Lucky Egg,Star Piece,Poke Ball,Great Ball,Ultra Ball,Pinap Berry,Razz Berry,Max Revive,Max Potion
    ret = {'items' : []}
    for item in ['Super Incubator','Incubator','Incense','Star Piece','Max Revive','Max Potion']:
        if box[item]:
            ret['items'].append((item.lower(), int(box[item])))
    if box['Raid Pass']:
        ret['items'].append(("pass", int(box["Raid Pass"])))
    if box['Lucky Egg']:
        ret['items'].append(("egg", int(box["Lucky Egg"])))
    if box['Lure Module']:
        ret['items'].append(("lure", int(box["Lure Module"])))
    return ret

def calcBoxPrice(prices, box, compare, noegg):
    total = 0
    for item, count in box['items']:
        if not (item in questionable and noegg):
            total += count * prices[item][compare]
    return total

def calcAvgSavings(boxes, prices, compare, verbose):
    pricesAtCost = {}
    best = {}
    for box in boxes:
        value = calcBoxPrice(prices, convertBoxFormat(box), compare, compare == "sale")
        if verbose:
            print(box['Event'] + ": " + box['Box'] + " Box")
            print(value, box['Cost'])
            print("{0:.1%} savings".format(1 - (float(box['Cost']) / value)))
        if box['Cost'] not in pricesAtCost:
            pricesAtCost[box['Cost']] = []
        pricesAtCost[box['Cost']].append(value)
        if box['Cost'] not in best:
            best[box['Cost']] = ("",0)
        if value > best[box['Cost']][1]:
            best[box['Cost']] = (box['Event'] + " " + box['Box'], value)
    return {cost: {'avg' : sum(values) / len(values), 'best' : best[cost], 'latest' : values[-1]} for (cost,values) in pricesAtCost.items()}

def printSummary(boxes, cutoff_date, title, prices, compare, verbose):
    #print(calcAvgSavings([box for box in boxes if box['Start Date'] >= three_months_back], noegg_prices))
    lul = calcAvgSavings([box for box in boxes if box['Start Date'] >= cutoff_date], prices, compare, verbose)
    print(title + ":")
    for price, stuff in sorted(lul.items(),key=lambda x:int(x[0])):
        value = stuff['avg']
        print("{0} coin boxes: average {1:.1f} coin value, {2:.1%} savings".format(price, value, 1 - (float(price) / value)))
        print("Best value: {1}, {2} ({0:.1%})".format((stuff['best'][1] / stuff['avg']) - 1, *stuff['best']))
        print("Latest value: {1} ({0:.1%})".format((stuff['latest'] / stuff['avg']) - 1, stuff['latest']))

def main(argv=None):
    parser = argparse.ArgumentParser(description="template")
    parser.add_argument("inputCsv", help="help message")
    parser.add_argument("outputJson", help="help message")
    parser.add_argument("--compare_full", help="Compare against full prices instead of best known sale", action="store_true", dest="full")
    parser.add_argument("--verbose", help="Compare against full prices instead of best known sale", action="store_true")
    #parser.add_argument("--name", help="help message")
    
    args = parser.parse_args()
    
    with open(os.path.join("gameData", "shopPrices.json"), "r") as f:
        prices = json.load(f)
    
    noegg_prices = copy.deepcopy(prices)
    for item in questionable:
        noegg_prices[item]['full'] = 0
        noegg_prices[item]['sale'] = 0
    
    compare = 'full' if args.full else 'sale'
    
    with io.open(args.inputCsv, "r", encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        boxes = [row for row in reader]
        for box in boxes:
            box['Start Date'] = datetime.date(*(date_from_ordinal(box['Start Date'])))
        #for line in f:
        #    # Event,Start Date,Box,Cost,Super Incubator,Incubator,Raid Pass,Incense,Lure Module,Lucky Egg,Star Piece,Poke Ball,Great Ball,Ultra Ball,Pinap Berry,Razz Berry,Max Revive,Max Potion,,Value per unit cost,Rank,Value/cost with limited space,Rank with limited space,Alternate value/cost,Alternate rank,Raw market value/cost,Raw market value rank,Percentage discount,"% discount, limited space",Alternate % discount,% discount relative to market
        #    event, date, box_name, cost, super_inc, inc, raid_pass, incense, lure, egg, starpiece, pokeball, greatball, ultraball, pinap, razz, max_revive, max_potion = line.split(",")[0:18]
    
    today = datetime.date.today()
    three_months_back = today - datetime.timedelta(weeks=13)
    six_months_back = today - datetime.timedelta(weeks=26)
    printSummary(boxes, three_months_back, "Last 3 months", prices if args.full else noegg_prices, compare, args.verbose)
    printSummary(boxes, six_months_back, "Last 6 months", prices if args.full else noegg_prices, compare, args.verbose)
    #for box in boxes:
    #    if box['Start Date'] >= three_months_back:
    #        value = calcBoxPrice(noegg_prices, convertBoxFormat(box), "sale", True)
    #        print(box['Event'] + ": " + box['Box'] + " Box")
    #        print(value, box['Cost'])
    #        print("{0:.1%} savings".format(1 - (float(box['Cost']) / value)))
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

