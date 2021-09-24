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


@bot.command(aliases=["j"])
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()


@bot.command(aliases=["l"])
async def leave(ctx):
    await ctx.guild.voice_client.disconnect()


def _on_play_end(error):
    # todo: find a way to get ctx here for server-wide queue? maybe in error?
    pass


@bot.command(aliases=["p"])
async def play(ctx, *args):
    # Join if not already in a channel
    if ctx.guild.voice_client is None or not ctx.guild.voice_client.is_connected:
        channel = ctx.author.voice.channel
        await channel.connect()
    # Find video
    arg = " ".join(args)
    videos_search = VideosSearch(arg, limit=1)
    videos_result = await videos_search.next()
    video = pafy.new(videos_result["result"][0]["link"])
    await ctx.channel.send(f"Trying to play {video.title}")
    # Get audio stream
    best_audio = video.getbestaudio()
    audio = discord.FFmpegOpusAudio(best_audio.url, before_options="-fflags +discardcorrupt")
    # Play!
    ctx.guild.voice_client.play(audio, after=_on_play_end)


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
    ctx.guild.voice_client.stop()


if __name__ == "__main__":
    try:
        token = os.environ["BOT_TOKEN"]
    except:
        print("BOT_TOKEN env var not found, aborting.")
        exit(-1)
    bot.run(token)
