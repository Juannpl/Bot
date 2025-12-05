# apex_utils.py

def get_most_played_legend(legends_data: dict):
    """
    Analyse les stats de toutes les légendes et retourne :
    {
        "name": <nom>,
        "kills": <kills>,
        "icon": <url>
    }
    """

    best_legend = None
    best_kills = -1
    best_icon = None

    for legend_name, legend_info in legends_data.items():
        # Skip "Global"
        if legend_name.lower() == "global":
            continue

        data_list = legend_info.get("data")
        if not data_list:
            # Aucune data → skip
            continue

        # Cherche l’entrée "BR Kills"
        for stat in data_list:
            if stat.get("key") == "kills":  # on prend UNIQUEMENT kills normal
                kills = stat.get("value", 0)

                if kills > best_kills:
                    best_kills = kills
                    best_legend = legend_name
                    best_icon = legend_info.get("ImgAssets", {}).get("icon")

                break  # on ne regarde pas le reste

    if best_legend is None or best_kills <= 0:
        return None

    return {
        "name": best_legend,
        "kills": best_kills,
        "icon": best_icon
    }
