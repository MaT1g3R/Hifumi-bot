import asyncio

import discord
from discord.ext import commands
from data_controller import DataManager
from data_controller.data_utils import get_prefix
from json import load

if not discord.opus.is_loaded():
    # The 'opus' library here is opus.dll on Windows
    # or libopus.so on Linux in the current directory.
    # You should replace this with the location the
    # opus library is located in and with the proper filename.
    # Note that on Windows XP SP1 and upper versions, this DLL
    # is automatically provided for you.
    raise ValueError('libopus is not loaded, please install the '
                     'library through your package manager or add '
                     'it to your PATH.')

class VoiceEntry:
    def __init__(self, message, player, bot):
        self.bot = bot
        self.bot.localize = bot.localize
        self.server = message.server
        self.requester = message.author
        self.channel = message.channel
        self.message = message
        self.player = player

    def __str__(self):
        localize = self.bot.localize(self.message)
        fmt = localize['song_display']
        duration = self.player.duration
        if duration:
            fmt = fmt + " " + localize['song_duration'].format(divmod(duration, 60))
        if self.player.uploader is None:
            self.player.uploader = "Livestream"
        return fmt.format(self.player, self.requester)

class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.playlist = []
        self.queuelength = 0
        self.voice = None
        self.waitplayer = None
        self.bot = bot
        self.bot.localize = bot.localize
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set()
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    def is_playing(self):
        if self.voice is None or self.current is None \
           or not self.voice.is_connected():
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player
    
    async def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()
    
    def safe_coro(self):
        coro = self.toggle_next()
        fut = asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
        try:
            fut.result()
        except:
            pass

    def safe_coro_two(self):
        coro = self.timeout_leave()
        fut = asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
        try:
            fut.result()
        except:
            pass
            
    def reassign(self, bot):
        self.current = None
        self.playlist = []
        self.queuelength = 0
        self.voice = None
        self.bot = bot
        self.bot.localize = bot.localize
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set()
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())
    
    async def toggle_next(self):
        try:
            self.playlist.remove(self.playlist[0])
            if self.current.player.duration:
                self.queuelength -= self.current.player.duration
            self.bot.loop.call_soon_threadsafe(self.play_next_song.set)
            if self.songs.empty():
                await self.leave()
        except IndexError:
            pass

    async def wait_play(self):
        self.waitplayer = self.voice.create_ffmpeg_player('./music.mp3',
                                              after=self.safe_coro_two)
        self.waitplayer.start()

    async def wait_stop(self):
        if self.waitplayer.is_playing():
            self.waitplayer.pause()
            self.waitplayer.volume = 0
            # FIXME Stop player without invoking timeout leaving function
        else:
            pass
        
    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await self.bot.send_message(self.current.channel,
                           self.bot.localize(self.current.message)['np'].format(
                           str(self.current)))
            self.current.player.start()
            await self.play_next_song.wait()

    async def leave(self):
        if self.is_playing():
            self.current.player.stop()
        if not self.waitplayer.is_playing():
            self.audio_player.cancel()
            await self.voice.disconnect()
            await self.bot.send_message(self.current.channel,
                  self.bot.localize(self.current.message)['music_self_leave'])
            self.reassign(self.bot)
        else:
            pass
        
    async def timeout_leave(self):
        if self.is_playing():
            self.current.player.stop()
        self.audio_player.cancel()
        await self.voice.disconnect()
        await self.bot.send_message(self.current.channel,
                    self.bot.localize(self.current.message)['music_timeout_leave']) 
        self.reassign(self.bot)

