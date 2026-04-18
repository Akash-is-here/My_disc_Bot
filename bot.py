import discord
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

DISCORD_TOKEN = os.getenv("TOKEN")
GROQ_API_KEY = os.getenv("API")

print("✅ Script started")
print(f"TOKEN present: {bool(DISCORD_TOKEN)}")
print(f"GROQ_API present: {bool(GROQ_API_KEY)}")

if not DISCORD_TOKEN:
    raise ValueError("❌ TOKEN missing!")
if not GROQ_API_KEY:
    raise ValueError("❌ API missing!")

print("✅ All env vars loaded successfully")

# Minimal bot just to test login
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ Logged in as {client.user} - Bot is alive!')

client.run(DISCORD_TOKEN)
