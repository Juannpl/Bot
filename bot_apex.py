import os
import re
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

APEX_BOT_ID = 918928120923435008
GUILD_ID = 739847426306867241

pending_requests = {}


@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")

@bot.event
async def on_interaction(interaction):
    # On ne prend que les slash commands
    if not interaction.type == discord.InteractionType.application_command:
        return

    # On ne prend que la commande stats
    if interaction.data["name"] != "stats":
        return

    # Stocker l'utilisateur qui a lancé la commande
    pending_requests[interaction.channel_id] = interaction.user.id
    print(f"📌 Commande /stats par {interaction.user}")



@bot.event
async def on_message_edit(before, after):

    if after.author.id != APEX_BOT_ID:
        return

    if not after.embeds:
        return

    embed = after.embeds[0]

    if not embed.title:
        return

    match = re.search(r"([\w\d_]+)'s statistics", embed.title)
    if not match:
        return

    apex_name = match.group(1)
    print(f"🎯 Pseudo Apex détecté : {apex_name}")

    user_id = pending_requests.get(after.channel.id)

    if not user_id:
        print("⚠️ Aucun utilisateur lié à cette commande.")
        return

    guild = bot.get_guild(GUILD_ID)
    member = guild.get_member(user_id)

    if not member:
        print("❌ Impossible de trouver le membre.")
        return

    try:
        await member.edit(nick=apex_name)
        print(f"✅ {member} renommé en {apex_name}")

        del pending_requests[after.channel.id]

    except discord.Forbidden:
        print("❌ Permission refusée : rôle trop bas.")

    except Exception as e:
        print(f"❌ Erreur : {e}")


bot.run(TOKEN)