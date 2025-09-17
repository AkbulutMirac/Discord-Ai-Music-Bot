# Discord Music Bot
This is a Discord music bot built using Python and the discord.py library. The bot can join voice channels, play music from YouTube, and respond to user commands.

## Features
- Join and leave voice channels
- Play music from YouTube
- Control playback (play, pause, resume, skip, stop)
- Manage a queue of songs
- Persnonal Ai chat with memory (Gemini from Google)
- Use !help to see all commands

## Requirements
- Python 3.8 or higher
- ffmpeg # Make sure ffmpeg is installed and added to your system PATH
- A Discord bot token # Get it from the Discord Developer Portal
- Google API key for Gemini
- Channel ID for the 'I am ready' message (You can get it by enabling Developer Mode in Discord settings and right-clicking the channel.After that, copy the ID and paste it in the api_requeriments.py file. And then you can get answer from every channel in the server. That was for just 'I am ready' message.)

## Installation
1.Download the python and intall it
2. Download or clone the repository
3. Run cmd as administrator and write this code to install libraries
```bash
pip install discord.py yt-dlp google.generativeai pynacl gTTS 
```
4. Set up the bot token and API keys in `api_requeriments.py`
```python
BOT_TOKEN = "your_bot_token"
GEMINI_API_KEY = "your_gemini_api_key"
CHANNEL_ID = "your_channel_id" # Its for just 'I am ready' message.
```
5. Run cmd as administrator and use this code to run. 
```bash
cd <your path to discord ai music bot file> #C:\Users\yourname\OneDrive\Desktop\Discord AI Music Bot
python dc_ai_music_bot.py
```
## Usage
Quick note: To play a song, first add it to the queue with `!add <song name>`, then use !play.
### Queue
- `!add <song>` — Add a song to the queue
- `!remove <name>` — Remove a song from the queue
- `!clear` — Clear the queue
- `!queue` — Show the current queue
### Playback
- `!play` — Bot joins the voice channel and plays the queue
- `!pause` — Pause playback
- `!resume` — Resume playback
- `!skip` — Skip to the next song
- `!stop` — Stop playback and clear the queue
### Voice (TTS)
- `!speak` <text> — Bot speaks the given text in Turkish
### AI
- `!translate` <text> — Translate text to Turkish
- `!chat <message>` — Chat with Gemini AI
### Voice Channel
- `!join` — Bot joins your voice channel
- `!leave` — Bot leaves the voice channel
### Help
- `!help` — Show this help message
## Note
- Make sure ffmpeg is installed and added to your system PATH
- The bot requires permissions to connect, speak, and read messages in the Discord server. You can set these permissions in the Discord Developer Portal when you create your bot.
- The bot uses Google Gemini for AI chat functionality, so ensure you have a valid API key and the google.generativeai library installed
- The bot's AI chat functionality has a memory for each user, which is reset when the bot restarts











