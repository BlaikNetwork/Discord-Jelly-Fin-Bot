import asyncio
import math
import random
import helpers
import discord
import configparser
config = configparser.ConfigParser()

# Read the config file
config.read('config.cfg')

#api
port = config.getint('API', 'port')
image_url_required = config.getboolean('JellyFin', 'image_url_required')
url = config.get('JellyFin', 'url')
player = None
bot = None
VERSION = None
image_url = ""

if image_url_required:
    image_url = config.get('JellyFin', 'image_url') + f"/Items/(id)/Images/Primary?width=2048&height=2048"
else:
    image_url = f"{url}/Items/(id)/Images/Primary?width=2048&height=2048"

def setup(bott, music_player, APPVERSION):
    global bot, player, VERSION
    bot = bott
    player = music_player
    VERSION = APPVERSION
    helpers.setup(bott, music_player)

async def skip():
    """Command to skip the currently playing song."""
    if player.channel and player.channel.is_playing():
        if player.playall_active:  # Check if playall is active
            player.channel.stop()  # Stop the current song
            await helpers.success("Song Skipped!")
            return ("Song Skipped!")
        elif player.playing:  # Check if playall is active
            player.channel.stop()  # Stop the current song
            await helpers.success("Song Skipped!")
            return ("Song Skipped!")
        else:
            await helpers.error("Playall queue or Play queue is not active.")
            return ("Playall queue or Play queue is not active.")
    else:
        await helpers.error("No audio is currently playing.")
        return ("No audio is currently playing.")
    

async def play(song_name):

    if not song_name:
        await helpers.error("You need to specify an id!")
        return "You need to specify an id!"

    song_list = []

    song_name = song_name.replace(" ", "")

    if "," in song_name:
        song_list = song_name.split(",")
    else:
        song_list.append(song_name)

    songs = await helpers.get_song_list()

    selected = []

    for requested_id in song_list[:]:
        for song in songs:
            if song["Id"].casefold() == requested_id.casefold():
                selected.append(song)
                song_list.remove(requested_id)
                break

    if not selected:
        await helpers.error(
            "Sorry, I can't find any of the songs provided. Please choose from !songs"
        )
        return "Sorry, I can't find any of the songs provided. Please choose from !songs"

    if song_list:
        await helpers.error(f"Found {len(song_list)} invalid song ids")
        

    result = await helpers.playqueue(selected)

    return result
    

async def leave():
    """Command to make the bot leave the voice channel"""
    if player.channel:
        player.channel.disconnect()
        await helpers.success("Disconnected from the voice channel")
        return "Disconnected from the voice channel"
    else:
        await helpers.error("I'm not connected to a voice channel!")
        return "I'm not connected to a voice channel!"


async def ping():
    """Command to make the bot leave the voice channel"""
    await helpers.success("Pong!")
    return "Pong!"




async def playnext(song_name):
    """Command to add a song to the queue."""    
    
    if song_name == " ":
        song_name = ""

    if not song_name:
        await helpers.error("You need to specifify an id!")
        return "You need to specifify an id!"
    
    if not player.queue_list:
        await helpers.error("The queue is currently Empty.")
        return "The queue is currently Empty."

    song_list = ""
    if " " in song_name:
        song_name = song_name.replace(" ", "")
        if "," in song_name:
            song_list = song_name.split(",")
    elif "," in song_name:
            song_list = song_name.split(",")
    else:
        song_list = []
        song_list.append(song_name)
    # Join the song name parts into a single string (in case it's multi-word)
    songs = await helpers.get_song_list()

    # Check if the song is in the available list

    selected = []
    songed_list = song_list
    for ii in songed_list[:]:
        for i in songs:
            song = i["Id"]
            if song.casefold() == ii.casefold():
                selected.append(i)       
                song_list.remove(ii)
                if len(song_list) == 0:
                    break
        


    if len(selected) == 0:
        await helpers.error(f"Sorry, I can't find any of the song/songs provided. Please choose from !songs")
        return "Sorry, I can't find any of the song/songs provided. Please choose from !songs"
    
    if len(song_list) >= 1:
        invalid = len(song_list)
        await helpers.error(f"Found {invalid} invalid song ids")
        print(f"Found {invalid} invalid song ids")

    list = player.queue_list[:]
    player.queue_list.clear()
    for i in selected:
        player.queue_list.append(i)
    for ii in list:
        player.queue_list.append(ii)
    
    await helpers.success("The " + str(len(selected)) + " id/s provided will play next in the queue!")
    return "The " + str(len(selected)) + " id/s provided will play next in the queue!"


