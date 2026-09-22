import discord
from discord.ext import commands as command
import configparser
import api
import music_commands
from player import PlayerState
from pathlib import Path
import json

# Create a ConfigParser object
config = configparser.ConfigParser()

# Read the config file
config.read('config.cfg')

#api
port = config.getint('API', 'port')

TOKEN = config.get('Bot', 'TOKEN')
VERSION = config.get('VERSION', 'version')
voice_channel = config.getint('Bot', 'voice_channel_id')
text_channel = config.getint('Bot', 'text_channel_id')
server_url = config.get('JellyFin', 'url')  # Replace with your Jellyfin server URL
api_key = config.get('JellyFin', 'api_key')  # Your Jellyfin API key
download_urls = (
    server_url + "/Items/<id>/Download?api_key=" + api_key
)  # Replace with your actual URL
ffmpeg_path = config.get('FFMPEG', 'ffmpeg_path')
ffmpeg_path_required = config.getboolean('FFMPEG', 'ffmpeg_path_required')

music_player = PlayerState()
intents = discord.Intents.default()
intents.message_content = True
bot = command.Bot(command_prefix="!", intents=intents)
music_commands.setup(bot, music_player, VERSION)
api.setup(music_player)
bot.remove_command('help')

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await music_commands.helpers.startUp()



@bot.command()
async def help(ctx):
    '''Lists all available commands'''
    embed = discord.Embed(
        title="List of available commands",
        color=discord.Color.dark_blue()
    )
    embed.set_footer(text="Bot Developed By Blaik Network\n© Copyright Blaik Network 2026")
    
    # Adding fields with inline=True creates the columns
    embed.add_field(name="!clearqueue", value="Command to clear the queue", inline=False)
    embed.add_field(name="!help", value="Shows this message", inline=False)
    embed.add_field(name="!instantmix", value="Command to add a instantmix to the queue", inline=False)
    embed.add_field(name="!loop", value="Command to loop a song", inline=False)
    embed.add_field(name="!play", value="Command to add a song/s to the queue", inline=False)
    embed.add_field(name="!playall", value="Command to play all the songs in the list one by one", inline=False)
    embed.add_field(name="!queue", value="Command to show what is currently in the queue", inline=False)
    embed.add_field(name="!randomplaylist", value="Command to add multiple songs to the queue based on album, artist or random song", inline=False)
    embed.add_field(name="!randomsong", value="Command to add a random song to the queue", inline=False)
    embed.add_field(name="!search", value="Command to search for songs based on the artist, album or song name", inline=False)
    embed.add_field(name="!skip", value="Command to skip the currently playing song", inline=False)
    embed.add_field(name="!songs", value="Command to list all the available songs", inline=False)
    embed.add_field(name="!stop", value="Command to stop any currently playing music", inline=False)
    embed.add_field(name="!updatesongs", value="Command to update the songs database for the bot", inline=False)
    embed.add_field(name="!version", value="Command to show the bot name and version", inline=False)
    embed.add_field(name="!playnext", value="Command to add a song/s next in the queue", inline=False)
    embed.add_field(name="!pause", value="Command to pause currently playing audio", inline=False)
    embed.add_field(name="!resume", value="Command to resume currently playing audio", inline=False)
    embed.add_field(name="!playnow", value="Command to add a song/s next in the queue and play them", inline=False)
    embed.add_field(name="!remove", value="Command to remove songs from the queue", inline=False)
    embed.add_field(name="!playlist", value="Command that adds playlist support, see !playlist usage for more info", inline=False)
    embed.add_field(name="!auth", value="Access web portal", inline=False)
    embed.add_field(name="!lookup", value="Command to lookup ids", inline=False)
    
    channel = bot.get_channel(text_channel)
    await channel.send(embed=embed)
       
@bot.command()
async def ping(ctx):
    """Command to make the bot leave the voice channel"""
    await music_commands.helpers.success("Pong!")


@bot.command()
async def play(ctx, *, song_name=""):
    '''Command to add a song/s to the queue.'''
    print(song_name)
    return await music_commands.play(song_name)


