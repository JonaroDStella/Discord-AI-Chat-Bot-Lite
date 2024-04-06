import discord
from discord.ext import commands
from userdb import UserDB
from config import *
from utils import *


client = commands.Bot(command_prefix=COMMAND_PREFIX,
                      intents=discord.Intents.all())
history = []
userdb = UserDB()


@client.event
async def on_ready():
    print(f'Login as {client.user}')


@client.listen('on_message')
async def on_message(message: discord.Message):
    global history
    if message.author == client.user:
        return

    if message.content.startswith(CHAT_PREFIX):
        data = userdb.get_user(message.author.id)
        content = message.content[len(CHAT_PREFIX):]
        print(f'{message.author.name}: {content}')
        reply = await make_completion(data, content)
        print(f'{client.user.name}: {reply}')

        voice = discord.utils.get(client.voice_clients, guild=message.guild)
        if voice:
            async with message.channel.typing():
                await Voice(voice, data['voice_id'], reply)

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


@client.command(name='show')
async def show(ctx: commands.Context, *args):
    data = userdb.get_user(ctx.author.id)
    output = ''
    if len(args) == 0:
        args = data.keys()
    for name in args:
        output += f'\n{name}: {data[name]}'
    await ctx.channel.send(f'```{output}```')


@client.command(name='set')
async def set(ctx: commands.Context, *args):
    response = userdb.set_data(ctx.author.id, args[0], ' '.join(args[1:]))
    await ctx.channel.send(response)

client.run(TOKEN)
