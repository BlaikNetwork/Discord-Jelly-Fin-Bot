import asyncio

class PlayerState:
    def __init__(self):
        self.playall_active = False
        self.playing = False
        self.looping = False
        self.channel = None
        self.queue_list = []
        self.nowplaying = ""
        self.song_list = []
        self.data = ""
        self.song_finished = asyncio.Event()
        self.artist_list = []
        self.album_list = []