async def playnow(song_name):
    """Command to add a song to the queue."""
    
    if song_name == " ":
        song_name = ""

    if not song_name:
        await helpers.error("You need to specifify an id!")
        return "you need to specifify an id!"
    
    if not player.queue_list:
        await helpers.error("The queue is currently Empty.")
        return "The queue is currently Empty."
    
    song_list = ""
    if " " in song_name:
        song_name = song_name.replace(" ", "")
        if "," in song_name:
            song_list = song_name.split(",")
    elif "," in song_name:
            song_list = song_name.split(",")
    else:
        song_list = []
        song_list.append(song_name)
    # Join the song name parts into a single string (in case it's multi-word)
    songs = await helpers.get_song_list()

    # Check if the song is in the available list

    selected = []
    songed_list = song_list
    for ii in songed_list[:]:
        for i in songs:
            song = i["Id"]
            if song.casefold() == ii.casefold():
                selected.append(i)       
                song_list.remove(ii)
                if len(song_list) == 0:
                    break
        


    if len(selected) == 0:
        await helpers.error(f"Sorry, I can't find any of the song/songs provided. Please choose from !songs")
        return "Sorry, I can't find any of the song/songs provided. Please choose from !songs"
    
    if len(song_list) >= 1:
        invalid = len(song_list)
        await helpers.error(f"Found {invalid} invalid song ids")
        print(f"Found {invalid} invalid song ids")

    list = player.queue_list[:]
    player.queue_list.clear()
    for i in selected:
        player.queue_list.append(i)
    for ii in list:
        player.queue_list.append(ii)
    
    player.channel.stop()
    await helpers.success("The " + str(len(selected)) + " id/s provided will play now/next in the queue!")
    return "The " + str(len(selected)) + " id/s provided will play now/next in the queue!"


async def pause():
    
    if  player.channel and (player.channel.is_playing() or player.channel.is_paused()):
        player.channel.pause()
        await helpers.success("Playback has been paused!")
        return "Playback has been paused!"
    else:
        await helpers.error("Nothing to Pause!")
        return "Nothing to Pause!"


async def resume():
    
    if player.channel and (player.channel.is_playing() or player.channel.is_paused()):
        player.channel.resume()
        await helpers.success("Playback has been resumed!")
        return "Playback has been resumed!"
    else:
        await helpers.error("Nothing to resume!")
        return "Nothing to resume!"


async def remove(song_name = ""):
    """Command to add a song to the queue."""
    
    if song_name == "":
        await helpers.error("You need to specifify an id!")
        return "You need to specifify an id!"
    
    if not player.queue_list:
        await helpers.error("The queue is currently Empty.")
        return "The queue is currently Empty."
    song_list = ""
    if " " in song_name:
        song_name = song_name.replace(" ", "")
        if "," in song_name:
            song_list = song_name.split(",")
    elif "," in song_name:
            song_list = song_name.split(",")
    else:
        song_list = []
        song_list.append(song_name)
    # Join the song name parts into a single string (in case it's multi-word)
    songs = await helpers.get_song_list()

    # Check if the song is in the available list

    selected = []
    songed_list = song_list
    for ii in songed_list[:]:
        for i in songs:
            song = i["Id"]
            if song.casefold() == ii.casefold():
                selected.append(i)       
                song_list.remove(ii)
                if len(song_list) == 0:
                    break
        


    if len(selected) == 0:
        await helpers.error(f"Sorry, I can't find any of the song/songs provided. Please choose from !songs")
        return "Sorry, I can't find any of the song/songs provided. Please choose from !songs"
    
    if len(song_list) >= 1:
        invalid = len(song_list)
        await helpers.error(f"Found {invalid} invalid song ids")
        print(f"Found {invalid} invalid song ids")

    for i in selected:
        for ii in player.queue_list[:]:
            if ii == i:
                player.queue_list.remove(i)

    await helpers.success("Removed " + str(len(selected)) + " ids from the Queue!")
    return "Removed " + str(len(selected)) + " ids from the Queue!"

