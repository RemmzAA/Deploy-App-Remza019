# 🤖 Discord Bot Setup Guide - REMZA019 Gaming

## Current Status
⚠️ **Discord Bot is NOT ACTIVE** - Missing `DISCORD_BOT_TOKEN` in environment

## What's Already Implemented
✅ Discord bot code exists in `/app/backend/discord_bot.py`
✅ Discord link updated to: `https://discord.gg/5W2W23snAM`
✅ Bot commands are defined and ready:
   - `/ping` - Test bot connectivity
   - `/stats` - Show server statistics
   - `/help` - Display available commands

## Why Bot is Not Working
The `DISCORD_BOT_TOKEN` environment variable is **empty** in `/app/backend/.env`

## How to Activate Discord Bot

### Step 1: Get Discord Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application or select existing one
3. Go to "Bot" section
4. Click "Reset Token" or "Copy" to get your bot token
5. **IMPORTANT**: Save this token securely - it's shown only once!

### Step 2: Add Token to Environment
1. Open `/app/backend/.env`
2. Find the line: `DISCORD_BOT_TOKEN=`
3. Add your token: `DISCORD_BOT_TOKEN=your_actual_token_here`
4. Save the file

### Step 3: Restart Backend
```bash
sudo supervisorctl restart backend
```

### Step 4: Verify Bot is Running
Check backend logs:
```bash
tail -f /var/log/supervisor/backend.out.log | grep -i discord
```

You should see: `✅ Discord bot connected as [BotName]`

## Bot Permissions Needed
When inviting bot to your server, it needs these permissions:
- ✅ Send Messages
- ✅ Read Messages/View Channels
- ✅ Embed Links
- ✅ Read Message History

## Discord Bot Features (Once Active)
- 📊 Real-time server statistics
- 🔔 Stream notifications
- 💬 Interactive commands
- 📈 Leaderboard integration
- 🎮 Gaming activity tracking

## Troubleshooting

### Bot Still Not Working?
1. **Check Token Format**: Should be a long alphanumeric string
2. **Verify Bot Permissions**: Ensure bot has necessary permissions in your Discord server
3. **Check Logs**: Look for error messages in backend logs
4. **Bot Invited**: Make sure bot is actually invited to your Discord server

### Common Errors
- `Improper token has been passed` - Invalid or expired token
- `Missing Access` - Bot lacks required permissions
- `Connection failed` - Network or Discord API issues

## Need Help?
Contact support or check:
- Discord Developer Documentation: https://discord.com/developers/docs
- Discord.py Documentation: https://discordpy.readthedocs.io/

---
**Note**: The application works perfectly fine without Discord bot. It's an optional enhancement for community engagement.
