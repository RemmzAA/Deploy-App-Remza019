"""
REMZA019 Gaming - Discord Bot (Renamed to avoid cache)
Cross-platform notifications, commands, and community engagement
"""
import discord
from discord.ext import commands, tasks
import os
import asyncio
import aiohttp
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot Configuration
DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
API_BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
DISCORD_CHANNEL_ID = os.environ.get('DISCORD_NOTIFICATION_CHANNEL')

# Bot setup - DISABLE DEFAULT HELP
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Track last stream status
last_stream_status = False

@bot.event
async def on_ready():
    logger.info(f'✅ REMZA019 Bot logged in as {bot.user.name}!')
    logger.info(f'Connected to {len(bot.guilds)} server(s)')
    
    # Start background tasks
    if not check_stream_status.is_running():
        check_stream_status.start()
    
    logger.info('🔄 Stream monitoring started!')

@bot.command(name='points')
async def get_points(ctx, username: str = None):
    """Check your points balance"""
    if not username:
        await ctx.send("❌ Usage: `!points <username>`")
        return
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/api/viewer/profile/{username}") as response:
                if response.status == 200:
                    data = await response.json()
                    embed = discord.Embed(title=f"🎮 {username}'s Stats", color=discord.Color.green())
                    embed.add_field(name="Points", value=f"⭐ {data.get('points', 0)}", inline=True)
                    embed.add_field(name="Level", value=f"🏆 {data.get('level', 1)}", inline=True)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"❌ User '{username}' not found!")
    except Exception as e:
        logger.error(f"Error fetching points: {e}")
        await ctx.send("❌ Error fetching points.")

@bot.command(name='leaderboard')
async def leaderboard(ctx, limit: int = 10):
    """Show top players"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/api/viewer/leaderboard?limit={limit}") as response:
                if response.status == 200:
                    data = await response.json()
                    leaderboard_data = data.get('leaderboard', [])
                    
                    embed = discord.Embed(title="🏆 Leaderboard", color=discord.Color.gold())
                    for player in leaderboard_data[:limit]:
                        embed.add_field(
                            name=f"#{player.get('rank')} {player.get('username')}",
                            value=f"⭐ {player.get('points')} points",
                            inline=False
                        )
                    await ctx.send(embed=embed)
    except Exception as e:
        logger.error(f"Error: {e}")
        await ctx.send("❌ Error fetching leaderboard.")

@bot.command(name='live')
async def check_live(ctx):
    """Check if stream is live"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/api/twitch/status") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('is_live'):
                        embed = discord.Embed(title="🔴 REMZA019 IS LIVE!", color=discord.Color.red())
                        embed.add_field(name="Game", value=data.get('game_name', 'Unknown'), inline=True)
                        embed.add_field(name="Viewers", value=f"👥 {data.get('viewer_count', 0)}", inline=True)
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send("⚪ Stream is offline.")
    except Exception as e:
        logger.error(f"Error: {e}")
        await ctx.send("❌ Error checking stream.")

@bot.command(name='help')
async def help_cmd(ctx):
    """Show commands"""
    embed = discord.Embed(title="🤖 REMZA019 Bot Commands", color=discord.Color.purple())
    embed.add_field(name="!points <user>", value="Check points", inline=False)
    embed.add_field(name="!leaderboard", value="Top players", inline=False)
    embed.add_field(name="!live", value="Check stream status", inline=False)
    await ctx.send(embed=embed)

@tasks.loop(minutes=2)
async def check_stream_status():
    """Check stream and notify"""
    global last_stream_status
    if not DISCORD_CHANNEL_ID:
        return
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/api/twitch/status") as response:
                if response.status == 200:
                    data = await response.json()
                    is_live = data.get('is_live', False)
                    if is_live and not last_stream_status:
                        channel = bot.get_channel(int(DISCORD_CHANNEL_ID))
                        if channel:
                            embed = discord.Embed(title="🔴 REMZA019 JUST WENT LIVE!", color=discord.Color.red())
                            await channel.send("@everyone 🎮 Stream is LIVE!", embed=embed)
                    last_stream_status = is_live
    except Exception as e:
        logger.error(f"Error: {e}")

@check_stream_status.before_loop
async def before_check():
    await bot.wait_until_ready()

if __name__ == "__main__":
    if not DISCORD_BOT_TOKEN:
        logger.error("❌ DISCORD_BOT_TOKEN not set!")
    else:
        bot.run(DISCORD_BOT_TOKEN)
