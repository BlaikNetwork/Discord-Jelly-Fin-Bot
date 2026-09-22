import configparser
import discord
from discord import FFmpegPCMAudio
import requests
import json
import math
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
from pathlib import Path
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
    server_url + "/Items/<id>/Download?apiKey=" + api_key
)
ffmpeg_path = config.get('FFMPEG', 'ffmpeg_path')
ffmpeg_path_required = config.getboolean('FFMPEG', 'ffmpeg_path_required')
join_msg = config.get('MESSAGES', 'join')
leave_msg = config.get('MESSAGES', 'leave')
image_url_required = config.getboolean('JellyFin', 'image_url_required')
image_url = ""

if image_url_required:
    image_url = config.get('JellyFin', 'image_url') + f"/Items/(id)/Images/Primary?width=2048&height=2048"
else:
    image_url = f"{server_url}/Items/(id)/Images/Primary?width=2048&height=2048"

player = None
bot = None

authTokens = []

playlist_path = Path("playlist.json")
if playlist_path.is_file():
    print("Playlist file exists.")
else:
    playlist_path.write_text("{}", encoding="utf-8")

with open('playlist.json', 'r') as playlistFile:
        playlistData = json.load(playlistFile)

playlist_lock = asyncio.Lock()

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

async def embededs(status, songs, image):
    # Basic embed creation
    try:
        embed = discord.Embed(
            title=status,
            description=songs,
            color=discord.Color.dark_blue(),
        )
        if image:
            embed.set_image(url=image)
        channel = bot.get_channel(text_channel)
        await channel.send(embed=embed)
    except Exception as e:
        print("Error: " + e)

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

async def getSongData(songed):
    song_list = await get_song_list()
    for song in song_list:
        if song["Id"] == songed:   
            artist = ""
            for i in song["Artists"]:
                artist = artist + " " + i
            songe = f"{song.get('Name')} | **Artist:** {artist} | **Album:** {song.get('Album')} | **Id:** `{song.get('Id')}`"
            return songe

    print("Song: " + str(songed) + " not found")
    return None

async def song2(songed):
    song_list = await get_song_list()
    for song in song_list:
        if song["Id"] == songed:   
            return song

    print("Song: " + str(songed) + " not found")
    return None

async def nowplayingEmbed(songe):
    song = await song2(songe)
    if song is None:
        return
    print(song)
    song_name = song.get('Name')
    album = song.get("Album")
    artist = ""
    for i in song["Artists"]:
        artist = artist + " " + i
    albumId = song.get("AlbumId")
    albumart = image_url.replace('(id)', albumId)
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

async def playlistContentEmbed(name, id, songs, pageStart):
    correct_songs = []
    for count, i in enumerate(songs):
        count = count+pageStart
        correct_songs.append(f"{count+1}. {await getSongData(i)}\n")
    correct_songs = "\n".join(correct_songs)
    embed = discord.Embed(title=name,description=correct_songs, color=discord.Color.ash_theme())
    embed.set_footer(text=f"{id}")
    channel = bot.get_channel(text_channel)
    await channel.send(embed=embed)

async def playlistsEmbed(userid, page, discordmessage):
    songs = []
    if userid in playlistData:
        if discordmessage:
            playlists = list(playlistData[userid].values())
            for playlist in playlists:
                id = playlist["Id"]
                songs.append(id)
            page = int(page)
            page_size = 10
            start = (page - 1) * page_size
            end = start + page_size

            # Calculate the total number of pages
            total_pages = math.ceil(len(songs) / page_size)

            # If the page number is invalid, notify the user
            if page < 1 or page > total_pages:
                await error(f"Invalid page number. Please choose a page between 1 and {total_pages}.")

            # Get the songs for the current page
            page_songs = songs[start:end]
            correct_page_songs = []

            for song in page_songs:
                song = playlistData[userid][song]
                songed = f"{song['Name']}\n`{song['Id']}` {song['SongCount']} songs\n"
                correct_page_songs.append(songed)

            # Create the message for the page
            message = "\n".join(correct_page_songs)
            # Send the message to the channel
            user = await bot.fetch_user(userid)
            displayname = user.display_name
            await embeded(f"**{displayname}'s playlists\nPage {page}/{total_pages}**", message)
        else:
            return playlistData[userid]
    else:
        if discordmessage:
            await error("No playlists found!")
        else:
            return "No playlists found!"

async def plays(songe):
    channels = bot.get_channel(voice_channel)
    voice_client = discord.utils.get(bot.voice_clients, guild=channels.guild)
    if voice_client is None:
        voice_client = await channels.connect()

        player.channel = voice_client

    try:
        player.nowplaying = songe
        song_path = download_urls.replace("<id>", songe)
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
    songed, albums, artists = songs()
    if songed is None or albums is None or artists is None:
        return False
    else:
        player.song_list = songed
        player.album_list = albums
        player.artist_list = artists
        return True

