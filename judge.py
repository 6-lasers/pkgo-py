######################################################
#
#    judge.py
#
#  IV judge for Pokemon GO.
#
######################################################

import discord
import asyncio

import os
import json

import yaml

import pkgo_data
import pkgo_pkmn
import pkgo_appraise


from discord.ext.commands import Bot
import time
from time import strftime

# import spelling

# Append path of this script to the path of
# config files which we're loading.
# Assumes that config files will always live in the same directory.
dataDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "gameData")

config = {}
teamAppraisal = {}
def load_config():
    global config
    global teamAppraisal
    
    # Load configuration
    with open("config.json", "r") as fd:
        config = json.load(fd)
    
    baseStatsName = os.path.join(dataDir, "baseStats.yml")
    dustJsonName = os.path.join(dataDir, "dust-to-level.json")
    levelToCpmName = os.path.join(dataDir, "level-to-cpm.json")
    teamAppraisalName = os.path.join(dataDir, "team_appraisal.json")
    
    baseStatsFile = open(baseStatsName, "r")
    pkgo_data.baseStats = yaml.load(baseStatsFile)
    baseStatsFile.close()
    
    dustJsonFile = open(dustJsonName, "r")
    pkgo_data.dustJson = json.load(dustJsonFile)
    dustJsonFile.close()
    
    levelToCpmFile = open(levelToCpmName, "r")
    pkgo_data.levelToCpm = json.load(levelToCpmFile)
    levelToCpmFile.close()
    
    teamAppraisalFile = open(teamAppraisalName, "r")
    teamAppraisal = json.load(teamAppraisalFile)
    teamAppraisalFile.close()

load_config()

# def spellcheck(word):
    # suggestion = spelling.correction(word)
    
    # # If we have a spellcheck suggestion
    # if suggestion != word:
        # return "\"{0}\" is not a Pokemon! Did you mean \"{1}\"?".format(word, spelling.correction(word))
    # else:
        # return "\"{0}\" is not a Pokemon! Check your spelling!".format(word)


Judge = Bot(command_prefix=config['default_prefix'])

def check_channel(channel):
    ret = True
    if 'iv_channels' in config and config['iv_channels'] and channel not in config['iv_channels']:
        ret = False
    return ret

"""

======================

End helper functions

======================

"""

@Judge.event
async def on_ready():
    #prints to the terminal or cmd prompt window upon successful connection to Discord
    print("""This Pokemon...has relatively superior...
*ya-a-awn*
...Who are you?

!

Someone impressive enough to shock me awake!
""")


@Judge.command(pass_context = True)
async def team_help(ctx):
    """Print help about team leader messages.
    
    Usage: !team_help <team name>"""
    
    if check_channel(ctx.message.channel.name):
        team_name = ctx.message.content.split(" ")[1]
        
        if team_name.lower() in teamAppraisal:
            # help_msg = "\n".join(["{0}: {1}]")
            
            helpmsg = "```{0} team appraisal messages (overall):\n\n".format(team_name.capitalize())
            for i, entry in enumerate(teamAppraisal[team_name]['overall']):
                helpmsg += "  {0}: {1}\n".format(i, entry)
            
            helpmsg += "\n{0} team appraisal messages (individual stats):\n\n".format(team_name.capitalize())
            for i, entry in enumerate(teamAppraisal[team_name]['indiv']):
                helpmsg += "  {0}: {1}\n".format(i, entry)
            
            helpmsg += "```"
        else:
            helpmsg = "{0} isn't a team name!".format(team_name)
        
        await Judge.send_message(ctx.message.channel, helpmsg)

@Judge.command(pass_context = True)
async def appraisal_help(ctx):
    """Print help about appraisals.
    
    Usage: !appraisal_help"""
    
    if check_channel(ctx.message.channel.name):
        helpmsg = """```Appraisal help:
        <Overall appraisal>: The first message your team leader says when you appraise your Pokemon in-game.
            A number from 0-3. For the translation table, please use !team_help <team name>, e.g. !team_help mystic
        
        <highest stat appraisal>: The second message your team leader says when you appraise your Pokemon in-game.
            Any of 'h' (STA), 'a' (ATK), or 'd' (DEF). Indicates what a Pokemon's best stat is.
        
        <highest stat type>: The third message your team leader says when you appraise your Pokemon in-game.
            A number from 0-3. For the translation table, please use !team_help <team name>, e.g. !team_help mystic
            
        <*hatched/powered>:
            A string consisting of the letters "h" and/or "p". "h" indicates the Pokemon was hatched, and "p" indicates you've powered up the Pokemon since obtaining it.
            This helps the IV Judge more accurately identify the Pokemon's strength.
            If Pokemon is neither hatched nor powered up, can be omitted.```"""
        
        await Judge.send_message(ctx.message.channel, helpmsg)

@Judge.command(pass_context = True)
async def iv(ctx):
    """Check IV of a Pokemon.
    
    Usage: !iv <species> <iv> <hp> <power up cost (in 100s)> <overall appraisal> <highest stat appraisal> <highest stat type> <(optional) hatched/powered>
    
    """
    
    if check_channel(ctx.message.channel.name):
        line = ctx.message.content.split(" ", 1)[1]
        
        # Convert lines to appraisals
        appr = pkgo_appraise.lineToAppr(line)
        
        try:
            # Check IVs for each appraisal
            response =  "PKMN {0}: ({1} CP {2}):\n".format(ctx.message.author.mention, appr['spec'], appr['cp'])
            pkarr = pkgo_appraise.matchApprIVs(appr)
            if pkarr:
                for pk in pkarr:
                    response += "Possible match: {0}\n".format(pkgo_pkmn.PKMNToStr(pk))
            else:
                response += "No matches! Please double check your request for typos, or check if your Pokemon has been powered up.\n"
        except KeyError as e:
            response = "{0} is not a Pokemon species!\n".format(appr['spec'])
        
        await Judge.send_message(ctx.message.channel,  response)


Judge.run(config['bot_token'])
