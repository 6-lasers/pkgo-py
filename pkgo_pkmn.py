######################################################
#
#    pkgo_pkmn.py
#
#  Libraries for handling Pokemon Go mon-related tasks
#  such as calculating CP and serializing to/from string.
#
######################################################

import math

import pkgo_data

# pkmn objects have the following fields:
# hp, cp, IVs, species, base stats, level

# Max IV is 15
maxIV = 15

# Calculate CP
def calcCPBackend(sta, atk, defe, cpm):
    return int(max(10, math.floor(atk * math.pow(defe, 0.5) * math.pow(sta, 0.5) * math.pow(cpm, 2) / 10)))

def calcCP(sta, atk, defe, lvl):
    cpm = pkgo_data.levelToCpm[str(lvl)]
    return calcCPBackend(sta, atk, defe, cpm)

def calcCPForPKMN(pk):
    basesta, baseatk, basedef = tuple(pkgo_data.baseStats[pk['spec']])
    return calcCP(basesta + pk['ivsta'], baseatk+ pk['ivatk'], basedef + pk['ivdef'], pk['level'])

# Calculate HP
def calcHP(sta, lvl):
    cpm = pkgo_data.levelToCpm[str(lvl)]
    return int(max(10, math.floor(cpm * sta)))

def ivstrToIVs(pk, ivstr):
    pk['ivsta'] = int(ivstr[0], 16)
    pk['ivatk'] = int(ivstr[1], 16)
    pk['ivdef'] = int(ivstr[2], 16)

def PKMNFromStr(str):
    splitline = str.split()
    
    pk = dict({})
    try:
        pk['level'], pk['spec'], pk['ivsta'], pk['ivatk'], pk['ivdef'] = tuple(splitline)
        
        pk['ivsta'] = int(pk['ivsta'], 10)
        pk['ivatk'] = int(pk['ivatk'], 10)
        pk['ivdef'] = int(pk['ivdef'], 10)
    except:
        pk['level'], pk['spec'], ivs = tuple(splitline)
        ivstrToIVs(pk, ivs)
    pk['level'] = float(pk['level'])
    pk['spec'] = pk['spec'].capitalize()
    
    return pk

def PKMNToStr(pk):
    ivsum = pk['ivsta'] + pk['ivatk'] + pk['ivdef']
    return "Level {0} {1}, IVs STA {2:2}, ATK {3:2}, DEF {4:2}, total {5:2} ({6:.1%}) ({2:x}{3:x}{4:x})".format(pk['level'], pk['spec'], pk['ivsta'], pk['ivatk'], pk['ivdef'], ivsum, ivsum / 45.0)

