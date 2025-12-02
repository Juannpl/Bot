import os
import discord
import aiohttp
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from apex_utils import get_most_played_legend

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
    name="statapex",
    description="Récupère le pseudo Apex, renomme et affiche les stats",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.choices(platform=[
    app_commands.Choice(name="PC", value="PC"),
    app_commands.Choice(name="Playstation", value="PS4"),
    app_commands.Choice(name="Xbox", value="X1")
])
@app_commands.describe(player_name="Pseudo Apex à rechercher", platform="Plateforme du joueur")
async def statapex(interaction: discord.Interaction, platform: app_commands.Choice[str], player_name: str):
    await interaction.response.defer(ephemeral=True)
    platform_val = platform.value

    print(
        f"📌 Commande lancée par {interaction.user} | Player: {player_name} | Platform: {platform_val}")

    url = f"https://api.mozambiquehe.re/bridge?platform={platform_val}&player={player_name}&auth={API_KEY}"

    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(url) as r:
                if r.status != 200:
                    await interaction.followup.send("Erreur HTTP de l'API.", ephemeral=True)
                    return
                data = await r.json()

    except Exception as e:
        await interaction.followup.send(f"Erreur réseau: {e}", ephemeral=True)
        return

    try:
        global_stats = data["global"]
        total_stats = data.get("total", {})

        apex_real_name = global_stats["name"]
        level = global_stats.get("level", "N/A")
        # Récupérer la légende la plus jouée
        legends_data = data.get("legends", {}).get("all", {})
        main_legend = get_most_played_legend(legends_data)

        # Rank data
        rank_data = global_stats.get("rank", {})
        rank_name = rank_data.get("rankName", "N/A")
        rank_div = rank_data.get("rankDiv", "N/A")
        rank_score = rank_data.get("rankScore", "N/A")
        rank_img = rank_data.get("rankImg", None)

        # ALS data
        als_top_percent = rank_data.get("ALStopPercent", "N/A")
        als_top_int = rank_data.get("ALStopInt", "N/A")
        als_top_percent_global = rank_data.get("ALStopPercentGlobal", "N/A")
        als_top_int_global = rank_data.get("ALStopIntGlobal", "N/A")
        als_flag = rank_data.get("ALSFlag", False)

        als_status_emoji = "🟩 Données fiables" if als_flag else "🟧 Données estimées (moins fiables)"

        # Total account kills & damage
        total_kills = f"{total_stats.get('kills', {}).get('value'):,}" if total_stats.get(
            'kills') else "N/A"
        total_damage = f"{total_stats.get('damage', {}).get('value'):,}" if total_stats.get(
            'damage') else "N/A"

        # Realtime info
        realtime = data.get("realtime", {})
        legend_name = realtime.get("selectedLegend", "N/A")

        # ----- EMBED -----
        embed = discord.Embed(
            title=f"{apex_real_name}'s statistics",
            color=discord.Color.blue()
        )

        if rank_img:
            embed.set_thumbnail(url=rank_img)

        embed.add_field(name="Level", value=level, inline=True)
        embed.add_field(
            name="Rank", value=f"{rank_name} {rank_div}", inline=True)
        embed.add_field(name="Rank Score (RP)", value=rank_score, inline=True)

        # --- MAIN LEGEND ---
        if main_legend:
            embed.add_field(
                name="Main Legend",
                value=f"**{main_legend['name']}**\nKills : **{main_legend['kills']}**",
                inline=False
            )
            if main_legend.get("icon"):
                embed.set_image(url=main_legend["icon"])
        else:
            embed.add_field(name="Main Legend",
                            value="Aucune donnée disponible", inline=False)

        embed.add_field(name="Current Legend", value=legend_name, inline=True)

        # ----- TOTAL ACCOUNT STATS -----
        embed.add_field(
            name="📊 Account Totals",
            value=f"**Total Kills:** {total_kills}\n**Total Damage:** {total_damage}",
            inline=False
        )

        # ----- ALS section -----
        embed.add_field(name="ALS Status",
                        value=als_status_emoji, inline=False)

        embed.add_field(
            name="Platform Rank (ALS)",
            value=f"Top **{als_top_percent}%**\nApprox. **#{als_top_int}**",
            inline=True
        )

        embed.add_field(
            name="Global Rank (ALS)",
            value=f"Top **{als_top_percent_global}%**\nApprox. **#{als_top_int_global}**",
            inline=True
        )

        embed.set_footer(text=f"Requested by {interaction.user}")

        await interaction.followup.send(embed=embed, ephemeral=True)
        print(f"🎯 Embed envoyé pour {apex_real_name}")

    except KeyError:
        await interaction.followup.send("Impossible de récupérer le pseudo Apex.", ephemeral=True)
        return

    # ----- Renommage -----
    try:
        member_obj = interaction.guild.get_member(interaction.user.id) or await interaction.guild.fetch_member(interaction.user.id)
        await member_obj.edit(nick=apex_real_name)
        print(f"🔧 Renommage : {member_obj} → {apex_real_name}")
    except:
        pass


bot.run(TOKEN)
