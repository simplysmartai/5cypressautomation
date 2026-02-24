# Telegram Bot Setup Guide

Get real-time skill notifications in Telegram in under 2 minutes.

---

## Step 1: Create Your Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Choose a display name (e.g., "5 Cypress Skills Bot")
4. Choose a username (must end in `bot`, e.g., `cypress_skills_bot`)
5. Copy the **bot token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

**Save this token - you'll need it!**

---

## Step 2: Get Your Chat ID

1. Search for **@userinfobot** in Telegram
2. Send `/start` to the bot
3. It will reply with your **Chat ID** (a number like: `987654321`)

**Save this ID - you'll need it!**

---

## Step 3: Start Your Bot

1. Find your bot in Telegram (search for the username you created)
2. Send `/start` to activate it
3. You're now ready to receive notifications!

---

## Step 4: Configure Cloudflare Pages

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Click **Workers & Pages** → **5cypressautomation**
3. Click **Settings** → **Environment variables**
4. Add these two variables:

```
Name: TELEGRAM_BOT_TOKEN
Value: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
(your bot token from Step 1)

Name: TELEGRAM_CHAT_ID  
Value: 987654321
(your chat ID from Step 2)
```

5. Click **Save** and **Redeploy** (or push code to trigger deploy)

---

## Step 5: Test It

1. Go to https://5cypress.com
2. Login with: `demo@5cypress.com`
3. Run any skill (e.g., Email Sequence Builder)
4. Check Telegram - you should receive a notification! ✅

---

## Notification Examples

**Success:**
```
✅ Skill Completed Successfully

Skill: Email Sequence Builder
Client: Demo Client
Duration: 1234ms
Time: 2:30 PM
```

**Failure:**
```
❌ Skill Failed

Skill: Page Cro Analyzer
Client: Demo Client
Duration: 567ms
Time: 2:35 PM

Error: `Failed to fetch URL: Connection timeout`
```

**Usage Alert:**
```
⚠️ WARNING: Usage Alert

Client: Demo Client
Usage: 38/50 (76%)

Client is at 76% of their monthly limit.
```

---

## Troubleshooting

**Not receiving notifications?**
- Make sure you sent `/start` to your bot
- Verify both environment variables are set correctly
- Check Cloudflare deployment logs for errors
- Test the bot token: https://api.telegram.org/bot{YOUR_TOKEN}/getMe

**Getting "unauthorized" errors?**
- Double-check your bot token (no spaces)
- Make sure you copied the full token from @BotFather

**Getting "chat not found" errors?**
- Verify your Chat ID is correct
- Make sure you sent `/start` to the bot first

---

## Advanced: Group Notifications

Want notifications in a Telegram group instead?

1. Create a Telegram group
2. Add your bot to the group
3. Make the bot an admin (required to send messages)
4. Get the group Chat ID:
   - Add **@RawDataBot** to the group
   - Copy the `"id"` value (will be negative, like `-1001234567890`)
5. Update `TELEGRAM_CHAT_ID` in Cloudflare with the group ID

Now all skill notifications go to the group!

---

## Security Notes

- **Never share your bot token** - treat it like a password
- The bot can only send messages to chats that started it
- Cloudflare environment variables are encrypted at rest
- Bot tokens can be regenerated via @BotFather if compromised

---

**Questions?** Check [PHASE_3_COMPLETE.md](PHASE_3_COMPLETE.md) for full platform docs.
