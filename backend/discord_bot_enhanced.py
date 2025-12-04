"""
REMZA019 Gaming - Enhanced Discord Bot
Real-time stream notifications, schedule, stats, and community engagement
"""
import discord
from discord.ext import commands, tasks
import os
import asyncio
import aiohttp
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv(Path(__file__).parent / '.env')

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

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Track last stream status for notifications
last_stream_status = False
notified_users = set()  # Users who want live notifications

# Day name mapping
DAY_NAMES = {
    'MON': 'Ponedeljak',
    'TUE': 'Utorak',
    'WED': 'Sreda',
    'THU': 'Četvrtak',
    'FRI': 'Petak',
    'SAT': 'Subota',
    'SUN': 'Nedelja'
}

@bot.event
async def on_ready():
    logger.info(f'✅ Discord Bot logged in as {bot.user.name} (ID: {bot.user.id})')
    logger.info(f'Connected to {len(bot.guilds)} server(s)')
    
    # Start background tasks
    if not check_stream_status.is_running():
        check_stream_status.start()
    
    logger.info('🔄 Stream monitoring started!')

# ==================== SCHEDULE COMMANDS ====================

@bot.command(name='schedule')
async def show_schedule(ctx):
    """Prikaži nedeljni raspored streamova"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/api/schedule") as response:
                if response.status == 200:
                    data = await response.json()
                    schedule = data.get('schedule', [])
                    
                    if not schedule:
                        await ctx.send("📅 Trenutno nema zakazanih streamova.")
                        return
                    
                    embed = discord.Embed(
                        title="📅 REMZA019 Gaming - Raspored Streamova",
                        description="Nedeljni raspored svih streamova",
                        color=discord.Color.blue()
                    )
                    
                    # Sort by day
                    day_order = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
                    sorted_schedule = sorted(schedule, key=lambda x: day_order.index(x['day']) if x['day'] in day_order else 999)
                    
                    for item in sorted_schedule:
                        day = item.get('day', '?')
                        time = item.get('time', '?')
                        game = item.get('game', 'TBA')
                        day_name = DAY_NAMES.get(day, day)
                        
                        embed.add_field(
                            name=f"🗓️ {day_name}",
                            value=f"🕐 **{time}** CET\n🎮 {game}",
                            inline=True
                        )
                    
                    embed.set_footer(text="🔔 Koristi !notify za notifikacije kada stream počne!")
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Nije moguće učitati raspored. Pokušaj ponovo kasnije.")
    except Exception as e:
        logger.error(f"Error fetching schedule: {e}")
        await ctx.send("❌ Greška pri učitavanju rasporeda.")

@bot.command(name='nextstream')
async def next_stream(ctx):
    """Prikaži kada je sledeći stream"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/api/schedule") as response:
                if response.status == 200:
                    data = await response.json()
                    schedule = data.get('schedule', [])
                    
                    if not schedule:
                        await ctx.send("📅 Nema zakazanih streamova.")
                        return
                    
                    # Find next stream
                    now = datetime.now()
                    current_day = now.strftime('%a').upper()[:3]
                    current_time = now.strftime('%H:%M')
                    
                    day_order = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
                    current_day_idx = day_order.index(current_day) if current_day in day_order else 0
                    
                    # Find next stream
                    next_item = None
                    for i in range(7):
                        check_day = day_order[(current_day_idx + i) % 7]
                        for item in schedule:
                            if item['day'] == check_day:
                                if i == 0 and item['time'] > current_time:
                                    next_item = item
                                    break
                                elif i > 0:
                                    next_item = item
                                    break
                        if next_item:
                            break
                    
                    if not next_item:
                        next_item = schedule[0]  # Fallback to first item
                    
                    day_name = DAY_NAMES.get(next_item['day'], next_item['day'])
                    
                    embed = discord.Embed(
                        title="⏰ Sledeći Stream",
                        color=discord.Color.purple()
                    )
                    embed.add_field(name="📅 Dan", value=day_name, inline=True)
                    embed.add_field(name="🕐 Vreme", value=f"{next_item['time']} CET", inline=True)
                    embed.add_field(name="🎮 Igra", value=next_item['game'], inline=False)
                    embed.set_footer(text="🔔 Koristi !notify da dobiješ notifikaciju!")
                    
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Nije moguće učitati raspored.")
    except Exception as e:
        logger.error(f"Error fetching next stream: {e}")
        await ctx.send("❌ Greška pri traženju sledećeg streama.")

# ==================== STATS COMMANDS ====================

