import discord
from discord.ext import commands
import os
from cogs.music import Music

# Prepare the bot
bot = commands.Bot(command_prefix='^')

if __name__ == "__main__":
    try:
        token = os.environ["BOT_TOKEN"]
    except:
        print("BOT_TOKEN env var not found, aborting.")
        exit(-1)
    # Load functionality
    bot.add_cog(Music(bot))

    bot.run(token)
