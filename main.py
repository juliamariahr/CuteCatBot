import os
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
from flask import Flask
from threading import Thread
import requests
import datetime
import asyncio

load_dotenv()
CAT_API_TOKEN = os.getenv("CAT_API_TOKEN")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
PORT = int(os.getenv("PORT", 3000))

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot online!"

def get_cat_image_url():
    try:
        headers = {
            'x-api-key': CAT_API_TOKEN
        }
        res = requests.get("https://api.thecatapi.com/v1/images/search", headers=headers)
        return res.json()[0]['url']
    except Exception as e:
        print(f"Erro ao buscar imagem do gato: {e}")
        return None

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logado como {bot.user.name}")
    for guild in bot.guilds:
        print(f"- {guild.name} ({guild.id})")
    send_daily_cat_picture.start()

@bot.command()
async def miau(ctx):
    url = get_cat_image_url()
    if url:
        await ctx.send(url)
    else:
        await ctx.send("Não consegui pegar um gatinho agora 😿")


@tasks.loop(time=datetime.time(hour=9, minute=0))
async def send_daily_cat_picture():
    for guild in bot.guilds:
        channel = next(
            (c for c in guild.text_channels if c.permissions_for(guild.me).send_messages),
            None
        )
        if channel:
            try:
                url = get_cat_image_url()
                if url:
                    await channel.send("🐱 Dose diária de fofura:")
                    await channel.send(url)
                else:
                    await channel.send("Não consegui pegar um gato hoje 😿")
            except Exception as e:
                print(f"Erro ao enviar para {channel.name} em {guild.name}: {e}")
        else:
            print(f"Nenhum canal acessível em {guild.name}")


async def main():
    Thread(target=app.run, kwargs={
        "host": "0.0.0.0",
        "port": PORT,
        "debug": False
    }).start()
    await bot.start(DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
