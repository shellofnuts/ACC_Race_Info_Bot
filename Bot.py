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

### BOT EVENTS

@bot.event
async def on_ready():
	print(f'{bot.user.name} has connected to Discord!')
	
@bot.event
async def on_message(message):
	if message.author == bot.user:
		return
	if not message.content.startswith('!') and message.author.id == 761495523898556427: 	#	Ignores commands
		emoji = discord.utils.get(message.guild.emojis, name='KEKW')
		await message.add_reaction(emoji)
		print(f'Reacted to {message.author} with KEKW')
	await bot.process_commands(message)

### BOT COMMANDS

@bot.command(name='test', pass_context=True)
async def test_response(ctx):
	response = 'This is a test'
	await ctx.send(response + f' {ctx.message.author.mention}!')
	print(f'Replied to {ctx.message.author}')

@bot.command(name='standings', pass_context=True)
async def standings(ctx):
	response = f'{ctx.message.author.mention}, the current standings are:'
	figure = ACC.Standings('RaceResults')
	figure.getTable()
	figurename = figure.output
	await ctx.send(response)
	await ctx.channel.send(file=discord.File(figurename))
	os.remove(figurename)
	print(f"Gave standings to {ctx.message.author}")

@bot.command(name='totalresults', pass_context=True)
async def total_results(ctx):
	response = f'{ctx.message.author.mention}, the current results are:'
	figure = ACC.RaceResults('RaceResults')
	figure.getTable()
	figurename = figure.output
	await ctx.send(response)
	await ctx.channel.send(file=discord.File(figurename))
	os.remove(figurename)
	print(f"Gave total results to {ctx.message.author}")

bot.run(TOKEN)