async def version():
    # Check if the error is CommandNotFound
    await helpers.success(f"Blaik Network JellyFin Music Bot Version: {VERSION}")
    return f"Blaik Network JellyFin Music Bot Version: {VERSION}"


async def randomsong():
    print ("getting random song...")
    """Command to add a random song to the queue."""    
    try:
        songs = await helpers.get_song_list()
        print("fetched songlist..")
        integer = random.randint(0, len(songs) - 1)
        song = []
        song.append(songs[integer])
        await helpers.playqueue(song)
        print("played song...")
    except Exception as e:
        print(f"randomerror: {e}")
    return "Random song added to the queue!"


async def queue( page=1):
    """Command to show what is currently in the queue."""
    
    message = ""
    if player.queue_list != []:
        songs = player.queue_list
        page_size = 10
        start = (page - 1) * page_size
        end = start + page_size

        # Calculate the total number of pages
        total_pages = math.ceil(len(songs) / page_size)

        # If the page number is invalid, notify the user
        if page < 1 or page > total_pages:
            await helpers.error(f"Invalid page number. Please choose a page between 1 and {total_pages}.")
            return f"Invalid page number. Please choose a page between 1 and {total_pages}."

        # Get the songs for the current page
        page_songs = songs[start:end]
        correct_page_songs = []

        for song in page_songs:
            songed = f"{await helpers.getSongData(song)} \n"
            correct_page_songs.append(songed)

        # Create the message for the page
        message = "".join(correct_page_songs)

        # Send the message to the channel
        await helpers.embeded(f"**Page {page}/{total_pages}, The following songs are in the queue!:**", message)
        return f"Page {page}/{total_pages}, The following songs are in the queue!: {message}"
    else:
        await helpers.error(f"The Queue is empty!")
        return f"The Queue is empty!"



async def clearqueue():
    if player.queue_list:
        player.queue_list.clear()
        await helpers.success("The Queue has been cleared!")
        return {"success": "The Queue has been cleared!"}
    else:
        await helpers.error("There is nothing in the Queue!")
        return {"error": "There is nothing in the Queue!"}


async def stop():
    """Command to stop any currently playing music."""
    voice = player.channel
    print("stop command executing...")
    try:
        if voice and (voice.is_playing() or voice.is_paused()):
            if player.playall_active:
                player.playall_active = False
                await helpers.success("The playall queue has been stopped.")
                message = "The playall queue has been stopped."
            elif player.looping:
                player.looping = False
                await helpers.success("The loop has been stopped.")
                message = "The loop has been stopped."
            else:
                player.playing = False
                await helpers.success("Stopped the current song.")
                message = "Stopped the current song."
            player.queue_list = []
            voice.stop()
            return message
        else:
            await helpers.error("No audio is currently playing.")
            return "No audio is currently playing."
    except Exception as e:
        print(f"Error occurred while executing stop: {e}")

    # If playall is active, stop it as well



import random

async def randomplaylist(keywords):
    try:
        """Add multiple random songs to the queue based on album, artist, or all songs."""

        # Determine song count
        count = 10

        if keywords:
            if helpers.is_numeric(keywords[0]) or len(keywords) >= 3 and helpers.is_numeric(keywords[2]):
                try:
                    count = int(keywords[-1])
                    keywords = keywords[:-1]
                except ValueError:
                    pass

        if count > 10000:
            await helpers.error("You can only add 10,000 songs at a time!")
            return "You can only add 10,000 songs at a time!"

        serversongslist = await helpers.get_song_list()
        foundsongs = []

        # No search criteria provided
        print(keywords)
        if not keywords:
            foundsongs = serversongslist.copy()

        else:
            search_type = keywords[0].casefold()
            search_query = " ".join(keywords[1:]).casefold()

            for song in serversongslist:

                if search_type == "album:":
                    if search_query in song["Album"].casefold():
                        foundsongs.append(song)

                elif search_type == "artist:":
                    if any(
                        search_query in artist.casefold()
                        for artist in song["Artists"]
                    ):
                        foundsongs.append(song)

                elif search_type == "decade:":
                    year = song["ProductionYear"]
                    if year is not None:
                        year = int(year)
                        if int(search_query) <= year <= int(search_query)+9:
                            foundsongs.append(song)
                else:
                    # Unknown filter, include all songs
                    foundsongs.append(song)

        if not foundsongs:
            await helpers.error("No Songs were found!")
            return "No Songs were found!"

        randomsongslist = [
            random.choice(foundsongs)
            for _ in range(count)
        ]

        await helpers.playqueue(randomsongslist)
        return "Songs added to the queue!"
    except Exception as e:
        print(e)



