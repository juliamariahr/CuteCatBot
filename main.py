import os
from dotenv import load_dotenv
import discord
from discord.ext import tasks
from flask import Flask
from threading import Thread
import requests
import datetime
import asyncio
from discord import app_commands, Interaction, Embed, ButtonStyle
from discord.ui import View, Button

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
        headers = {'x-api-key': CAT_API_TOKEN}
        res = requests.get("https://api.thecatapi.com/v1/images/search", headers=headers)
        return res.json()[0]['url']
    except Exception as e:
        print(f"Erro ao buscar imagem do gato: {e}")
        return None

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True

class CatBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("Comandos sincronizados!")

bot = CatBot()

@bot.event
async def on_ready():
    print(f"Logado como {bot.user.name}")
    for guild in bot.guilds:
        print(f"- {guild.name} ({guild.id})")
    send_daily_cat_picture.start()

# Comando /miau
@bot.tree.command(name="miau", description="Receba uma imagem fofa de gatinho 🐱")
async def miau_command(interaction: Interaction):
    url = get_cat_image_url()
    if url:
        await interaction.response.send_message(url)
    else:
        await interaction.response.send_message("Não consegui pegar um gatinho agora 😿", ephemeral=True)

# Comando /help
@bot.tree.command(name="help", description="Lista todos os comandos disponíveis do bot")
async def help_command(interaction: Interaction):
    embed = Embed(
        title="🐾 Comandos disponíveis",
        description=(
            "**/miau** — Envia uma imagem fofa de gatinho 🐱\n"
            "**/help** — Mostra essa lista de comandos 📜\n\n"
            "📅 O bot também envia uma imagem por dia às 9h!\n\n"
            "✨ *Novos comandos e atualizações estão chegando em breve!*"
        ),
        color=0xFFC0CB
    )
    embed.set_footer(text="Desenvolvido com amor 💖 por CutecatBot")

    site_button = Button(
        label="🌐 Site Oficial",
        url="https://cute-cat-bot.vercel.app/",
        style=ButtonStyle.link
    )

    view = View()
    view.add_item(site_button)

    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@tasks.loop(time=datetime.time(hour=9, minute=0))
async def send_daily_cat_picture():
    for guild in bot.guilds:
        channel = next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
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
    Thread(target=app.run, kwargs={"host": "0.0.0.0", "port": PORT, "debug": False}).start()
    await bot.start(DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
