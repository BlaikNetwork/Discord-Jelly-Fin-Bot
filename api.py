import configparser
from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn
import music_commands as commands

config = configparser.ConfigParser()

# Read the config file
config.read('config.cfg')

#api
port = config.getint('API', 'port')

# FastAPI server
app = FastAPI()

def setup(music_player):
    global player
    player = music_player


@app.get("/")
async def web_home():
    return FileResponse("index.html")

@app.get("/api/")
async def home():
    return {"status": "online"}

@app.api_route("/api/auth/", methods=["GET", "POST"])
async def auth(userid, token):
    result = await commands.helpers.auth(userid, token)
    return result

@app.api_route("/api/play/", methods=["GET", "POST"])
async def play(song_name=" "):    
    try:
        result = await commands.play(song_name)
        return result
    except Exception as e:
        return (f"error playing: {e}")

@app.api_route("/api/clearqueue/", methods=["GET", "POST"])
async def clearqueueapi():
    result = await commands.clearqueue()
    return result

@app.api_route("/api/queue/", methods=["GET", "POST"])
async def queueapi():
    result = player.queue_list
    return result

@app.api_route("/api/skip/", methods=["GET", "POST"])
async def skipapi():
    result = await commands.skip()
    return result

@app.api_route("/api/randomplaylist/", methods=["GET", "POST"])
async def randompl(args: str = ""):
    args = tuple(args.split())
    result = await commands.randomplaylist(args)
    return result

@app.get("/api/randomsong/")
async def randoms():
    return await commands.randomsong()

@app.get("/api/pause/")
async def pause():
    return await commands.pause()

@app.get("/api/resume/")
async def resume():
    return await commands.resume()

@app.get("/api/stop/")
async def stop():
    return await commands.stop()

@app.api_route("/api/loop/", methods=["GET", "POST"])
async def loop(id=" "):
    return await commands.loop(id)

@app.api_route("/api/instantmix/", methods=["GET", "POST"])
async def instantmix(id=" "):
    id = tuple(id.split())
    return await commands.instantmix(id)

@app.get("/api/songs/")
async def songs():
    return await commands.helpers.get_song_list()

@app.get("/api/albums/")
async def songs():
    return player.album_list

@app.get("/api/artists/")
async def songs():
    return player.artist_list

@app.get("/api/currentlyplayingsong/")
async def currently_playing_song():
    return player.nowplaying

@app.api_route("/api/playnow/", methods=["GET", "POST"])
async def playnow(id=" "):
    return await commands.playnow(id)

@app.api_route("/api/playnext/", methods=["GET", "POST"])
async def playnext(id=" "):
    return await commands.playnext(id)

@app.api_route("/api/remove/", methods=["GET", "POST"])
async def remove(id=" "):
    return await commands.remove(id)

@app.get("/api/playall/")
async def playall():
    return await commands.playall()

@app.get("/api/updatesongs/")
async def updatesongs():
    return await commands.updatesongs()

@app.api_route("/api/playlist/", methods=["GET", "POST"])
async def play(userid, song_name=" "):    
    try:
        song_name = song_name.split()
        print(song_name)
        result = await commands.playlist(song_name, userid, discord=False)
        return result
    except Exception as e:
        return (f"error playing: {e}")

async def start_api(port):
    print(f"Starting API on port {port}...")
    config = uvicorn.Config(app, host="0.0.0.0", port=port)
    server = uvicorn.Server(config)
    await server.serve()

# Run both together
async def main():
    await start_api(port)