async def songs( page: int = 1):
    """Command to list all available songs, paginated by 10 songs per page."""

    # Calculate the start and end index for the requested page
    songs = await helpers.get_song_list()
    page_size = 10
    start = (page - 1) * page_size
    end = start + page_size

    # Calculate the total number of pages
    total_pages = math.ceil(len(songs) / page_size)

    # If the page number is invalid, notify the user
    if page < 1 or page > total_pages:
        await helpers.error(f"Invalid page number. Please choose a page between 1 and {total_pages}.")
        return f"Invalid page number. Please choose a page between 1 and {total_pages}."

    # Get the songs for the current page
    page_songs = songs[start:end]
    correct_page_songs = []

    for song in page_songs:
        songed = f"{song.get('Name')} | Artist: {song.get('Artists')} | Album: {song.get('Album')} | Id: {song.get('Id')} \n"
        correct_page_songs.append(songed)

    # Create the message for the page
    message = "".join(correct_page_songs)

    # Send the message to the channel
    await helpers.embeded(f"**Page {page}/{total_pages}**", message)
    return f"Page {page}/{total_pages}: {message}"



async def playall():
    """Command to play all songs in the list one by one"""
    # Check if the bot is currently playing audio
    if player.channel and (player.channel.is_playing() or player.channel.is_paused()):
        await helpers.error(f"{player.channel}, Could not play all songs, A song is currently playing")
        return f"{player.channel}, Could not play all songs, A song is currently playing"
    
    await helpers.success(f"Playing all songs in the list!")

    songs = await helpers.get_song_list()
    
    player.playall_active = True

    # Loop through each song and play it
    for song_name in songs:
        if not player.playall_active:  # Check if playall_active is False to break the loop
            break

        Artists = song_name.get("Artists")
        Artist = Artists[0]
        songe = f"{song_name.get('Name')} | **Artist:** {Artist} | **Album:** {song_name.get('Album')} | **Id:** {song_name.get('Id')}"

        if await helpers.plays(songe):
            await helpers.nowplayingEmbed(songe)
        else:
            await helpers.error(f"Song '{songe}' not found!")

        # Wait for the song to finish before moving to the next one
        while player.channel.is_playing():
            await asyncio.sleep(1)  # Wait until the song finishes

    await helpers.success("All songs have been played.")
    await player.channel.disconnect()
    return "All songs have been played."



async def loop(song_name = ""):
    """Command to play loop a song from the list."""
    print("looping...")
    # Check if the bot is currently playing audio
    if player.channel and (player.channel.is_playing() or player.channel.is_paused()):
        await helpers.error("Could not loop song, A song is currently playing")
        return f"Could not loop song, A song is currently playing"

    if song_name == " ":
        song_name = ""
        
    if not song_name:
        print("song_name = ''")
        await helpers.error("You need to specify an id!")
        return "You need to specify an id!"

    # Join the song name parts into a single string (in case it's multi-word)
    
    player.looping = True

    # Check if the song is in the available list
    songs = await helpers.get_song_list()
    selected = []
    for i in songs:
        song = i["Id"]
        if song.casefold() == song_name:
            selected.append(i)
            break
        else:
            continue
    else:
        await helpers.error(
            f"Sorry, I can't find a song with id '{song_name}'. Please choose from !songs"
        )
        return f"Sorry, I can't find a song with id '{song_name}'. Please choose from !songs"

    song = selected[0]
    # Play the song using FFmpeg
    
    while player.looping:
        await asyncio.sleep(1)
        if not player.looping:  # Check if playall_active is False to break the loop
            break

        Artists = song.get("Artists")
        Artist = Artists[0]
        songe = f"{song.get('Name')} | **Artist:** {Artist} | **Album:** {song.get('Album')} | **Id:** {song.get('Id')}"

        if await helpers.plays(songe):
            await helpers.nowplayingEmbed(songe)
        else:
            player.looping = False
            await helpers.error(f"Song '{song_name}' not found!")
            return f"Song '{song_name}' not found!"

        while player.channel.is_playing():
            await asyncio.sleep(1)  # Wait until the song finishes



