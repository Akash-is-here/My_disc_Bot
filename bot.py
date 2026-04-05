
from flask import Flask   # Add this
import threading
import discord
import os
from dotenv import load_dotenv
from groq import Groq

# === Keep-alive web server ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Discord Bot is Running! ✅"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# Start the web server in background
threading.Thread(target=run_flask, daemon=True).start()


load_dotenv()


# Using your exact .env variable names
DISCORD_TOKEN = os.getenv("TOKEN")
GROQ_API_KEY = os.getenv("API")

# Safety check
if not DISCORD_TOKEN:
    raise ValueError("TOKEN not found in .env file!")
if not GROQ_API_KEY:
    raise ValueError("API not found in .env file!")

groq_client = Groq(api_key=GROQ_API_KEY)

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'✅ Logged on as {self.user}!')

    async def on_message(self, message):
        if message.author == self.user:
            return

        # Reply only when the bot is mentioned
        if self.user.mentioned_in(message):
            # Clean the user message (remove mention)
            user_input = message.content.replace(f"<@{self.user.id}>", "").replace(f"<@!{self.user.id}>", "").strip()

            if not user_input:
                await message.channel.send("Yes? How can I help you? 😊")
                return

            try:
                thinking_msg = await message.channel.send("Thinking... 🤔")

                # Groq streaming
                stream = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": user_input}],
                    temperature=0.84,
                    max_completion_tokens=1491,
                    top_p=0.97,
                    stream=True
                )

                response_msg = await message.channel.send("▌")
                full_response = ""

                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        if len(full_response) % 40 == 0 or len(full_response) > 1000:
                            await response_msg.edit(content=full_response + "▌")

                await response_msg.edit(content=full_response)
                await thinking_msg.delete()

            except Exception as e:
                print(f"Error: {e}")
                await message.channel.send("Sorry, I'm having some trouble right now 😓 Please try again.")

intents = discord.Intents.default()
intents.message_content = True

bot = MyClient(intents=intents)
bot.run(DISCORD_TOKEN) 