@bot.command()
async def playnext(ctx, *, song_name = ""):
    '''Command to add a song/s next in the queue.'''
    await music_commands.playnext(song_name)


@bot.command()
async def playnow(ctx, *, song_name = ""):
    '''Command to add a song/s next in the queue and play them.'''
    await music_commands.playnow(song_name)


@bot.command()
async def pause(ctx):
    '''Command to pause currently playing audio'''
    await music_commands.pause()
    


@bot.command()
async def resume(ctx):
    '''Command to resume currently playing audio'''
    await music_commands.resume()


@bot.command()
async def remove(ctx, *, song_name = ""):
    """Command to remove a song from the queue."""
    await music_commands.remove(song_name)
    
    
    
@bot.command()
async def version(ctx):
    '''Command to show JellyFin Music Bot Version'''
    # Check if the error is CommandNotFound
    await music_commands.helpers.success(f"Blaik Network JellyFin Music Bot Version: {VERSION}")


@bot.command()
async def randomsong(ctx):
    """Command to add a random song to the queue."""
    print("command: random song")
    await music_commands.randomsong()
    


@bot.command()
async def queue(ctx, page=1):
    """Command to show what is currently in the queue."""
    await music_commands.queue(page)
    


@bot.command()
async def clearqueue(ctx):
    '''Command to clear the queue.'''
    try: 
        await music_commands.clearqueue()
    except Exception as e:
        print(f"Error occurred while clearing queue: {e}")



@bot.command()
async def stop(ctx):
    '''Command to stop any currently playing music.'''
    print("stop command called...")
    try:
        await music_commands.stop()
    except Exception as e:
        print(f"Error occurred while stopping music: {e}")


@bot.command()
async def randomplaylist(ctx, *keywords: str):
    """Command to add multiple songs to the queue based on album, artist or random songs."""
    await music_commands.randomplaylist(keywords)
    


@bot.command()
async def skip(ctx):
    """Command to skip the currently playing song."""
    await music_commands.skip()

# Autocompletion for the song argument in play command
@bot.command()
async def songs(ctx, page: int = 1):
    """Command to list all available songs, paginated by 10 songs per page."""
    await music_commands.songs(page)
    


@bot.command()
async def playall(ctx):
    """Command to play all the songs in the list one by one."""
    await music_commands.playall()
    


@bot.command()
async def loop(ctx, *, song_name = " "):
    """Command to play loop a song from the list."""
    print("starting loop...")
    try:
        await music_commands.loop(song_name)
    except Exception as e:
        print(f"Error occurred while looping: {e}")
    


@bot.command()
async def search(ctx, *keywords: str):
    """Command to search for songs based on the artist, album or song name."""
    try:
        await music_commands.search(keywords)
    except Exception as e:
        print(f"Error occurred while searching: {e}")
    
    


@bot.command()
async def updatesongs(ctx):
    """Command to update the songs database for the bot."""
    await music_commands.updatesongs()
    



@bot.command()
async def instantmix(ctx, *keywords: str):
    '''Command to add an instantmix to the queue.'''
    await music_commands.instantmix(keywords)

@bot.command()
async def playlist(ctx, *keywords: str):
    '''Command to add an instantmix to the queue.'''
    userid = str(ctx.author.id)
    await music_commands.playlist(keywords, userid, discord=True)

@bot.command()
async def auth(ctx):
    userid = str(ctx.author.id)
    await music_commands.auth(ctx, userid)

@bot.command()
async def lookup(ctx, *, song_name=""):
    '''Command to add a song/s to the queue.'''
    return await music_commands.idLookup(song_name)


# Run the bot
print("Getting songs database from jellyfin server...")
if music_commands.helpers.getsongs():
    print("Got songs database successfully.")
else:
    print("Error getting songs database.")
print("Downloaded. Starting bot...")

async def main():
    await bot.start(TOKEN)

async def exit():
    await music_commands.helpers.exit()