async def search( keywords):
    """Command to search for songs based on the artist, album or song name."""
    if not keywords:
        await helpers.error("Please provide some keywords to search for.")
        return "Please provide some keywords to search for."

    # Join the keywords into a single search string
    try:
        # Try to cast the last keyword to an integer
        page = int(keywords[-1])
        # If it's valid, remove it from the keywords
        keywords = keywords[:-1]
    except ValueError:
        # If the last keyword is not a number, default page to 1
        page = 1

    search_query = " ".join(keywords).lower()
    search_query = str(search_query)

    # Fetch all the MP3 files in the SONG_DIR
    song_list = await helpers.get_song_list()

    # Filter the song list to find matches
    matching_songs = []
    if keywords[0].lower() == "album:":
        search_query = search_query.replace("album: ", "")
        for song in song_list:
            if search_query.casefold() in song["Album"].casefold():
                match = str(song["Name"] + " | Id: " + song["Id"] + "\n")
                matching_songs.append(match)
    elif keywords[0].lower() == "artist:":
        search_query = search_query.replace("artist: ", "")
        for song in song_list:
            for songe in song["Artists"]:
                if search_query.casefold() in songe.casefold():
                    match = str(song["Name"] + " | Id: " + song["Id"] + "\n")
                    matching_songs.append(match)
    else:
        for song in song_list:
            if search_query.casefold() in song["Name"].casefold():
                match = str(song["Name"] + " | Id: " + song["Id"] + "\n")
                matching_songs.append(match)

    if matching_songs:
        # If there are matches, send them to the user
        songs = matching_songs
        page_size = 20
        start = (page - 1) * page_size
        end = start + page_size

        # Calculate the total number of pages
        total_pages = math.ceil(len(songs) / page_size)

        # If the page number is invalid, notify the user
        if page < 1 or page > total_pages:
            await helpers.error(
                f"Invalid page number. Please choose a page between 1 and {total_pages}."
            )
            return f"Invalid page number. Please choose a page between 1 and {total_pages}."

        # Get the songs for the current page
        page_songs = songs[start:end]

        # Create the message for the page
        message = "".join(page_songs)

        # Send the message to the channel
        await helpers.embeded(f"**Page {page}/{total_pages}, Found the following songs matching '{search_query}':**", message)
    else:
        await helpers.error(f"No songs found matching '{search_query}'.")
        return f"No songs found matching '{search_query}'."


async def updatesongs():
    """Command to update the songs database for the bot."""
    if helpers.getsongs():
        await helpers.success(f"Song database updated successfully.")
        return f"Song database updated successfully."
    else:
        await helpers.error(f"Error updating song database.")
        return f"Error updating song database."



async def instantmix(id):
    """Command to add an instant mix to the queue."""
    # Check if the bot is currently playing audio
     
        
    if not id:
        await helpers.error("You need to specify an id!")
        return "You need to specify an id!"
    
    limit = 0
    try:
        limit = int(id[-1])
    except ValueError:
        limit = 15

    ids = id[0]
    id = ids

    await helpers.success(f"Getting an Instant Mix from JellyFin server!")
    try:
        songs = await helpers.getinstantmix(id, limit)
        if songs:
            await helpers.success(f"Instant Mix added to the queue!")
        await helpers.playqueue(songs)
        return "Instant Mix added to the queue!"
    except:
        await helpers.error(f"Could not Retrieve Instant Mix from JellyFin server!")
        return "Could not Retrieve Instant Mix from JellyFin server!"