class Music:
    """Voice related commands.

    Works in multiple servers at once.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state

        return state

    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

    @commands.command(pass_context=True, no_pm=True)
    async def join(self, ctx):
        """Summons the bot to join your voice channel."""
        localize = self.bot.localize(ctx)
        summoned_channel = ctx.message.author.voice_channel
        if summoned_channel is None:
            await self.bot.say(localize['no_voice'])

        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)
            await self.bot.say(localize['music_join'].format(get_prefix(
                                                             self.bot,
                                                             ctx.message)))
            await state.wait_play()
        else:
            await self.bot.say(localize['music_already_joined'])

    @commands.command(pass_context=True, no_pm=True)
    async def play(self, ctx, *, song: str):
        """Plays a song.

        If there is a song currently in the queue, then it is
        queued until the next song is done playing.

        This command automatically searches as well from YouTube.
        The list of supported sites can be found here:
        https://rg3.github.io/youtube-dl/supportedsites.html
        """
        localize = self.bot.localize(ctx)
        state = self.get_voice_state(ctx.message.server)
        opts = {
            'default_search': 'auto',
            'geo_bypass': True,
            'ignoreerrors': True,
            'quality': 'highest',
            'quiet': True,
        }

        if state.voice is None:
            await self.bot.say(localize['no_play'])
        else:
            try:
                await self.bot.send_typing(ctx.message.channel)
                player = await state.voice.create_ytdl_player(song,
                                                 ytdl_options=opts,
                                             after=state.safe_coro)
            except Exception:
                await self.bot.send_message(ctx.message.channel,
                                               localize['music_error'])
            else:
                player.volume = 2
                entry = VoiceEntry(ctx.message, player, self.bot)
                await self.bot.say(localize['song_queued'].format(str(entry)))
                await state.wait_stop()
                await state.songs.put(entry)
                state.playlist.append(str(entry))
                if player.duration:
                    state.queuelength += player.duration

    @commands.command(pass_context=True, no_pm=True)
    async def volume(self, ctx, value: int):
        """Sets the volume of the currently playing song."""
        localize = self.bot.localize(ctx)
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            if value == 0:
                player.volume = value / 100
                await self.bot.say(localize['volume_mute'])
            elif value >= 1 and value <= 200:
                player.volume = value / 100
                await self.bot.say(localize['volume'].format(int(player.volume * 100)))
            else:
                await self.bot.say(localize['volume_error'])
        else:
            await self.bot.say(localize['no_play'])

    @commands.command(pass_context=True, no_pm=True)
    async def pause(self, ctx):
        """Pauses the currently played song."""
        localize = self.bot.localize(ctx)
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.pause()
            await self.bot.say(localize['pause'].format(get_prefix(self.bot,
                                                                   ctx.message)))
        else:
            await self.bot.say(localize['no_play'])

    @commands.command(pass_context=True, no_pm=True)
    async def resume(self, ctx):
        """Resumes the currently played song."""
        localize = self.bot.localize(ctx)
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.resume()
            await self.bot.say(localize['resume'].format(get_prefix(self.bot,
                                                                    ctx.message)))
        else:
            await self.bot.say(localize['no_play'])

    @commands.command(pass_context=True, no_pm=True)
    async def leave(self, ctx):
        """Stops playing audio and leaves the voice channel.

        This also clears the queue.
        """
        localize = self.bot.localize(ctx)
        server = ctx.message.server
        state = self.get_voice_state(server)

        if state.voice:
            if state.is_playing():
                player = state.player
                player.stop()
        
            try:
                state.audio_player.cancel()
                del self.voice_states[server.id]
                await state.voice.disconnect()
                await self.bot.say(localize['music_leave'])
            except:
                pass
        else:
            await self.bot.say(localize['no_play'])

    @commands.command(pass_context=True, no_pm=True)
    async def skip(self, ctx):
        """Vote to skip a song. The song requester can automatically skip.

        3 skip votes are needed for the song to be skipped.
        """
        localize = self.bot.localize(ctx)
        state = self.get_voice_state(ctx.message.server)
        if not state.is_playing():
            await self.bot.say(localize['no_play'])
            return

        voter = ctx.message.author
        if voter == state.current.requester:
            await self.bot.say(localize['requested_skip'])
            await state.skip()
        elif voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= 3:
                await self.bot.say(localize['success_skip'])
                await state.skip()
            else:
                await self.bot.say(localize['voted_skip'].format(3 - total_votes))
        else:
            await self.bot.say(localize['already_voted'])

    @commands.command(pass_context=True, no_pm=True)
    async def queue(self, ctx, *, page=1):
        """Shows info about the currently played song.
        You can also search by pages.
        """
        localize = self.bot.localize(ctx)
        state = self.get_voice_state(ctx.message.server)
        total_pages = int(len(state.playlist) / 20 + 1)
        if page < 1 or page > total_pages:
            await self.bot.say(localize['invalid_page'])
        elif not isinstance(page, int):
            await self.bot.say(localize['not_integer_page'])
        elif not state.playlist:
            await self.bot.say(localize['empty_queue'])
        else:
            temp = []
            temp.append(localize['np'].format(state.playlist[0]))
            page_playlist = state.playlist[20*page-20:20*page]
            for index in range(len(page_playlist)):
                if page == 1 and index == 0:
                    pass
                elif index == 21:
                    break
                else:
                    temp.append("{}. {}".format((int(20*page-20) + index + 1), 
                                                       page_playlist[index]))
            m, s = divmod(state.queuelength, 60)
            h, m = divmod(m, 60)
            temp.append('')
            temp.append(localize['total_duration'].format(str(h), 
                                                 str(m).zfill(2),
                                                str(s).zfill(2)))
            if total_pages == 1:
                temp.append(localize['page_list'].format(page, total_pages))
            else:
                temp.append(localize['page_extended'].format(page,
                                                             total_pages,
                                                             get_prefix(self.bot,
                                                                   ctx.message)))
            await self.bot.say("\n".join(temp))