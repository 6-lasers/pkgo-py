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

# TODO:
# Raid boss HP: 600, 1800, 3000, 7500, 12500
# Raid boss CPM: 0.61, 0.67, 0.73, 0.79
# Raid boss CP CPM: 1, raid HP replaces STA

# pkmn objects have the following fields:
# hp, cp, IVs, species, base stats, level

# Max IV is 15
maxIV = 15

def calcCpm(lvl):
    if lvl.is_integer():
        return pkgo_data.levelToCpm['cpMultiplier'][int(lvl) - 1]
    else:
        #return math.sqrt((math.pow(pkgo_data.levelToCpm[str(math.floor(lvl))], 2) + math.pow(pkgo_data.levelToCpm[str(math.ceil(lvl))], 2)) / 2);
        return math.sqrt((math.pow(pkgo_data.levelToCpm['cpMultiplier'][int(math.floor(lvl)) - 1], 2) + math.pow(pkgo_data.levelToCpm['cpMultiplier'][int(math.ceil(lvl)) - 1], 2)) / 2);

# Calculate CP
def calcCPBackend(sta, atk, defe, cpm, verbose=False):
    if verbose:
        print atk * math.pow(defe, 0.5) * math.pow(sta, 0.5) * math.pow(cpm, 2) / 10
    return int(max(10, math.floor(atk * math.pow(defe, 0.5) * math.pow(sta, 0.5) * math.pow(cpm, 2) / 10)))

def calcCP(sta, atk, defe, lvl, verbose=False):
    cpm = calcCpm(lvl)
    return calcCPBackend(sta, atk, defe, cpm, verbose)

def calcCPForPKMN(pk, verbose=False):
    basesta, baseatk, basedef = tuple(pkgo_data.baseStats[pk['spec'].lower()])
    return calcCP(basesta + pk['ivsta'], baseatk + pk['ivatk'], basedef + pk['ivdef'], pk['level'], verbose)

# Calculate HP
def calcHP(sta, lvl):
    cpm = calcCpm(lvl)
    return int(max(10, math.floor(cpm * sta)))

def calcHPForPKMN(pk):
    basesta = pkgo_data.baseStats[pk['spec'].lower()][0]
    return calcHP(basesta + pk['ivsta'], pk['level'])

# Calculate ATK or DEF
def calcATK(atk, lvl):
    cpm = calcCpm(lvl)
    return int(math.floor(cpm * atk))

def calcATKForPKMN(pk):
    baseatk = pkgo_data.baseStats[pk['spec'].lower()][0]
    return calcHP(baseatk + pk['ivatk'], pk['level'])

def calcDEF(defe, lvl):
    cpm = calcCpm(lvl)
    return int(math.floor(cpm * defe))

def calcDEFForPKMN(pk):
    basedef = pkgo_data.baseStats[pk['spec'].lower()][0]
    return calcHP(basedef + pk['ivdef'], pk['level'])

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
    pk['spec'] = pk['spec'].lower()
    
    return pk

def PKMNToStr(pk):
    if pk['ivsta'] != None and pk['ivatk'] != None and pk['ivdef'] != None:
        ivsum = pk['ivsta'] + pk['ivatk'] + pk['ivdef']
        return "Level {0} {1}, IVs STA {2:2}, ATK {3:2}, DEF {4:2}, total {5:2} ({6:.1%}) ({2:x}{3:x}{4:x})".format(pk['level'], pk['spec'].capitalize(), pk['ivsta'], pk['ivatk'], pk['ivdef'], ivsum, ivsum / 45.0)
    else:
        return "Level {0} {1}, IVs unknown!".format(pk['level'], pk['spec'].capitalize())

def exportMonToPokebattler(pk, f):
    fields = []
    # pokemon
    fields.append(pk['spec'].upper())
    # name
    fields.append("")
    # cp
    fields.append(str(calcCPForPKMN(pk)))
    # level
    fields.append(str(pk['level']))
    # individualAttack
    fields.append(str(pk['ivatk']))
    # individualDefense
    fields.append(str(pk['ivdef']))
    # individualStamina
    fields.append(str(pk['ivsta']))
    # quickMove
    fields.append("Dragon tail")
    # cinematicMove
    fields.append("outrage")
    # shiny
    fields.append("FALSE")
    # lucky
    fields.append("FALSE")
    f.write(",".join(fields) + "\n")

def exportMonsToPokebattler(pks, f):
    f.write("pokemon,nickname,cp,level,AttackIV,DEFIV,HPIV,fastmove,specialmove,shiny,lucky\n")
    for pk in pks:
        exportMonToPokebattler(pk, f)