async def playlist(keywords, userid, discord):
    try:
        if not keywords:
            if discord:
                await helpers.error("Please Enter a Valid Sub-Command")
                return
            else:
                return "Please Enter a Valid Sub-Command"

        elif keywords[0] == "list".casefold():
            if len(keywords) > 1:
                if helpers.is_numeric(keywords[1]):
                    page = keywords[1]
                    return await helpers.read_playlists(userid, page, playlistId="", discordmessage=discord)
                else:
                    playlistId = keywords[1]
                    if len(keywords) > 2:
                        if helpers.is_numeric(keywords[2]):
                            page = keywords[2]
                            return await helpers.read_playlists(userid, page, playlistId, discordmessage=discord)
                    else:
                        return await helpers.read_playlists(userid, page=1, playlistId=playlistId, discordmessage=discord)
            else:
                return await helpers.read_playlists(userid, page=1, playlistId="", discordmessage=discord)
        elif keywords[0] == "create".casefold():
            if keywords[1:]:
                name = keywords[1:]
                name = " ".join(name)
                if len(name) >30:
                    if discord:
                        await helpers.error("Playlist Name is too long!")
                    else:
                        return "Playlist Name is too long!"
                else:
                    try:
                        id = await helpers.create_playlist(userid, name)
                        if discord:
                            await helpers.success(f"Sucessfuly created playlist `{name}` with id `{id}`")
                        else:
                            return f"Sucessfuly created playlist {name} with id {id}"
                    except Exception as e:
                        if discord:
                            await helpers.error("An error occurred while creating your playlist!")
                        else:
                            return "An error occurred while creating your playlist!"
                        print(e)
            else:
                if discord:
                    await helpers.error("No playlist name was given!")
                else:
                    return "No playlist name was given!"
        elif keywords[0] == "addsongs".casefold():
            if len(keywords) > 2:
                playlistId = keywords[1]
                keywords = "".join(keywords[2:])
                keywords2 = []
                if "," in str(keywords):
                    keywords2 = str(keywords).split(",")
                song_list = [song.strip().rstrip(",") for song in keywords2]

                # Check if the song is in the available list
                selected = []
                songed_list = song_list
                songs = await helpers.get_song_list()
                for ii in songed_list[:]:
                    for i in songs:
                        song = i["Id"]
                        if song.casefold() == ii.casefold():
                            selected.append(song)       
                            song_list.remove(ii)
                            if len(song_list) == 0:
                                break

                print(str(selected))

                if len(selected) == 0:
                    if discord:
                        await helpers.error(f"Sorry, I can't find any of the song/songs provided. Please choose from !songs")
                        return
                    else:
                        return f"Sorry, I can't find any of the song/songs provided. Please choose from !songs"
                    
                if len(song_list) >= 1:
                    invalid = len(song_list)
                    if discord:
                        await helpers.error(f"Found {invalid} invalid song ids")
                        return
                    else:  
                        return f"Found {invalid} invalid song ids"

                try:
                    if discord:
                        await helpers.addSongs_Playlist(playlistId, userid, selected, discordmessage=discord)
                        await helpers.success(f"Successfully Added `{len(selected)}` songs to your platlist with id `{playlistId}`")
                    else:
                        if await helpers.addSongs_Playlist(playlistId, userid, selected,discordmessage=discord):
                            return f"Successfully Added `{len(selected)}` songs to your platlist with id `{playlistId}`"
                        else:
                            return "Playlist not Found!"
                except Exception as e:
                    print(e)
                    if discord:
                        await helpers.error("An error occurred while adding songs to your playlist!")
                    else:
                        return "An error occurred while adding songs to your playlist!"
            else:
                if discord:
                    await helpers.error("No playlist id or list of songs provided!")
                else:
                    return "No playlist id or list of songs provided!"
        elif keywords[0] == "delete".casefold():
            if len(keywords) > 1:
                playlistId = keywords[1]
                if discord:
                    await helpers.delete_playlist(userid, playlistId, discordmessage=discord)
                else:
                    return await helpers.delete_playlist(userid, playlistId, discordmessage=discord)
            else:
                if discord:
                    await helpers.error("No playlist Id was given!")
                else:
                    return "No playlist Id was given!"
        elif keywords[0] == "removesongs".casefold():
            if len(keywords) > 2:
                playlistId = keywords[1]
                keywords = "".join(keywords[2:])
                keywords2 = []
                if "," in str(keywords):
                    keywords2 = str(keywords).split(",")
                song_list = [song.strip().rstrip(",") for song in keywords2]

                # Check if the song is in the available list
                selected = []
                songed_list = song_list
                songs = await helpers.get_song_list()
                for ii in songed_list[:]:
                    for i in songs:
                        song = i["Id"]
                        if song.casefold() == ii.casefold():
                            selected.append(song)       
                            song_list.remove(ii)
                            if len(song_list) == 0:
                                break

                if len(selected) == 0:
                    if discord:
                        await helpers.error(f"Sorry, I can't find any of the song/songs provided. Please choose from !songs")
                    else:
                        return f"Sorry, I can't find any of the song/songs provided. Please choose from !songs"
                    
                if len(song_list) >= 1:
                    invalid = len(song_list)
                    if discord:
                        await helpers.error(f"Found {invalid} invalid song ids")
                    else:
                        return f"Found {invalid} invalid song ids"
                try:
                    if discord:
                        await helpers.removeSongs_playlist(userid, playlistId, selected, discordmessage=discord)
                    else:
                        return await helpers.removeSongs_playlist(userid, playlistId, selected, discordmessage=discord)
                except Exception as e:
                    print(e)
                    if discord:
                        await helpers.error("An error occurred while removing songs from your playlist!")
                    else:
                        return "An error occurred while removing songs from your playlist!"
                    
            else:
                if discord:
                    await helpers.error("No playlist id or list of songs provided!")
                else:
                    return "No playlist id or list of songs provided!"
        elif keywords[0] == "queue".casefold():
            if len(keywords) > 1:
                playlistId = keywords[1]
                try:
                    if discord:
                        await helpers.queue_playlist(playlistId, userid, discordmessage=discord)
                    else:
                        return await helpers.queue_playlist(playlistId, userid,discordmessage=discord)
                except Exception as e:
                    print(e)
                    if discord:
                        await helpers.error("An error occured when queuing your playlist")
                    else:
                        return "An error occured when queuing your playlist"
            else:
                if discord:
                    await helpers.error("No playlist Id was provided!")
                else:
                    return "No playlist Id was provided!"
        elif keywords[0] == "usage".casefold():
            await helpers.usage_playlist()
        else:
            if discord:
                await helpers.error("Please Enter a Valid Sub-Command!")
            else:
                return "Please Enter a Valid Sub-Command!"
    except Exception as e:
        print(e)
        if discord:
            await helpers.error("An error occurred!")
        else:
            return "An error occurred!"

