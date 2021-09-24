from youtubesearchpython.__future__ import VideosSearch

import asyncio

import discord
from discord.ext import commands
import pafy
import urllib
import os

# GLOBALS
# Prepare the bot
bot = commands.Bot(command_prefix='^')
current_song = None
loop = False
current_vc = None

@bot.command(aliases=["j"])
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()


@bot.command(aliases=["loop"])
async def loop_song(ctx):
    global loop
    if loop:
        loop = False
        await ctx.channel.send("No longer looping")
    else:
        loop = True
        await ctx.channel.send("Looping")


@bot.command(aliases=["l"])
async def leave(ctx):
    await ctx.guild.voice_client.disconnect()


def _on_play_end(error):
    global current_song
    global current_vc
    print(f"Play end, error:{error}")
    if loop:
        audio = discord.FFmpegOpusAudio(current_song.url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -fflags +discardcorrupt")
        current_vc.play(audio, after=_on_play_end)
    else:
        current_song = None
    # todo: find a way to get ctx here for server-wide queue?


@bot.command(aliases=["p"])
async def play(ctx, *args):
    global current_song
    global current_vc
    # Join if not already in a channel
    if ctx.guild.voice_client is None or not ctx.guild.voice_client.is_connected:
        channel = ctx.author.voice.channel
        await channel.connect()
    if current_song is not None:
        await ctx.channel.send("Already playing!")
    else:
        # Find video
        arg = " ".join(args)
        videos_search = VideosSearch(arg, limit=1)
        videos_result = await videos_search.next()
        video = pafy.new(videos_result["result"][0]["link"])
        await ctx.channel.send(f"Trying to play {video.title}")
        # Get audio stream
        current_song = video.getbestaudio()
        audio = discord.FFmpegOpusAudio(current_song.url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -fflags +discardcorrupt")
        # Play!
        current_vc = ctx.guild.voice_client
        current_vc.play(audio, after=_on_play_end)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.channel.send("No such command")
    else:
        await ctx.channel.send("Something went wrong while executing command")
        raise error


@join.error
async def join_error(ctx, error):
    if isinstance(error, commands.errors.ClientException):
        await ctx.send("ClientException: already connected to a voice channel?")
    else:
        raise error


@bot.command(aliases=["s"])
async def skip(ctx):
    global loop
    if loop:
        loop = False
    ctx.guild.voice_client.stop()


if __name__ == "__main__":
    try:
        token = os.environ["BOT_TOKEN"]
    except:
        print("BOT_TOKEN env var not found, aborting.")
        exit(-1)
    bot.run(token)
