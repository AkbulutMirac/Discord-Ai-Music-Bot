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
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -filter:a "volume=0.25"'}

GEMINI_API_KEY = api_requeriments.gemini_api_key
BOT_TOKEN = api_requeriments.BOT_TOKEN
CHANNEL_ID = api_requeriments.channel_id

intents = discord.Intents.default()
intents.message_content = True 
intents.voice_states = True
bot = commands.Bot(command_prefix='!',intents= intents,help_command=None)


@bot.event
async def on_ready():
    channel = bot.get_channel(CHANNEL_ID) # this wont work unless you add channel id to api_requeriments.py
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
    
    if ctx.author.voice is None:
        await ctx.send("You need to be in a voice channel!")
    voice_channel = ctx.author.voice.channel
    voice_client = await voice_channel.connect()
    await ctx.send(f"Connected to {voice_channel.name}")

@bot.command() #clear the queue
async def clear(ctx):
    queue.clear()
    await ctx.channel.send("queue is now empty")

@bot.command()
async def add(ctx, *, song: str):
    loop = asyncio.get_event_loop()
    def ytdlp_extract():
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            return ydl.extract_info(f"ytsearch:{song}", download=False)
    result = await loop.run_in_executor(None, ytdlp_extract)
    first_result = result['entries'][0]
    url = first_result['url']
    title = first_result['title']
    queue.append((url, title))
    await ctx.channel.send(f"Added to queue: {title}")
@bot.command()
async def remove(ctx, *, song: str):
    for i, (url, title) in enumerate(queue):
        if song.lower() in title.lower():
            del queue[i]
            await ctx.channel.send(f"Removed from queue: {title}")
            return
    await ctx.channel.send(f"Song '{song}' not found in the queue.")
@bot.command()
async def pause(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Playback paused.")
    else:
        await ctx.send("There is no audio playing.")
@bot.command()
async def resume(ctx):
    if ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Playback resumed.")
    else:
        await ctx.send("The audio is not paused.")

@bot.command()
async def play(ctx):
    if ctx.voice_client is None:
        await ctx.send("Bot is not connected to a voice channel. Use !join first.")
        return
    if len(queue) == 0:
        await ctx.send("Queue is empty. Add songs with !add.")
        return
    url, title = queue.pop(0)
    source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)
    def after_playing(error):
        if error:
            print(f"Error: {error}")
        fut = asyncio.run_coroutine_threadsafe(play(ctx), bot.loop)
        try:
            fut.result()
        except Exception as e:
            print(f"After playing error: {e}")
    ctx.voice_client.play(source, after=after_playing)
    await ctx.send(f"Now playing: {title}")



@bot.command() # leave
async def leave(ctx):
    await ctx.voice_client.disconnect()
    await ctx.send("Disconnected from the voice channel.")

@bot.command() # stop
async def skip(ctx):
    if len(queue) > 0:
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Next song is playing.")
    elif len(queue) == 0:
        await ctx.send("Queue is empty. Add songs with !add.")
    if not ctx.voice_client.is_playing():
        await ctx.send("There is no audio :D")
        
@bot.command() # stop
async def stop(ctx):
    queue.clear()
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Playback stopped and queue cleaned.")
    else:
        await ctx.send("There is no audio :D")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')
config=types.GenerateContentConfig(
      response_modalities=['TEXT', 'IMAGE'])

@bot.command() #working with AI(gemini from google)
async def translate(ctx, *, sentence):
    response = model.generate_content(f"translate this to turkis'{sentence}'")
    await ctx.channel.send(response.text)

user_list = {}
@bot.command() #for chatting with AI
async def chat(ctx, *, sentence):
    if ctx.author.id in user_list:
        response = user_list[ctx.author.id].send_message(f"{sentence}")
    else:
        user_list[ctx.author.id] = model.start_chat()
        response = user_list[ctx.author.id].send_message(f"{sentence}")
    await ctx.channel.send(response.text)
@bot.command()
async def help(ctx):
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