async def auth(ctx, userid):
    try:
        token = await helpers.authGen(userid)
        desc = f"Go to http://127.0.0.1/{port} and enter the generated linking code below\n **Linking code** {token}"
        embed = discord.Embed(title="Blaik Network JellyFin UI Instructions", description=desc, color=discord.Color.onyx_embed())
        await ctx.author.send(embed=embed)
        await ctx.reply("Check your DMs for instructions to access the web UI")
    except Exception as e:
        print(e)

async def idLookup(id):
    song_list = ""
    if " " in id:
        id = id.replace(" ", "")
    if "," in id:
        song_list = id.split(",")
    elif "," in id:
        song_list = id.split(",")
    else:
        song_list = []
        song_list.append(id)

    found = []
    id  = song_list
    if len(id) == 1:
        id = id[0]
        totalList = []
        totalList.extend(player.song_list)
        totalList.extend(player.album_list)
        totalList.extend(player.artist_list)
        for check in totalList:
            if id == check["Id"]:
                found = check
                break
        try:
            if not found == []:
                message = ""
                imageid = ""
                if found.get("Type") == "Song":
                    artist = ""
                    for i in found["Artists"]:
                        artist = artist + " " + i
                    message = "**Name:** " + found["Name"] + "\n**Artists:** " + artist + "\n**Album:** " + found.get("Album") + "\n**Album Id:**" + found.get("AlbumId") + "\n**Id: **" + found["Id"] + "\n**Production Year: **" + str(found.get("ProductionYear")) + "\n**Type: **Song"
                    imageid = image_url.replace('(id)', found['AlbumId'])
                elif found.get("Type") == "Album":
                    artist = ""
                    for i in found["Artists"]:
                        artist = artist + " " + i
                    message = "**Name:** " + found["Name"] + "\n**Artists:** " + artist + "\n**Production Year:** " + str(found.get("ProductionYear")) + "\n**Type: **" + "Album"
                    imageid = image_url.replace('(id)', found['AlbumId'])
                else:
                    message = "**Name: **" + found["Name"] + "\n**Id: **" + found["Id"] + "\n**Type:** Artist"
                    imageid = image_url.replace('(id)', found['Id'])
                await helpers.embededs("Found Data", message, imageid)
            else:
                await helpers.error("No Data Found")
        except Exception as e:
            print("Error: " + e)
    else:
        await helpers.error("Too many ids provided, please provide no more than 1 id")