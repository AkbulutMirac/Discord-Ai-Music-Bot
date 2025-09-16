import os
import sys

from discord.ext import commands
import discord

import yt_dlp
from yt_dlp import YoutubeDL
import asyncio

import google.generativeai as genai
from google.genai import types

import api_requeriments

queue = []
my_queue = []
play_stopped = False
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'extract_flat': False,
    'quiet': True,
    'default_search': 'ytsearch',
    'forceurl': True,
    'forcejson': True
}
FFMPEG_OPTIONS = {
    'before_options': '-thread_queue_size 512 -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options':'-vn -ar 48000 -ac 2 -f opus'
}
GEMINI_API_KEY = api_requeriments.gemini_api_key
BOT_TOKEN = api_requeriments.BOT_TOKEN
CHANNEL_ID = api_requeriments.channel_id

intents = discord.Intents.default()
intents.message_content = True 
intents.voice_states = True
bot = commands.Bot(command_prefix='!',intents= intents,help_command=None)


@bot.event
async def on_ready():
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send('I am ready to be used :D')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith('hello'):
        await message.channel.send('hello!')
    await bot.process_commands(message) # whenever use on_message bot wont process commands unless you add this line
    #                                   # because on_message overrides the default command processing.
    #                                   # process_commands(message) is control the message wheter it is command or not.

@bot.command() # join
async def join(ctx):
    async with ctx.channel.typing():
        if ctx.author.voice is None:
            await ctx.send("You need to be in a voice channel!")
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            await ctx.send("I am already in the voice channel!")
            return
        voice_client = await voice_channel.connect()
        await ctx.send(f"Connected to {voice_channel.name}")

@bot.command()
async def clear(ctx):
    async with ctx.channel.typing():
        my_queue.clear()
        await ctx.channel.send("queue is now empty")

@bot.command()
async def add(ctx, *, song: str):
    async with ctx.channel.typing():
        await ctx.channel.send(f" '{song}' added to the queue")
    my_queue.append(song)
@bot.command()
async def remove(ctx, *, song: str):
    async with ctx.channel.typing():
        for i in my_queue:
            if song.lower() in i.lower():
                my_queue.remove(i)
                await ctx.channel.send(f"Removed from queue: {i}")
                return
        await ctx.channel.send(f"Song '{song}' not found in the queue.")
@bot.command()
async def pause(ctx):
    async with ctx.channel.typing():
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("Playback paused.")
        else:
            await ctx.send("There is no audio playing.")
@bot.command()
async def resume(ctx):
    async with ctx.channel.typing():
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("Playback resumed.")
        else:
            await ctx.send("The audio is not paused.")

@bot.command()
async def play(ctx):
    global play_stopped
    play_stopped = False
    if ctx.voice_client is None:
        await ctx.send("Bot is not connected to a voice channel. Use !join first.")
        return
    if len(my_queue) > 0:
        await ctx.channel.send("it may take a while to load the song")
    if ctx.voice_client is None:
        await ctx.send("Bot is not connected to a voice channel. Use !join first.")
        return
    if len(my_queue) == 0:
        await ctx.send("Queue is empty. Add songs with !add.")
        return
    
    loop = asyncio.get_event_loop()
    def ytdlp_extract():
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            return ydl.extract_info(f"ytsearch:{my_queue[0]}", download=False)
    result = await loop.run_in_executor(None, ytdlp_extract)
    first_result = result['entries'][0]
    url = first_result['url']
    title = first_result['title']
    queue.append((url, title))
    my_queue.pop(0)
    url, title = queue.pop(0)
    source = discord.FFmpegOpusAudio(url, **FFMPEG_OPTIONS)

    def after_playing(error):
        # Do not auto-start next track if stop() was called
        if error:
            print(f"Error: {error}")
        if play_stopped:
            return
        fut = asyncio.run_coroutine_threadsafe(play(ctx), bot.loop)
        try:
            fut.result()
        except Exception as e:
            print(f"After playing error: {e}")
    ctx.voice_client.play(source, after=after_playing)
    await ctx.send(f"Now playing: {title}")



@bot.command() # leave
async def leave(ctx):
    async with ctx.channel.typing():
        if ctx.voice_client is None:
            await ctx.send("I am not in a voice channel!")
            return
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")

@bot.command() # stop
async def skip(ctx):
    async with ctx.channel.typing():
        if ctx.voice_client is None:
            await ctx.send("I am not in a voice channel!")
            return
        if len(my_queue) > 0:
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()
                await ctx.send("Next song is playing.")
                return
        elif len(my_queue) == 0:
            await ctx.send("Queue is empty. Add songs with !add.")
            return
        if not ctx.voice_client.is_playing():
            await ctx.send("There is no audio :D")
            return
        
@bot.command() # stop
async def stop(ctx):
    global play_stopped
    play_stopped = True
    my_queue.clear()
    async with ctx.channel.typing():
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Playback stopped and queue cleaned.")
            return
        else:
            await ctx.send("There is no audio :D")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')
config=types.GenerateContentConfig(
      response_modalities=['TEXT'])

@bot.command() #working with AI(gemini from google)
async def translate(ctx, *, sentence):
    async with ctx.channel.typing():
        response = model.generate_content(f"translate this to turkish'{sentence}'")
        await ctx.channel.send(response.text)

user_list = {}
@bot.command() #for chatting with AI
async def chat(ctx, *, sentence):
    async with ctx.channel.typing():
        if ctx.author.id in user_list:
            response = user_list[ctx.author.id].send_message(f"{sentence}")
        else:
            user_list[ctx.author.id] = model.start_chat()
        response = user_list[ctx.author.id].send_message(f"{sentence}")
        await ctx.channel.send(response.text)
@bot.command()
async def help(ctx):
    async with ctx.channel.typing():
        help_text = """
        !!!!!!!!!!You need to use the join command to be able to use the play command.!!!!!!!!!
        !!!!!!!!!!You need to add songs to the queue with !add before using !play.!!!!!!!!!!!!!
        **Available Commands:**
        `!join` - Bot joins your voice channel.
        `!leave` - Bot leaves the voice channel.
        `!play` - Play a song from the queue.
        `!add <song name or URL>` - Adds a song to the queue without playing immediately.
        `!remove <song name>` - Removes a song from the queue.
        `!pause` - Pauses the current playback.
        `!resume` - Resumes paused playback.
        `!skip` - Skips to the next song in the queue.
        `!stop` - Stops playback and clears the queue.
        `!clear` - Clears the entire song queue.
        `!translate <text>` - Translates text to Turkish using AI.
        `!chat <message>` - Chat with Gemini AI.
        `!help` - Displays this help message.
        """
        await ctx.channel.send(help_text)


bot.run(BOT_TOKEN)
