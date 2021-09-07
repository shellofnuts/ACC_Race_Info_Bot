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
import ACC_CustomCommands as ACC
from datetime import datetime

import nest_asyncio
nest_asyncio.apply()

### Load tokens and relative info

token_directory = 'Tokens/'

with open(token_directory+'discord_ids.json') as json_file:
	disIDs = json.load(json_file)
	json_file.close()

TOKEN = disIDs['DISCORD_TOKEN']
SERVER = disIDs['DISCORD_SERVER']
SHEET = disIDs['GOOGLE_SHEET']
IMAGES = disIDs['RESULTS_IMAGES']
ADMIN_IDS = disIDs['ADMIN_ROLES']
SCHEDULE = disIDs['SCHEDULE']
GOOGLE_TOKEN = disIDs['GOOGLE_TOKEN_NAME']



print(f'{TOKEN} \n{SERVER}')

### INITIALISE BOT

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

### DEFINE BOT EVENTS

@bot.event
async def on_ready():
	print(f'{bot.user.name} has connected to Discord!')
	
@bot.event
async def on_message(message):
	"""
	Function to react to specific users (in a specific channel) with a custom emoji. Just for fun.

	:param message: discord.Message object. Passes through the message and additional context information
	:return: None
	"""
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
	"""
	Function to update the league figures. Only accessible to certain roles defined in discord_ids.json.
	This is to reduce calls to Google API and increase response time with pre-made images. Matplotlib is also quite slow to produce tables.

	:param ctx: discord.Message object. Contains information on message and context.
	:param sections: Defines what to update. sections = 'all', 'standings', 'results', 'times' or 'when'
	:return: None. Will return a statement to the Discord user and output any errors to the console.
	"""
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
			updated_images = ACC.UpdateFigures(token_directory+GOOGLE_TOKEN, SHEET, sections)
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
			if exception_message.__str__() == 'Argument not in list':
				# Did the user input an incorrect argument?
				await ctx.send(f'Hey {ctx.message.author.mention}, you used the wrong argument.\nUse !help to see them.')
				return
			else:
				try:
					# Try to mention one of the league admins that a problem occurred.
					role_id = ADMIN_IDS[0]
					tech_role = discord.utils.get(ctx.guild.roles, id=role_id)
					await ctx.send(f'Hey {ctx.message.author.mention}, I got an error with that. Please let one of the {tech_role.mention}')
				except:
					# If league admins cannot be mentioned, tell user to inform server owner. (Server owner is not mentioned. Just don't @ server owners.)
					guild_owner: discord.Member = ctx.message.guild.owner
					await ctx.send(f'Hey {ctx.message.author.mention}, I got an error. Please inform the boss {guild_owner.display_name}.')
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