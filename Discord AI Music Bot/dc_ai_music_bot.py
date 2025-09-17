import os
import sys

from discord.ext import commands
import discord

import yt_dlp
from yt_dlp import YoutubeDL
import asyncio

import google.generativeai as genai
from google.genai import types

from gtts import gTTS
import io
from io import BytesIO
import time

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
FFMPEG_SPEAK_OPTIONS = {
    'options':'-vn -filter:a "atempo=1.25"'
}

GEMINI_API_KEY = api_requeriments.gemini_api_key
BOT_TOKEN = api_requeriments.BOT_TOKEN
CHANNEL_ID = api_requeriments.channel_id


intents = discord.Intents.default()
intents.message_content = True 
intents.voice_states = True
bot = commands.Bot(command_prefix='!',intents= intents,help_command=None)


@bot.event # its for i am ready message
async def on_ready():
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send('I am ready to be used :D')

@bot.command()#to close my pc
async def shutdown(ctx):
    async with ctx.channel.typing():
        await ctx.channel.send('closing in 10 sec...')
        os.system("script.bat")


@bot.command() # clear the queue
async def clear(ctx):
    async with ctx.channel.typing():
        my_queue.clear()
        await ctx.channel.send("queue is now empty")
@bot.command() # add to queue
async def add(ctx, *, song: str):
    async with ctx.channel.typing():
        await ctx.channel.send(f" '{song}' added to the queue")
    my_queue.append(song)
@bot.command() # remove from queue
async def remove(ctx, *, song: str):
    async with ctx.channel.typing():
        for i in my_queue:
            if song.lower() in i.lower():
                my_queue.remove(i)
                await ctx.channel.send(f"Removed from queue: {i}")
                return
        await ctx.channel.send(f"Song '{song}' not found in the queue.")
@bot.command() # pause
async def pause(ctx):
    async with ctx.channel.typing():
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("Playback paused.")
        else:
            await ctx.send("There is no audio playing.")
@bot.command() # resume
async def resume(ctx):
    async with ctx.channel.typing():
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("Playback resumed.")
        else:
            await ctx.send("The audio is not paused.")
@bot.command() # skip
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
@bot.command() # leave
async def leave(ctx):
    async with ctx.channel.typing():
        if ctx.voice_client is None:
            await ctx.send("I am not in a voice channel!")
            return
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")
@bot.command(name='queue')  # show queue (function renamed to avoid shadowing global `queue` list)
async def show_queue(ctx):
    if len(my_queue) == 0:
        await ctx.send("Queue is empty.")
    else:
        await ctx.send('\n'.join(my_queue))
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
        mp3_fp = io.BytesIO()
        tts = gTTS(text="merhaba", lang='tr')
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        await asyncio.sleep(0.5)
        source = discord.FFmpegOpusAudio(mp3_fp, pipe=True,**FFMPEG_SPEAK_OPTIONS)
        ctx.voice_client.play(source)
        await ctx.send(f"Connected to {voice_channel.name}")
@bot.command()#speak
async def speak(ctx, *, text):
    if ctx.author.voice is None:
        await ctx.send("You need to be in a voice channel!")
        return
    async with ctx.channel.typing():
        await ctx.send("Wait a moment...")
    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()
    if ctx.voice_client and ctx.voice_client.is_playing():
        await ctx.send("The bot is currently playing audio, please wait.")
        return
    mp3_fp = io.BytesIO()
    tts = gTTS(text=text, lang='tr')
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    await asyncio.sleep(0.5)
    source = discord.FFmpegOpusAudio(mp3_fp, pipe=True,**FFMPEG_SPEAK_OPTIONS)
    ctx.voice_client.play(source)
@bot.command() # play
async def play(ctx):
    global play_stopped
    play_stopped = False
    if ctx.author.voice is None:
        await ctx.send("You need to be in a voice channel!")
        return
    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()
        mp3_fp = io.BytesIO()
        tts = gTTS(text="merhaba", lang='tr')
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        await asyncio.sleep(0.5)
        source = discord.FFmpegOpusAudio(mp3_fp, pipe=True,**FFMPEG_SPEAK_OPTIONS)
        ctx.voice_client.play(source)
    await asyncio.sleep(0.5)
    if len(my_queue) > 0:
        await ctx.channel.send("It may take a while to load the song")
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


#AI PART
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')
config=types.GenerateContentConfig(response_modalities=['TEXT'],max_output_tokens=256)

@bot.command() #working with AI(gemini from google)
async def translate(ctx, *, sentence):
    async with ctx.channel.typing():
        response = model.generate_content(f"translate this to turkish'{sentence}'")
        await asyncio.sleep(0.5)
        await ctx.channel.send(response.text)
user_list = {}
@bot.command() #for chatting with AI 
async def chat(ctx, *, sentence):
    async with ctx.channel.typing():
        if ctx.author.id in user_list:
            response = user_list[ctx.author.id].send_message(f"{sentence}.give a short answer")
        else:
            user_list[ctx.author.id] = model.start_chat()
        response = user_list[ctx.author.id].send_message(f"{sentence}.give a short answer")
        await ctx.channel.send(response.text)



@bot.command()
async def help(ctx):
    async with ctx.channel.typing():
        embed = discord.Embed(
            title="Help — Commands",
            description="Quick note: To play a song, first add it to the queue with `!add <song name>`, then use `!play`.",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Queue", value="`!add <song>` — Add a song to the queue\n`!remove <name>` — Remove a song from the queue\n`!clear` — Clear the queue\n`!queue` — Show the current queue", inline=False)
        embed.add_field(name="Playback", value="`!play` — Bot joins the voice channel and plays the queue\n`!pause` — Pause playback\n`!resume` — Resume playback\n`!skip` — Skip to the next song\n`!stop` — Stop playback and clear the queue", inline=False)
        embed.add_field(name="Voice (TTS)", value="`!speak <text>` — Bot speaks the given text in Turkish", inline=False)
        embed.add_field(name="AI", value="`!translate <text>` — Translate text to Turkish\n`!chat <message>` — Chat with Gemini AI", inline=False)
        embed.add_field(name="Voice Channel", value="`!join` — Bot joins your voice channel\n`!leave` — Bot leaves the voice channel", inline=False)
        embed.add_field(name="Help", value="`!help` — Show this help message", inline=False)
        embed.set_footer(text=f"Prefix: ! | Developed by mirage")

        await ctx.send(embed=embed)

bot.run(BOT_TOKEN)

