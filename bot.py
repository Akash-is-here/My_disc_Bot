import discord
import os
from dotenv import load_dotenv
from groq import Groq
import asyncio
import aiohttp
from aiohttp import web

# ================== KEEP-ALIVE FOR RENDER (aiohttp - Recommended) ==================
async def ping_handler(request):
    return web.Response(text="✅ AakiGPT Bot is Running 24/7 on Render", status=200)

async def start_keep_alive():
    app = web.Application()
    app.router.add_get('/', ping_handler)      # Root path
    app.router.add_get('/ping', ping_handler)  # Extra path for safety

    port = int(os.getenv("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🔥 Keep-alive server started on port {port} (aiohttp)")
# ================================================================================

load_dotenv()
DISCORD_TOKEN = os.getenv("TOKEN")
GROQ_API_KEY = os.getenv("API")

if not DISCORD_TOKEN:
    raise ValueError("❌ TOKEN not found in environment variables!")
if not GROQ_API_KEY:
    raise ValueError("❌ API not found in environment variables!")

groq_client = Groq(api_key=GROQ_API_KEY)

# Conversation history (per channel)
conversation_history = {}

# Personality / System Prompt
SYSTEM_PROMPT = (
    "You are AakiGPT, a helpful, witty, and friendly AI created by Akash. "
    "You love coding, tech, memes, and helping people. Be engaging, concise, "
    "and fun unless asked for detailed explanations."
)

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'✅ Logged in as {self.user}!')
        print('🤖 AakiGPT is now running 24/7 on Render')

    async def on_message(self, message):
        if message.author == self.user:
            return
        if self.user.mentioned_in(message):
            user_input = message.content.replace(f"<@{self.user.id}>", "")\
                                       .replace(f"<@!{self.user.id}>", "")\
                                       .strip()
            if not user_input:
                await message.channel.send("Yes? How can I help you? 😊")
                return

            channel_id = str(message.channel.id)
            if channel_id not in conversation_history:
                conversation_history[channel_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

            conversation_history[channel_id].append({"role": "user", "content": user_input})

            try:
                thinking_msg = await message.channel.send("Thinking... 🤔")
                async with message.channel.typing():
                    stream = groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=conversation_history[channel_id],
                        temperature=0.84,
                        max_completion_tokens=1491,
                        top_p=0.97,
                        stream=True
                    )

                    response_msg = await message.channel.send("▌")
                    full_response = ""
                    last_edit = asyncio.get_event_loop().time()

                    for chunk in stream:
                        if chunk.choices[0].delta.content is not None:
                            full_response += chunk.choices[0].delta.content
                            if asyncio.get_event_loop().time() - last_edit > 1.0 or len(full_response) > 1800:
                                await response_msg.edit(content=full_response + "▌")
                                last_edit = asyncio.get_event_loop().time()

                    await response_msg.edit(content=full_response)
                    await thinking_msg.delete()

                # Save to history
                conversation_history[channel_id].append({"role": "assistant", "content": full_response})

                # Trim history
                if len(conversation_history[channel_id]) > 22:
                    conversation_history[channel_id] = [conversation_history[channel_id][0]] + conversation_history[channel_id][-21:]

            except Exception as e:
                print(f"Error: {e}")
                await message.channel.send("Sorry, I'm having some trouble right now 😓")

intents = discord.Intents.default()
intents.message_content = True
bot = MyClient(intents=intents)

async def main():
    await start_keep_alive()          # Start the web server first
    await bot.start(DISCORD_TOKEN)    # Then start the bot (use start() instead of run() in async main)

if __name__ == "__main__":
    asyncio.run(main())
