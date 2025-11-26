import os
import discord
import aiohttp
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
API_KEY = os.getenv("APEX_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

PLATFORMS = {"PC": "PC", "Playstation": "PS4", "Xbox": "X1"}

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")
    try:
        await tree.sync(guild=discord.Object(id=GUILD_ID))
        print("✅ Commands synced to guild")
    except Exception:
        await tree.sync()
        print("✅ Commands synced globally")

@tree.command(
    name="renameapex",
    description="Récupère le pseudo Apex, renomme et affiche les stats",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.choices(platform=[
    app_commands.Choice(name="PC", value="PC"),
    app_commands.Choice(name="Playstation", value="PS4"),
    app_commands.Choice(name="Xbox", value="X1")
])
@app_commands.describe(player_name="Pseudo Apex à rechercher", platform="Plateforme du joueur")
async def renameapex(interaction: discord.Interaction, platform: app_commands.Choice[str], player_name: str):
    await interaction.response.defer(ephemeral=True)
    platform_val = platform.value
    print(f"📌 Commande lancée par {interaction.user} | Player: {player_name} | Platform: {platform_val}")

    url = f"https://api.mozambiquehe.re/bridge?platform={platform_val}&player={player_name}&auth={API_KEY}"
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(url) as r:
                if r.status != 200:
                    await interaction.followup.send("Erreur HTTP de l'API.", ephemeral=True)
                    print(f"❌ HTTP {r.status} pour {player_name} sur {platform_val}")
                    return
                data = await r.json()
    except Exception as e:
        await interaction.followup.send(f"Erreur réseau: {e}", ephemeral=True)
        print(f"❌ Erreur réseau pour {player_name} : {e}")
        return

    try:
        global_stats = data["global"]
        apex_real_name = global_stats["name"]
        level = global_stats.get("level", "N/A")
        rank = global_stats.get("rank", {}).get("rankName", "N/A")
        kills = global_stats.get("kills", "N/A")
        realtime = data.get("realtime")
        legend_name = "N/A"
        if isinstance(realtime, dict):
            selected_legend = realtime.get("selectedLegend")
            if isinstance(selected_legend, dict):
                legend_name = selected_legend.get("LegendName", "N/A")

        embed = discord.Embed(
            title=f"{apex_real_name}'s statistics",
            color=discord.Color.blue()
        )
        embed.add_field(name="Level", value=level, inline=True)
        embed.add_field(name="Rank", value=rank, inline=True)
        embed.add_field(name="Kills", value=kills, inline=True)
        embed.add_field(name="Current Legend", value=legend_name, inline=True)
        embed.set_footer(text=f"Requested by {interaction.user}")
        await interaction.followup.send(embed=embed, ephemeral=True)

        print(f"🎯 Embed stats envoyé pour {apex_real_name}")

    except KeyError:
        await interaction.followup.send("Impossible de récupérer le pseudo Apex.", ephemeral=True)
        print(f"⚠️ Pas de pseudo Apex trouvé pour {player_name}")
        return

    # Renommer le membre
    try:
        member_obj = interaction.guild.get_member(interaction.user.id) or await interaction.guild.fetch_member(interaction.user.id)
        await member_obj.edit(nick=apex_real_name)
        print(f"🔧 Renommage de {member_obj} en {apex_real_name}")
    except discord.Forbidden:
        print(f"❌ Permission refusée pour {interaction.user}")
    except Exception as e:
        print(f"❌ Erreur lors du renommage pour {interaction.user} : {e}")

bot.run(TOKEN)
