import configparser
import os 
import aiohttp
import discord
from discord import FFmpegPCMAudio
import requests

config = configparser.ConfigParser()

# Read the config file
config.read('config.cfg')

#api
port = config.getint('API', 'port')

TOKEN = config.get('Bot', 'TOKEN')
voice_channel = config.getint('Bot', 'voice_channel_id')
text_channel = config.getint('Bot', 'text_channel_id')
server_url = config.get('JellyFin', 'url')  # Replace with your Jellyfin server URL
api_key = config.get('JellyFin', 'api_key')  # Your Jellyfin API key
download_urls = (
    server_url + "/Items/<id>/Download?api_key=" + api_key
)
ffmpeg_path = config.get('FFMPEG', 'ffmpeg_path')
ffmpeg_path_required = config.getboolean('FFMPEG', 'ffmpeg_path_required')

player = None
bot = None

def setup(both, music_player):
    global bot, player
    bot = both
    player = music_player

# Function to get a list of songs in the directory
async def get_song_list():
    """Return a list of files in the song directory."""
    print("Getting song list...")
    song_list = player.song_list
    return song_list

async def getId(songed):
    song_list = await get_song_list()
    for song in song_list:
        Artists = song.get("Artists")
        Artist = Artists[0]
        songe = f"{song.get('Name')} | **Artist:** {Artist} | **Album:** {song.get('Album')} | **Id:** {song.get('Id')}"
        if songe == songed:
            print("The id is: " + song["Id"])
            return song["Id"]



async def embeded(status, songs):
    # Basic embed creation
    embed = discord.Embed(
        title=status,
        description=songs,
        color=discord.Color.dark_blue()
    )
    channel = bot.get_channel(text_channel)
    await channel.send(embed=embed)

async def success(status):
    # Basic embed creation
    embed = discord.Embed(
        description=status,
        color=discord.Color.green()
    )
    channel = bot.get_channel(text_channel)
    await channel.send(embed=embed)

async def errorr(status):
    await error(status)

async def error(status):
    # Basic embed creation
    embed = discord.Embed(
        title="Error!",
        description=status,
        color=discord.Color.red()
    )
    channel = bot.get_channel(text_channel)
    await channel.send(embed=embed)

async def song(songed):
    song_list = await get_song_list()
    for song in song_list:
        Artists = song.get("Artists")
        Artist = Artists[0]
        songe = f"{song.get('Name')} | **Artist:** {Artist} | **Album:** {song.get('Album')} | **Id:** {song.get('Id')}"
        if songe == songed:
            print("The id is: " + song["Id"])
            return (song["Id"])

    print("Song: " + str(songed) + " not found")
    return False

async def song2(songed):
    song_list = await get_song_list()
    for song in song_list:
        Artists = song.get("Artists")
        Artist = Artists[0]
        songe = f"{song.get('Name')} | **Artist:** {Artist} | **Album:** {song.get('Album')} | **Id:** {song.get('Id')}"
        if songe == songed:   
            return song

    print("Song: " + str(songed) + " not found")
    return None

async def nowplayingEmbed(songe):
        song = await song2(songe)
        if song is None:
            return
        song_name = song.get('Name')
        album = song.get("Album")
        artists_array = song.get("Artists")
        artist = artists_array[0]
        albumId = song.get("AlbumId")
        albumart = f"{server_url}/Items/{albumId}/Images/Primary?width=256&height=256"
        presence = f"{song_name} by {artist}"
        nowplaying = f":musical_note: Now playing: {song_name}"
        desc = f"**Artist:** {artist}\n**Album:** {album}"
        embed = discord.Embed(title=nowplaying, description=desc, color=discord.Color.random())
        embed.set_thumbnail(url=albumart)
        channel = bot.get_channel(text_channel)
        server_name = channel.guild.name
        channel_name = channel.name
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name=server_name + " " + channel_name,
            state=presence
        )
        await bot.change_presence(activity=activity)
        await channel.send(embed=embed)

async def plays(songe):
    song_id = await song(songe)
    if song_id:
        channels = bot.get_channel(voice_channel)
        voice_client = discord.utils.get(bot.voice_clients, guild=channels.guild)
        if voice_client is None:
            voice_client = await channels.connect()

        player.channel = voice_client

        try:
            player.nowplaying = songe
            song_path = download_urls.replace("<id>", song_id)
            if ffmpeg_path_required == True:
                audio_source = FFmpegPCMAudio(
                    song_path,
                    executable=ffmpeg_path,
                    options='-filter:a "loudnorm=I=-16:TP=-1.5:LRA=11"',
                )
            else:
                audio_source = FFmpegPCMAudio(
                    song_path, options='-filter:a "loudnorm=I=-16:TP=-1.5:LRA=11"'
                )
            
            player.song_finished.clear()

            def after_playback(error):
                bot.loop.call_soon_threadsafe(
                    player.song_finished.set
                )

            voice_client.play(audio_source, after=after_playback)
            return True
        except:
            await error("Song Failed to play!")
            await voice_client.stop()
            return False
    return False


