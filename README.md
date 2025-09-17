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
- discord.py library
- yt-dlp library
- google.generativeai library
- ffmpeg # Make sure ffmpeg is installed and added to your system PATH
- A Discord bot token # Get it from the Discord Developer Portal
- Google API key for Gemini
- Channel ID for the 'I am ready' message (You can get it by enabling Developer Mode in Discord settings and right-clicking the channel.After that, copy the ID and paste it in the api_requeriments.py file. And then you can get answer from every channel in the server. That was for just 'I am ready' message.)

## Installation
1. Download or clone the repository
2. Install the required libraries
```bash
pip install discord.py yt-dlp google.generativeai pynacl gTTS 
```
3. Set up the bot token and API keys in `api_requeriments.py`
```python
BOT_TOKEN = "your_bot_token"
GEMINI_API_KEY = "your_gemini_api_key"
CHANNEL_ID = "your_channel_id" # Its for just 'I am ready' message.
```
4. Run the bot
```bash
python dc_ai_music_bot.py
```
## Usage
-!!!!!!!!!!You need to use the join command to be able to use the play command.!!!!!!!!!
-!!!!!!!!!!You need to add songs to the queue with !add before using !play.!!!!!!!!!!!!!
- Use `!join` to make the bot join your voice channel
- Use `!play` to play a song # it will play the first song in the queue
- Use `!leave` to make the bot leave the voice channel
- Use `!add <YouTube URL or search term>` to add a song to the queue
- Use `!remove` to remove a song from the queue
- Use `!pause` to pause the current song
- Use `!resume` to resume the paused song
- Use `!skip` to skip the current song
- Use `!stop` to stop playback and clear the queue
- Use `!clear` to clear the queue
- Use `!translate` to translate English to Turkish
- Use `!chat <message>` to chat with the AI (Gemini) #it has a memory for every people who uses it unleess you restart the bot
- Use `!help` to see all commands
## Note
- Make sure ffmpeg is installed and added to your system PATH
- The bot requires permissions to connect, speak, and read messages in the Discord server. You can set these permissions in the Discord Developer Portal when you create your bot.
- The bot uses Google Gemini for AI chat functionality, so ensure you have a valid API key and the google.generativeai library installed
- The bot's AI chat functionality has a memory for each user, which is reset when the bot restarts










