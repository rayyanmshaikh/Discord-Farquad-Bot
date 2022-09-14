from lib2to3.pgen2 import token
import discord
from discord.ext import commands, tasks
import os
from itertools import cycle

intents = discord.Intents.all()
client = commands.Bot(command_prefix='.',intents=intents)
status = cycle(['Snoozing', 'Working', 'Finding Shrek'])
config = open("config.txt", "r").readline()


@client.event
async def on_ready():
    change_status.start()
    print(f'We have logged in as {client.user}')


@tasks.loop(hours=1)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))


@client.event
async def on_member_join(member):
    print(f'{member} has joined {member.server}')


@client.event
async def on_member_remove(member):
    print(f'The peasant {member} couldn\'t handle this Lord')


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Missing argument')
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send('Invalid Command')
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('Naughty naughty')


@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')


@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5, member: discord.Member = None):
    if member is None:
        await ctx.channel.purge(limit=amount)
    else:
        msgs = [message async for message in ctx.channel.history(limit=amount)
                if message.author == member]
        for i in msgs:
            await i.delete()


@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member = None, *, reason='You were bad'):
    if member is None:
        await ctx.send('You forgot to @ a user')
    else:
        await member.kick(reason=reason)
        await ctx.send(f'Kicked {member.mention}')


@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member = None, *, reason='You were bad'):
    if member is None:
        await ctx.send('You forgot to @ a user')
    else:
        await member.ban(reason=reason)
        await ctx.senf(f'Banned {member.mention}')


@client.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
    banned = await ctx.guild.bans()
    member_name, member_disc = member.rsplit('#')

    for entry in banned:
        user = entry.user
        if (user.name, user.discriminator) == (member_name, member_disc):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.name}#{user.discriminator}')
            return


@client.command()
@commands.is_owner()
async def load(ctx, extension):
    await client.load_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} is loaded')


@client.command()
@commands.is_owner()
async def unload(ctx, extension):
    await client.unload_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} is unloaded')


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


client.run(config)