@bot.command(name='stats')
async def channel_stats(ctx):
    """Prikaži statistiku YouTube kanala"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/api/youtube/channel-stats") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    embed = discord.Embed(
                        title="📊 REMZA019 Gaming - Channel Stats",
                        description="Real-time YouTube statistika",
                        color=discord.Color.red()
                    )
                    
                    embed.add_field(
                        name="👥 Subscribers",
                        value=f"**{data.get('subscriber_count', 'N/A')}**",
                        inline=True
                    )
                    embed.add_field(
                        name="📹 Videos",
                        value=f"**{data.get('video_count', 'N/A')}**",
                        inline=True
                    )
                    embed.add_field(
                        name="👀 Total Views",
                        value=f"**{data.get('view_count', 'N/A')}**",
                        inline=True
                    )
                    
                    embed.set_footer(text="📺 youtube.com/@REMZA019")
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Nije moguće učitati statistiku.")
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        await ctx.send("❌ Greška pri učitavanju statistike.")

@bot.command(name='live')
async def check_live_status(ctx):
    """Proveri da li je REMZA019 trenutno live"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/api/live/status") as response:
                if response.status == 200:
                    data = await response.json()
                    is_live = data.get('is_live', False)
                    
                    if is_live:
                        viewers = data.get('current_viewers', '0')
                        game = data.get('live_game', 'FORTNITE')
                        
                        embed = discord.Embed(
                            title="🔴 REMZA019 JE LIVE!",
                            description=f"🎮 Trenutno igra: **{game}**",
                            color=discord.Color.red()
                        )
                        embed.add_field(name="👥 Viewers", value=viewers, inline=True)
                        embed.add_field(name="📺 Link", value="[Watch on YouTube](https://youtube.com/@REMZA019)", inline=False)
                        await ctx.send(embed=embed)
                    else:
                        embed = discord.Embed(
                            title="⚪ REMZA019 nije live",
                            description="Proveri !schedule za raspored streamova",
                            color=discord.Color.dark_grey()
                        )
                        await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Nije moguće proveriti live status.")
    except Exception as e:
        logger.error(f"Error checking live status: {e}")
        await ctx.send("❌ Greška pri proveri live statusa.")

# ==================== USER COMMANDS ====================

@bot.command(name='points')
async def get_points(ctx, username: str = None):
    """Proveri svoje poene i nivo"""
    if not username:
        await ctx.send("❌ Koristi: `!points <username>`")
        return
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/api/viewer/profile/{username}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    embed = discord.Embed(
                        title=f"🎮 {username}'s Profile",
                        color=discord.Color.green()
                    )
                    embed.add_field(name="⭐ Points", value=f"**{data.get('points', 0)}**", inline=True)
                    embed.add_field(name="🏆 Level", value=f"**{data.get('level', 1)}**", inline=True)
                    
                    # Add level name if available
                    level_name = data.get('level_name')
                    if level_name:
                        embed.add_field(name="👤 Rank", value=level_name, inline=False)
                    
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"❌ User '{username}' nije pronađen!")
    except Exception as e:
        logger.error(f"Error fetching points: {e}")
        await ctx.send("❌ Greška pri učitavanju poena.")

@bot.command(name='leaderboard')
async def leaderboard(ctx, limit: int = 10):
    """Prikaži top igrače"""
    if limit > 20:
        limit = 20
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/api/viewer/leaderboard?limit={limit}") as response:
                if response.status == 200:
                    data = await response.json()
                    leaderboard_data = data.get('leaderboard', [])
                    
                    if not leaderboard_data:
                        await ctx.send("📊 Leaderboard je trenutno prazan.")
                        return
                    
                    embed = discord.Embed(
                        title="🏆 REMZA019 Gaming Leaderboard",
                        description=f"Top {len(leaderboard_data)} igrača",
                        color=discord.Color.gold()
                    )
                    
                    medals = ['🥇', '🥈', '🥉']
                    for idx, player in enumerate(leaderboard_data[:limit]):
                        rank = idx + 1
                        username = player.get('username', 'Unknown')
                        points = player.get('points', 0)
                        level = player.get('level', 1)
                        
                        medal = medals[idx] if idx < 3 else f"#{rank}"
                        
                        embed.add_field(
                            name=f"{medal} {username}",
                            value=f"⭐ {points} pts • 🏆 Level {level}",
                            inline=False
                        )
                    
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Nije moguće učitati leaderboard.")
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {e}")
        await ctx.send("❌ Greška pri učitavanju leaderboard-a.")

# ==================== NOTIFICATION COMMANDS ====================

