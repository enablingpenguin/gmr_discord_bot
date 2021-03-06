# bot.py
import os
import requests
import json
import csv
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

def find_mentionstr(gmrname):
    with open("users.csv", "r") as infile:
        reader = csv.reader(infile)
        next(reader)
        for line in reader:
            if [gmrname] == line[:1]:
                return line[1:][0]

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.casefold() == '!GMR'.casefold():
        site_request = requests.get(os.getenv('GMR_URL'))
        jsonResponse = site_request.json()
        currentturn = jsonResponse["Games"][0]["CurrentTurn"]["UserId"]
        expires = jsonResponse["Games"][0]["CurrentTurn"]["Expires"]
        playerdata = jsonResponse["Players"]

        for player in playerdata:
            playerid = player["SteamID"]
            if playerid == currentturn:
                name = player["PersonaName"]
                break
        mentionstr = find_mentionstr(str(name))
        if mentionstr == None:
            response = "**Current Turn:** " + str(name) + "\n**Expires:** " + expires
            await message.channel.send(response)
        else:
            response = mentionstr + "\n**Current Turn:** " + str(name) + "\n**Expires:** " + expires
            await message.channel.send(response)
        
    if message.content.casefold().startswith('!GMR@ME'.casefold()):
        mentionstr = str(message.author.mention)
        gmrname = message.content[8:]
        site_request = requests.get(os.getenv('GMR_URL'))
        jsonResponse = site_request.json()
        playerdata = jsonResponse["Players"]
        userexists = "false"
        for player in playerdata:
            if player["PersonaName"] == gmrname:
                userexists = "true"
        try:
            if userexists == "false":
                raise Exception()
            with open('users.csv', mode='a') as usercsv:
                usercsv_writer = csv.writer(usercsv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                usercsv_writer.writerow([gmrname, mentionstr])
            response = "I will mention " + mentionstr + " when it is " + gmrname + "'s turn"
            await message.channel.send(response)
        except:
            response = "Something went wrong, try again\n**Proper use:**\n!GMR@ME [Steam Name Here]"
            await message.channel.send(response)

client.run(TOKEN)
