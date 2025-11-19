"""
REMZA019 Gaming - Discord Bot
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
DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN', 'PENDING_USER_INPUT')
API_BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
DISCORD_CHANNEL_ID = os.environ.get('DISCORD_NOTIFICATION_CHANNEL', None)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)  # Disable default help

# Track last stream status
last_stream_status = False

@bot.event
async def on_ready():
    logger.info(f'✅ Discord Bot logged in as {bot.user.name} (ID: {bot.user.id})')
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
                    embed = discord.Embed(
                        title=f"🎮 {username}'s Stats",
                        color=discord.Color.green()
                    )
                    embed.add_field(name="Points", value=f"⭐ {data.get('points', 0)}", inline=True)
                    embed.add_field(name="Level", value=f"🏆 {data.get('level', 1)}", inline=True)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"❌ User '{username}' not found!")
    except Exception as e:
        logger.error(f"Error fetching points: {e}")
        await ctx.send("❌ Error fetching points. Please try again later.")

@bot.command(name='leaderboard')
async def leaderboard(ctx, limit: int = 10):
    """Show top players leaderboard"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/api/viewer/leaderboard?limit={limit}") as response:
                if response.status == 200:
                    data = await response.json()
                    leaderboard_data = data.get('leaderboard', [])
                    
                    embed = discord.Embed(
                        title="🏆 REMZA019 Gaming Leaderboard",
                        description=f"Top {limit} Players",
                        color=discord.Color.gold()
                    )
                    
                    for player in leaderboard_data[:limit]:
                        rank = player.get('rank', '?')
                        username = player.get('username', 'Unknown')
                        points = player.get('points', 0)
                        embed.add_field(
                            name=f"#{rank} {username}",
                            value=f"⭐ {points} points",
                            inline=False
                        )
                    
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Failed to fetch leaderboard!")
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {e}")
        await ctx.send("❌ Error fetching leaderboard. Please try again later.")

@bot.command(name='level')
async def level_info(ctx, username: str = None):
    """Check your level and progress"""
    if not username:
        await ctx.send("❌ Usage: `!level <username>`")
        return
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/api/viewer/profile/{username}") as response:
                if response.status == 200:
                    data = await response.json()
                    embed = discord.Embed(
                        title=f"📊 {username}'s Level Progress",
                        color=discord.Color.blue()
                    )
                    embed.add_field(name="Current Level", value=f"🏆 {data.get('level', 1)}", inline=True)
                    embed.add_field(name="Total Points", value=f"⭐ {data.get('points', 0)}", inline=True)
                    embed.add_field(name="Unlocked Features", value=", ".join(data.get('unlocked_features', ['None'])), inline=False)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"❌ User '{username}' not found!")
    except Exception as e:
        logger.error(f"Error fetching level: {e}")
        await ctx.send("❌ Error fetching level info. Please try again later.")

@bot.command(name='live')
async def check_live(ctx):
    """Check if REMZA019 is currently live"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/api/twitch/status") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('is_live'):
                        embed = discord.Embed(
                            title="🔴 REMZA019 IS LIVE!",
                            description=data.get('title', 'Live Stream'),
                            color=discord.Color.red(),
                            url="https://www.twitch.tv/remza019"
                        )
                        embed.add_field(name="Game", value=data.get('game_name', 'Unknown'), inline=True)
                        embed.add_field(name="Viewers", value=f"👥 {data.get('viewer_count', 0)}", inline=True)
                        
                        if data.get('thumbnail_url'):
                            embed.set_image(url=data['thumbnail_url'])
                        
                        embed.add_field(name="Watch Now", value="[Click here to watch](https://www.twitch.tv/remza019)", inline=False)
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send("⚪ REMZA019 is currently offline. Check back later!")
                else:
                    await ctx.send("❌ Failed to check stream status!")
    except Exception as e:
        logger.error(f"Error checking live status: {e}")
        await ctx.send("❌ Error checking stream status. Please try again later.")

@bot.command(name='bothelp')
async def help_command(ctx):
    """Show all available commands"""
    embed = discord.Embed(
        title="🤖 REMZA019 Gaming Bot Commands",
        description="All available commands for the bot",
        color=discord.Color.purple()
    )
    
    commands_list = [
        ("!points <username>", "Check your points balance"),
        ("!level <username>", "Check your level and progress"),
        ("!leaderboard [limit]", "Show top players (default: 10)"),
        ("!live", "Check if REMZA019 is currently live"),
        ("!bothelp", "Show this help message")
    ]
    
    for cmd, description in commands_list:
        embed.add_field(name=cmd, value=description, inline=False)
    
    embed.set_footer(text="REMZA019 Gaming | remza019.com")
    await ctx.send(embed=embed)

@tasks.loop(minutes=2)
async def check_stream_status():
    """Background task to check Twitch stream status and notify"""
    global last_stream_status
    
    if not DISCORD_CHANNEL_ID:
        return
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/api/twitch/status") as response:
                if response.status == 200:
                    data = await response.json()
                    is_live = data.get('is_live', False)
                    
                    # Notify when going live
                    if is_live and not last_stream_status:
                        channel = bot.get_channel(int(DISCORD_CHANNEL_ID))
                        if channel:
                            embed = discord.Embed(
                                title="🔴 REMZA019 JUST WENT LIVE!",
                                description=data.get('title', 'Live Stream'),
                                color=discord.Color.red(),
                                url="https://www.twitch.tv/remza019"
                            )
                            embed.add_field(name="Game", value=data.get('game_name', 'Unknown'), inline=True)
                            embed.add_field(name="Viewers", value=f"👥 {data.get('viewer_count', 0)}", inline=True)
                            
                            if data.get('thumbnail_url'):
                                embed.set_image(url=data['thumbnail_url'])
                            
                            embed.add_field(name="Watch Now", value="[Click here to watch](https://www.twitch.tv/remza019)", inline=False)
                            
                            await channel.send("@everyone 🎮 **REMZA019 is now LIVE!**", embed=embed)
                            logger.info("✅ Sent live notification to Discord!")
                    
                    last_stream_status = is_live
                    
    except Exception as e:
        logger.error(f"Error in stream check task: {e}")

@check_stream_status.before_loop
async def before_check_stream_status():
    """Wait until bot is ready before starting the task"""
    await bot.wait_until_ready()

def run_discord_bot():
    """Start the Discord bot"""
    if DISCORD_BOT_TOKEN == 'PENDING_USER_INPUT':
        logger.warning("⚠️ DISCORD_BOT_TOKEN not set! Discord bot will not start.")
        logger.warning("To enable Discord bot:")
        logger.warning("1. Create a bot at https://discord.com/developers/applications")
        logger.warning("2. Add DISCORD_BOT_TOKEN to .env file")
        logger.warning("3. Invite bot to your server")
        return
    
    try:
        bot.run(DISCORD_BOT_TOKEN)
    except Exception as e:
        logger.error(f"❌ Failed to start Discord bot: {e}")

if __name__ == "__main__":
    run_discord_bot()