'''
def songs():

    # API endpoint to get all songs
    url = f"{server_url}/Items"

    # Request parameters to filter audio items and sort by name
    params = {
        "Recursive": "true",  # Fetch items recursively (including albums, etc.)
        "IncludeItemTypes": "Audio",  # Only fetch audio items (songs)
        "SortBy": "SortName",  # Sort by name
        "api_key": api_key,  # Provide API key
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
    '''

def songs():
    url = f"{server_url}/Items"
    chunk_size = 0

    params = {
        "Recursive": "true",
        "IncludeItemTypes": "Audio,MusicAlbum,MusicArtist",
        "SortBy": "SortName",
        "Limit": 1,
        "apiKey": api_key,
    }
    session = requests.Session()
    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return None, None

    first_data = response.json()
    total_songs = first_data.get("TotalRecordCount", 0)
    chunk_size = int(total_songs) / 3
    chunk_size = math.ceil(chunk_size)

    def process_chunk(start_index):
        params = {
            "Recursive": "true",
            "IncludeItemTypes": "Audio,MusicAlbum,MusicArtist",
            "SortBy": "SortName",
            "StartIndex": start_index,
            "Limit": chunk_size,
            "apiKey": api_key,
        }

        response = session.get(url, params=params)

        if response.status_code != 200:
            print(f"Error loading chunk {start_index}")
            return []

        data = response.json()
        chunk_songs = []
        chunk_albums = []
        chunk_artists = []
        for song in data.get("Items", []):
            if song.get("Type") == "Audio":
                chunk_songs.append({
                    "Name": song["Name"],
                    "Artists": song.get("Artists", ["Unknown Artist"]),
                    "Album": song.get("Album", "Unknown Album"),
                    "AlbumId": song.get("AlbumId"),
                    "Id": song["Id"],
                    "ProductionYear": song.get("ProductionYear"),
                    "Type": "Song",
                })
            elif song.get("Type") == "MusicAlbum":
                chunk_albums.append({
                    "Name": song["Name"],
                    "Artists": song.get("Artists", ["Unknown Artist"]),
                    "Id": song["Id"],
                    "Image": song.get("ImageTags", {}).get("Primary"),
                    "ProductionYear": song.get("ProductionYear"),
                    "Type": "Album",
                })
            else:
                chunk_artists.append({
                    "Name": song["Name"],
                    "Id": song["Id"],
                    "Image": song.get("ImageTags", {}).get("Primary"),
                    "Type": "Artist",
                })
        print(
            f"Processed chunk {start_index} "
            f"({len(chunk_songs)} songs)"
        )

        return chunk_songs, chunk_albums, chunk_artists

    songed = []
    albums = []
    artists = []
    timer = time.perf_counter()
    with ThreadPoolExecutor() as executor:

        results = executor.map(
            process_chunk,
            range(0, total_songs, chunk_size)
        )
        for chunk_songs, chunk_albums, chunk_artists in results:
            songed.extend(chunk_songs)
            albums.extend(chunk_albums)
            artists.extend(chunk_artists)

    timer = time.perf_counter() - timer
    print(f"Finished loading {len(songed)} songs, {len(albums)} albums, {len(artists)} artists in {timer:.2f} seconds" )

    return songed, albums, artists

async def playqueue(songs):

    for song in songs:
        player.queue_list.append(song["Id"])

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

def is_numeric(val):
    try:
        float(val)
        return True
    except ValueError:
        return False

async def save_playlists():
    async with playlist_lock:
        with open("playlist.json", "w") as f:
            json.dump(playlistData, f, indent=4)

async def read_playlists(userid, page, playlistId, discordmessage):
    if playlistId == "":
        if discordmessage:
            await playlistsEmbed(userid, page, discordmessage)
        else:
            return await playlistsEmbed(userid, page, discordmessage)
    else:
        if userid in playlistData and playlistId in playlistData[userid]:
            if discordmessage:
                page = int(page)
                songs = playlistData[userid][playlistId]["Songs"]
                page_size = 10
                start = (page - 1) * page_size
                end = start + page_size
            
                # Calculate the total number of pages
                total_pages = math.ceil(len(songs) / page_size)
            
                # If the page number is invalid, notify the user
                if page < 1 or page > total_pages:
                    await error(f"Invalid page number. Please choose a page between 1 and {total_pages}.")
            
                # Get the songs for the current page
                page_songs = songs[start:end]
                songStart = page*page_size-10

                name = playlistData[userid][playlistId]["Name"]
                name = f"**{name}  -  Page {page} of {total_pages}**"
                await playlistContentEmbed(name, playlistId, page_songs, songStart)
            else:
                return playlistData[userid][playlistId]
        else:
            if discordmessage:
                await error(f"Playlist `{playlistId}` not found!")
            else:
                return f"Playlist {playlistId} not found!"
        
