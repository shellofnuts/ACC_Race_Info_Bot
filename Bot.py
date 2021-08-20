"""

ACC Discord Bot

Objectives:
	1. To automatically announce when scheduled races are happening.
	2. To give summaries of races.
	3. To give the overall standings.
	4. To give best lap times (overall and per user)
	5. Other fun ideas
	
"""

### Import dependenies


import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import ACC_CustomCommands as ACC

import nest_asyncio
nest_asyncio.apply()

### Load tokens and relative info

load_dotenv("discord_tokens.env")
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER = os.getenv('DISCORD_SERVER')

print(f'{TOKEN} \n{SERVER}')

### INITIALISE BOT

bot = commands.Bot(command_prefix='!')

### Discord IDs

disIDs = [761495523898556427, 246290545348050945, 374245587387809793]

### BOT EVENTS

@bot.event
async def on_ready():
	print(f'{bot.user.name} has connected to Discord!')
	
@bot.event
async def on_message(message):
	if message.author == bot.user:
		return
	if not message.content.startswith('!') and message.author.id in disIDs and message.channel.id == 876749209339047936: 	#	Ignores commands
		emoji = discord.utils.get(message.guild.emojis, name='KEKW')
		await message.add_reaction(emoji)
		print(f'Reacted to {message.author} with KEKW')
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
	print(f'Replied to {ctx.message.author}')

@bot.command(name='standings', pass_context=True, help="Returns the current league standings!")
async def standings(ctx):
	await ctx.send('Grabbing data...')

	results = ACC.PullData('Celbridge ACC Points', 0)
	results.authClient()
	figure = ACC.Standings(results.getDataFrame())
	figure.getTable()
	figurename = figure.output

	response = f'{ctx.message.author.mention}, the current standings are:'
	await ctx.send(response)
	await ctx.channel.send(file=discord.File(figurename))
	os.remove(figurename)
	print(f"Gave standings to {ctx.message.author}")

@bot.command(name='raceresults', pass_context=True, help="Returns the results of all of the races so far!")
async def total_results(ctx):
	await ctx.send('Grabbing data...')

	results = ACC.PullData('Celbridge ACC Points', 0)
	results.authClient()
	figure = ACC.RaceResults(results.getDataFrame())
	figure.getTable()
	figurename = figure.output

	response = f'{ctx.message.author.mention}, the current results are:'
	await ctx.send(response)
	await ctx.channel.send(file=discord.File(figurename))
	os.remove(figurename)
	print(f"Gave total results to {ctx.message.author}")

@bot.command(name='times', pass_context=True, help="Returns the best laps!")
async def times(ctx):
	await ctx.send('Grabbing data...')

	timedata = ACC.PullData('Celbridge ACC Points', 1)
	timedata.authClient()
	figure = ACC.BestTimes(timedata.getDataFrame())
	figure.getTable()
	figurename = figure.output

	response = f'{ctx.message.author.mention}, the current fastest times are:'
	await ctx.send(response)
	await ctx.channel.send(file=discord.File(figurename))
	os.remove(figurename)
	print(f"Gave times to {ctx.message.author}")

bot.run(TOKEN)