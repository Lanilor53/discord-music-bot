from discord.ext import commands
from discord import FFmpegOpusAudio
from util import youtube_handler
# TODO: move join and leave commands, they don't belong here


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_song = None
        self.loop = False
        self.current_vc = None
        self.queue = []

    def _play_song(self, song):
        """
        Start playing the given song
        """

        # Get audio stream
        audio = FFmpegOpusAudio(song.url,
                                before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 "
                                               "-fflags +discardcorrupt")
        # Play!
        self.current_song = song
        self.current_vc.play(audio, after=self._on_play_end)

    def _on_play_end(self, error):
        """
        Callback function that triggers when playback ends
        """

        if self.loop:
            self._play_song(self.current_song)
        else:
            if len(self.queue) > 0:
                song = self.queue.pop(0)
                self._play_song(song)
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
        Search YouTube and add the requested video to queue
        """

        # Join if not already in a channel
        if ctx.guild.voice_client is None or not ctx.guild.voice_client.is_connected:
            channel = ctx.author.voice.channel
            await channel.connect()
            self.current_vc = ctx.guild.voice_client

        # Find song
        arg = " ".join(args)
        video = await youtube_handler.get_first_video_link(arg)
        song = video.getbestaudio()

        # If there is a song playing - add to queue
        if self.current_song is not None:
            self.queue.append(song)
            await ctx.channel.send(f"Added to queue: {song.title}\n\nPosition: {len(self.queue)}")
        # Else start playing immediately
        else:
            await ctx.channel.send(f"Playing: {video.title}")
            self._play_song(song)

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
            await ctx.channel.send("Looping the song")

    @commands.command(aliases=["l"])
    async def leave(self, ctx):
        """
        Leave the current voice channel
        """

        self.current_song = None
        self.loop = False
        self.current_vc = None
        self.queue = []
        await ctx.guild.voice_client.disconnect()

    @commands.command(aliases=["queue", "q"])
    async def show_queue(self, ctx):
        if len(self.queue) == 0:
            await ctx.channel.send("Nothing queued")
        else:
            await ctx.channel.send(f"Playing: {self.current_song.title}\nQueue:\n"+'\n'.join([i.title for i in self.queue]))

    @join.error
    async def join_error(self, ctx, error):
        """
        Gives a tip on what can be wrong when join command fails
        """

        if isinstance(error, commands.errors.ClientException):
            await ctx.send("ClientException: already connected to a voice channel?")
        else:
            raise error
