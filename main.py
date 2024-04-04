import discord
from discord.ext import commands
from config import *
from utils import *


client = commands.Bot(command_prefix=COMMAND_PREFIX,
                      intents=discord.Intents.all())
history = []


@client.event
async def on_ready():
    print(f'Login as {client.user}')


@client.listen('on_message')
async def on_message(message: discord.Message):
    global history
    if message.author == client.user:
        return

    if message.content.startswith(CHAT_PREFIX):
        content = message.content[len(CHAT_PREFIX):]
        print(f'{message.author.name}: {content}')
        if len(history) > HISTORY_LIMIT:
            history = history[-HISTORY_LIMIT:]
        history.append({'role': 'user',
                        'content': content})
        reply = await make_completion([{'role': 'system',
                                        'content': PROMPT}] + history)
        history.append({"role": "assistant",
                        "content": reply})
        print(f'{client.user.name}: {reply}')
        voice = discord.utils.get(client.voice_clients, guild=message.guild)

        if voice:
            async with message.channel.typing():
                await Voice(voice, VOICE_ID, reply)

        for splited in split_message(reply):
            await message.channel.send(splited)


@client.command(name='join')
async def join(ctx: commands.Context):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if ctx.author.voice == None:
        await ctx.channel.send("You are not connected to any voice channel")
    elif voice == None:
        voiceChannel = ctx.author.voice.channel
        await voiceChannel.connect()
    else:
        await ctx.channel.send("Already connected to a voice channel")


@client.command(name='leave')
async def leave(ctx: commands.Context):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice == None:
        await ctx.channel.send("The Bot is not connected to a voice channel")
    else:
        await voice.disconnect()

client.run(TOKEN)
