######################################################
#
#    pkgo_data.py
#
#  Common variables for Pokemon GO modules
#
######################################################

import os
import json

baseStats = None
dustJson = None
levelToCpm = None

def loadData(dataDir, statsType):
    global baseStats
    global dustJson
    global levelToCpm
    
    baseStatsName = os.path.join(dataDir, "baseStats.json")
    dustJsonName = os.path.join(dataDir, "dust-to-level.json")
    levelToCpmName = os.path.join(dataDir, "level-to-cpm.json")
    
    baseStatsFile = open(baseStatsName, "r")
    baseStats = json.load(baseStatsFile)
    baseStatsFile.close()
    
    dustJsonFile = open(dustJsonName, "r")
    dustJson = json.load(dustJsonFile)
    dustJsonFile.close()
    
    levelToCpmFile = open(levelToCpmName, "r")
    levelToCpm = json.load(levelToCpmFile)
    levelToCpmFile.close()

