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

import nest_asyncio
nest_asyncio.apply()

### Load tokens and relative info

load_dotenv("discord_tokens.env")
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER = os.getenv('DISCORD_SERVER')

print(TOKEN, SERVER)

### Run Bot

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
	
@bot.event
async def on_message(message):
	if message.author == bot.user:
		return
	if not message.content.startswith('!'):
		await message.add_reaction('\N{EYES}')
	await bot.process_commands(message)
	

@bot.command(name='test', pass_context=True)
async def test_response(ctx):
	response = 'This is a test'
	await ctx.send(response + f' {ctx.message.author.mention}!')
	print(f'Replied to {ctx.message.author}')

bot.run(TOKEN)