async def create_playlist(userid, name):
    my_uuid = str(uuid.uuid4())
    if userid not in playlistData:
        playlistData[userid]= {}
    playlistData[userid][my_uuid] = {
    "Name" : name,
    "Id": my_uuid,
    "SongCount": 0,
    "Songs": []
    }
    await save_playlists()
    return my_uuid

async def addSongs_Playlist(playlistId, userid, songlist, discordmessage):
    if playlistId in playlistData[userid]:
        print(songlist)
        existingSongs = []
        existingSongs = playlistData[userid][playlistId]["Songs"]
        print(existingSongs)
        existingSongs.extend(songlist)
        playlistData[userid][playlistId]["SongCount"] = len(existingSongs)
        playlistData[userid][playlistId]["Songs"] = existingSongs
        await save_playlists()
        return True
    else:
        if discordmessage:
            await error("Playlist not Found!")
            return False
        else:
            return False

async def delete_playlist(userid, playlistId, discordmessage):
    if userid in playlistData and playlistId in playlistData[userid]:
        del playlistData[userid][playlistId]
        await save_playlists()
        if discordmessage:
            await success(f"Playlist `{playlistId}` successfully deleted!")
        else:
            return f"Playlist {playlistId} successfully deleted!"
    else:
        if discordmessage:
            await error("Playlist not Found!")
        else:
            return "Playlist not Found!"

async def removeSongs_playlist(userid, playlistId, songs, discordmessage):
    if userid in playlistData and playlistId in playlistData[userid]:
        if len(playlistData[userid][playlistId]["Songs"]) > 0:
            removed = 0
            for i in playlistData[userid][playlistId]["Songs"][:]:
                for ii in songs:
                    if i == ii:
                        playlistData[userid][playlistId]["Songs"].remove(i)
                        removed += 1
            songCount = len(playlistData[userid][playlistId]["Songs"])
            playlistData[userid][playlistId]["SongCount"] = songCount
            await save_playlists()
            if discordmessage:
                await success(f"Successfully Removed `{removed}` songs from your platlist with id `{playlistId}`")
            else:
                return f"Successfully Removed {removed} songs from your platlist with id {playlistId}"
        else:
            if discordmessage:
                await error(f"Playlist `{playlistId}` has no songs!")
            else:
                return f"Playlist {playlistId} has no songs!"
    else:
        if discordmessage:
            await error(f"Playlist `{playlistId}` not Found!")
        else:
            return f"Playlist {playlistId} not Found!"

async def queue_playlist(playlistId, userid, discordmessage):
    if userid in playlistData and playlistId in playlistData[userid]:
        if len(playlistData[userid][playlistId]["Songs"]) > 0:
            songData= []
            for songId in playlistData[userid][playlistId]["Songs"]:
                songlist = await get_song_list()
                for song in songlist:
                    if songId == song["Id"]:
                        songData.append(song)
            await playqueue(songData)
            if discordmessage:
                await success(f"Successfully added playlist {playlistId} to the queue!")
            else:
                return f"Successfully added playlist {playlistId} to the queue!"
        else:
            if discordmessage:
                await error(f"No songs in playlist `{playlistId}`")
            else:
                return f"No songs in playlist {playlistId}"
    else:
        if discordmessage:
            await error(f"Either playlist `{playlistId}` dosen't exist or you have no playlists, not sure which one :(")
        else:
            return f"Either playlist {playlistId} dosen't exist or you have no playlists, not sure which one :("

async def auth(userid, token):
    for i in authTokens:
        print("i: " + str(i))
        print("userid: " + userid)
        print("token: " + token)
        if i["id"] == userid and i["token"] == token:
            return "success"
    return "unsuccessful"

async def authGen(userid):
    for i in authTokens:
        if i["id"] == userid:
            i["token"] == str(uuid.uuid4())
            return "success"
    uuidd = str(uuid.uuid4())
    token = {"id": userid,"token": uuidd}
    authTokens.append(token)
    return uuidd

async def startUp():
    embed = discord.Embed(
                title=join_msg,
                color=discord.Color.blurple()
            )
    channel = bot.get_channel(text_channel)
    await channel.send(embed=embed)

async def exit():
    embed = discord.Embed(
            title=leave_msg,
            color=discord.Color.blurple()
        )
    channel = bot.get_channel(text_channel)
    await channel.send(embed=embed)

async def usage_playlist():
    await embeded("Playlist Usage", "list `playlist id / page` `page`\ncreate `name`\naddsongs `playlist id` `id1, id2, id3`\ndelete `playlist id`\nremovesongs `playlist id` `id1, id2, id3`\n queue `playlist id`")