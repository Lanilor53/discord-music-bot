from youtubesearchpython.__future__ import VideosSearch

from discord.ext import commands
import pafy
from discord import FFmpegOpusAudio
# TODO: move join and leave commands, they don't belong here


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_song = None
        self.loop = False
        self.current_vc = None

    def _on_play_end(self, error):
        """
        Callback function that triggers when playback ends
        """

        if self.loop:
            audio = FFmpegOpusAudio(self.current_song.url,
                                    before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 "
                                                   "-fflags +discardcorrupt")
            self.current_vc.play(audio, after=self._on_play_end)
        else:
            self.current_song = None

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """
        Send a message on command error
        """

        if isinstance(error, commands.CommandNotFound):
            await ctx.channel.send("No such command")
        else:
            await ctx.channel.send("Something went wrong while executing command")
            raise error

    @commands.command(aliases=["p"])
    async def play(self, ctx, *args):
        """
        Searches YouTube and plays the requested video
        """

        # Join if not already in a channel
        if ctx.guild.voice_client is None or not ctx.guild.voice_client.is_connected:
            channel = ctx.author.voice.channel
            await channel.connect()
        if self.current_song is not None:
            await ctx.channel.send("Already playing!")
        else:
            # Find video
            arg = " ".join(args)
            videos_search = VideosSearch(arg, limit=1)
            videos_result = await videos_search.next()
            video = pafy.new(videos_result["result"][0]["link"])
            await ctx.channel.send(f"Trying to play {video.title}")
            # Get audio stream
            self.current_song = video.getbestaudio()
            audio = FFmpegOpusAudio(self.current_song.url,
                                    before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 "
                                                   "-fflags +discardcorrupt")
            # Play!
            self.current_vc = ctx.guild.voice_client
            self.current_vc.play(audio, after=self._on_play_end)

    @commands.command(aliases=["s"])
    async def skip(self, ctx):
        """
        Skip the current played song and stop looping
        """

        if self.loop:
            self.loop = False
        ctx.guild.voice_client.stop()

    @commands.command(aliases=["j"])
    async def join(self, ctx):
        """
        Join the voice channel that the command-issuing user is in
        """

        channel = ctx.author.voice.channel
        await channel.connect()

    @commands.command(aliases=["loop"])
    async def loop_song(self, ctx):
        """
        Loop the current played song
        """

        if self.loop:
            self.loop = False
            await ctx.channel.send("No longer looping")
        else:
            self.loop = True
            await ctx.channel.send("Looping")

    @commands.command(aliases=["l"])
    async def leave(self, ctx):
        """
        Leave the current voice channel
        """

        await ctx.guild.voice_client.disconnect()

    @join.error
    async def join_error(self, ctx, error):
        """
        Gives a tip on what can be wrong when join command fails
        """

        if isinstance(error, commands.errors.ClientException):
            await ctx.send("ClientException: already connected to a voice channel?")
        else:
            raise error
