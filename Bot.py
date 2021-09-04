"""

ACC Discord Bot

Objectives:
	1. To automatically announce when scheduled races are happening.
	2. To give summaries of races.
	3. To give the overall standings.
	4. To give best lap times (overall and per user)
	5. Other fun ideas
	
"""

### Import dependencies

import json
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import ACC_CustomCommands as ACC
from datetime import datetime

import nest_asyncio
nest_asyncio.apply()

### Load tokens and relative info

with open('discord_ids.json') as json_file:
	disIDs = json.load(json_file)
	json_file.close()

TOKEN = disIDs['DISCORD_TOKEN']
SERVER = disIDs['DISCORD_SERVER']
SHEET = disIDs['GOOGLE_SHEET']
IMAGES = disIDs['RESULTS_IMAGES']
ADMIN_IDS = disIDs['ADMIN_ROLES']
SCHEDULE = disIDs['SCHEDULE']



print(f'{TOKEN} \n{SERVER}')

### INITIALISE BOT

bot = commands.Bot(command_prefix='!')

### DEFINE BOT EVENTS

@bot.event
async def on_ready():
	print(f'{bot.user.name} has connected to Discord!')
	
@bot.event
async def on_message(message):
	if message.author == bot.user:
		return
	if (not message.content.startswith('!') and
			message.author.id in disIDs['KEKW_USER_ID'] and
			message.channel.id in disIDs['DISCORD_CHANNELS']):
			#Ignores commands and targets specific users & channel

		emoji = discord.utils.get(message.guild.emojis, name='KEKW')
		await message.add_reaction(emoji)
		print(f'Reacted to {message.author} on {ctx.message.guild} in {ctx.message.channel.name} with KEKW')
	await bot.process_commands(message)

### BOT COMMANDS

@bot.command(name='test', pass_context=True, help='Test command to make sure the bot is working')
async def test_response(ctx):
	response = 'This is a test'
	if ctx.message.author.id in disIDs:
		emoji = discord.utils.get(ctx.message.guild.emojis, name='KEKW')
		print(f'Replied KEKW to {ctx.message.author}')
		await ctx.message.add_reaction(emoji)
		return
	await ctx.send(response + f' {ctx.message.author.mention}!')
	print(f'Replied to {ctx.message.author} on {ctx.message.guild} in {ctx.message.channel.name}')

@bot.command(name='standings', pass_context=True, help="Returns the current league standings.")
async def standings(ctx):
	figurename = "CurrentStandings.png"
	response = f'{ctx.message.author.mention}, the current standings are:'
	await ctx.send(response)
	await ctx.channel.send(file=discord.File(figurename))
	print(f"Gave standings to {ctx.message.author} on {ctx.message.guild} in {ctx.message.channel.name}")

@bot.command(name='raceresults', pass_context=True, help="Returns the results of all of the races so far.")
async def total_results(ctx):
	figurename = "RaceResults.png"

	response = f'{ctx.message.author.mention}, the current results are:'
	await ctx.send(response)
	await ctx.channel.send(file=discord.File(figurename))
	print(f"Gave total results to {ctx.message.author} on {ctx.message.guild} in {ctx.message.channel.name}")

@bot.command(name='times', pass_context=True, help="Returns the best laps.")
async def times(ctx):
	figurename = "BestTimes.png"

	response = f'{ctx.message.author.mention}, the current fastest times are:'
	await ctx.send(response)
	await ctx.channel.send(file=discord.File(figurename))
	print(f"Gave times to {ctx.message.author} on {ctx.message.guild} in {ctx.message.channel.name}")

@bot.command(name="update", pass_context=True, help="Admin command to update figures. Arguments are: [all, standings, results, times, when]. \n Default is all. \"when\" returns last update.")
async def update_figures(ctx, sections: str = 'all'):
	if (ADMIN_IDS in [y.id for y in ctx.message.author.roles] or
			ctx.message.author.guild_permissions.administrator):
		if sections == "when":
			response = ""
			for key, value in IMAGES.items():
				date = datetime.strptime(value, '%Y-%m-%d-%H:%M:%S')
				response += f'{key} : {date.strftime("%H:%M:%S on %d %b %Y")}\n'
			await ctx.send(response)
			return
		try:
			updated_images = ACC.UpdateFigures(SHEET, sections)
			for i in updated_images.updated_images:
				IMAGES[i] = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
				disIDs["RESULTS_IMAGES"][i] = IMAGES[i]

			with open('discord_ids.json', "w") as json_file:
				json.dump(disIDs, json_file, indent=4)
				json_file.close()

			await ctx.send(f'{ctx.message.author.mention} \n Successfully updated "{sections}"!')
			print(f"Updated {sections} for {ctx.message.author} on {ctx.message.guild} in {ctx.message.channel.name}")
		except Exception as exception_message:
			print(exception_message)
			await ctx.send(f"Unknown argument {ctx.message.author.mention}.")
			return

@bot.command(name='schedule', pass_context=True, help="Know the schedule of upcoming races.")
async def schedule(ctx):
	response = f"{ctx.message.author.mention}, the current schedule is:\n\n"
	for key, value in SCHEDULE.items():
		date = datetime.strptime(value, '%Y-%m-%d-%H:%M:%S')
		response += f'{key} on {date.strftime("%A %d %B")} at {date.strftime("%I:%M %p")}\n'
	await ctx.send(response)
	print(f"Gave the schedule to {ctx.message.author} on {ctx.message.guild} in {ctx.message.channel.name}")

bot.run(TOKEN)