async def getinstantmix(id, limit):
    url = f"{server_url}/Items/{id}/InstantMix"

    params = {"limit": limit, "apiKey": api_key}  # Provide API key

    # Send GET request to Jellyfin API
    response = requests.get(url, params=params)
    if response.status_code == 200:
        songedd = []
        data = response.json()

        # Print song details
        for song in data["Items"]:
            artistlist = ""
            artists = song.get("Artists", [])
            if artists:
                artistlist = artists
            else:
                artistlist = "Unknown Artist"  # Fallback if no artists found
            album = ""
            albums = song.get("Album", [])
            albumId = song.get("AlbumId")
            if albums:
                album = albums
            else:
                album = "Unknown Album"
            songs = {
                "Name": song["Name"],
                "Artists": artistlist,  # List of artists
                "Album": album,  # Assuming album info is available
                "AlbumId": albumId,
                "Id": song["Id"],
            }

            songedd.append(songs)
        return songedd
    else:
        print(f"Error: {response.status_code} - {response.text}")


def getsongs():
    global player
    songs_list = []
    songed, data = songs()
    if songed is None:
        return False
    else:
        #player.song_list.extend(songed)
        songs_list = songed
        for song in songs_list:
            player.song_list.append(song)
        return True

'''def songs():
    url = f"{server_url}/Items"

    params = {
        "Recursive": "true",
        "IncludeItemTypes": "Audio",
        "SortBy": "SortName",
        "api_key": api_key,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        songed = [
            {
                "Name": song["Name"],
                "Artists": song.get("Artists") or "Unknown Artist",
                "Album": song.get("Album") or "Unknown Album",
                "AlbumId": song.get("AlbumId"),
                "Id": song["Id"],
            }
            for song in data["Items"]
        ]

        return songed, data

    except requests.RequestException as e:
        print(e)
        return None, None '''


def songs():

    # API endpoint to get all songs
    url = f"{server_url}/Items"

    # Request parameters to filter audio items and sort by name
    params = {
        "Recursive": "true",  # Fetch items recursively (including albums, etc.)
        "IncludeItemTypes": "Audio",  # Only fetch audio items (songs)
        "SortBy": "SortName",  # Sort by name
        "api_key": apiKey,  # Provide API key
    }

    # Send GET request to Jellyfin API
    response = requests.get(url, params=params)

    if response.status_code == 200:
        songed = []
        data = response.json()

        # Print song details
        for song in data["Items"]:
            artistlist = ""
            artists = song.get("Artists", [])
            if artists:
                artistlist = artists
            else:
                artistlist = "Unknown Artist"  # Fallback if no artists found
            album = ""
            albums = song.get("Album", [])
            albumId = song.get("AlbumId")
            if albums:
                album = albums
            else:
                album = "Unknown Album"
            songs = {
                "Name": song["Name"],
                "Artists": artistlist,  # List of artists
                "Album": album,  # Assuming album info is available
                "AlbumId": albumId,
                "Id": song["Id"],
            }

            songed.append(songs)
        return songed, data
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None, None

import asyncio

async def playqueue(songs):

    for song in songs:
        artist = song["Artists"][0]

        queue_item = (
            f"{song['Name']} | "
            f"**Artist:** {artist} | "
            f"**Album:** {song['Album']} | "
            f"**Id:** {song['Id']}"
        )

        player.queue_list.append(queue_item)

    await success(f"Added {len(songs)} song(s) to queue!")

    # Start queue worker if not already running
    if not player.playing:
        player.playing = True
        asyncio.create_task(process_queue())

    return "Queued successfully"

async def process_queue():

    try:
        while player.queue_list:

            song = player.queue_list.pop(0)

            if await plays(song):

                await nowplayingEmbed(song)

                # Wait until FFmpeg playback finishes
                await player.song_finished.wait()

            else:
                await error(f"Song {song} not found!")

    finally:

        player.playing = False

        await embeded(
            "Queue is Empty",
            "Add more songs to continue playing!"
        )

        if player.channel:
            await player.channel.disconnect()