@bot.command(name='notify')
async def toggle_notifications(ctx):
    """Prijavi se ili odjavi za live notifikacije"""
    user_id = ctx.author.id
    
    if user_id in notified_users:
        notified_users.remove(user_id)
        await ctx.send(f"🔕 {ctx.author.mention}, odjavljen si sa live notifikacija.")
    else:
        notified_users.add(user_id)
        await ctx.send(f"🔔 {ctx.author.mention}, prijavljen si za live notifikacije! Dobijaćeš DM kada REMZA019 bude live.")

# ==================== HELP COMMAND ====================

@bot.command(name='help', aliases=['commands', 'bothelp'])
async def help_command(ctx):
    """Prikaži sve dostupne komande"""
    embed = discord.Embed(
        title="🤖 REMZA019 Gaming Bot - Komande",
        description="Sve dostupne komande za bot",
        color=discord.Color.blue()
    )
    
    # Schedule commands
    embed.add_field(
        name="📅 RASPORED",
        value=(
            "**!schedule** - Nedeljni raspored streamova\n"
            "**!nextstream** - Kada je sledeći stream\n"
        ),
        inline=False
    )
    
    # Stats commands
    embed.add_field(
        name="📊 STATISTIKA",
        value=(
            "**!stats** - YouTube channel statistika\n"
            "**!live** - Proveri live status\n"
        ),
        inline=False
    )
    
    # User commands
    embed.add_field(
        name="🎮 KORISNIK",
        value=(
            "**!points <username>** - Proveri poene i nivo\n"
            "**!leaderboard [broj]** - Top igrači (max 20)\n"
        ),
        inline=False
    )
    
    # Notification commands
    embed.add_field(
        name="🔔 NOTIFIKACIJE",
        value=(
            "**!notify** - Prijavi se/odjavi za live notifikacije\n"
        ),
        inline=False
    )
    
    embed.set_footer(text="REMZA019 Gaming | Napravljeno sa ❤️")
    await ctx.send(embed=embed)

# ==================== BACKGROUND TASKS ====================

@tasks.loop(minutes=2)
async def check_stream_status():
    """Background task - provera live statusa svakih 2 minuta"""
    global last_stream_status
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/api/live/status") as response:
                if response.status == 200:
                    data = await response.json()
                    is_live = data.get('is_live', False)
                    
                    # Notify when going live
                    if is_live and not last_stream_status:
                        game = data.get('live_game', 'FORTNITE')
                        viewers = data.get('current_viewers', '0')
                        
                        # Broadcast to all guilds
                        for guild in bot.guilds:
                            # Find general or first text channel
                            channel = discord.utils.get(guild.text_channels, name='general')
                            if not channel:
                                channel = guild.text_channels[0] if guild.text_channels else None
                            
                            if channel:
                                embed = discord.Embed(
                                    title="🔴 REMZA019 JE LIVE!",
                                    description=f"🎮 {game}",
                                    color=discord.Color.red()
                                )
                                embed.add_field(name="👥 Viewers", value=viewers, inline=True)
                                embed.add_field(name="📺 Gledaj", value="[YouTube](https://youtube.com/@REMZA019)", inline=True)
                                embed.set_footer(text="🔔 Koristi !notify za personalizovane notifikacije")
                                
                                try:
                                    await channel.send("@everyone", embed=embed)
                                except:
                                    logger.warning(f"Could not send to {guild.name}")
                        
                        # Send DM to notified users
                        for user_id in notified_users:
                            try:
                                user = await bot.fetch_user(user_id)
                                await user.send(embed=embed)
                            except:
                                logger.warning(f"Could not DM user {user_id}")
                        
                        logger.info("✅ Live notification sent!")
                    
                    last_stream_status = is_live
                    
    except Exception as e:
        logger.error(f"Error in stream status check: {e}")

@check_stream_status.before_loop
async def before_check_stream_status():
    await bot.wait_until_ready()

# ==================== BOT RUNNER ====================

def run_discord_bot():
    """Start the Discord bot"""
    if DISCORD_BOT_TOKEN == 'PENDING_USER_INPUT' or not DISCORD_BOT_TOKEN:
        logger.warning("⚠️ DISCORD_BOT_TOKEN not set! Discord bot will not start.")
        logger.warning("To enable Discord bot:")
        logger.warning("1. Create a bot at https://discord.com/developers/applications")
        logger.warning("2. Add DISCORD_BOT_TOKEN to .env file")
        logger.warning("3. Invite bot to your server")
        return
    
    try:
        logger.info("🤖 Starting enhanced Discord bot...")
        bot.run(DISCORD_BOT_TOKEN)
    except Exception as e:
        logger.error(f"❌ Failed to start Discord bot: {e}")

if __name__ == "__main__":
    run_discord_bot()
