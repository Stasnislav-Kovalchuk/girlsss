import folium


_CATEGORY_EMOJI = {
    "Водні резорти / купання": "🏊",
    "Замки / архітектура": "🏰",
    "Прогулянки на природі": "🌿",
    "Вечеря з видом / гастро": "🍷",
    "Парки скульптур / арт": "🎨",
    "природа": "🌿",
    "замок": "🏰",
    "відпочинок": "🏖️",
    "вечеря": "🍷",
}

_CATEGORY_COLORS = ["red", "pink", "purple", "orange", "darkpurple", "cadetblue"]


def category_emoji(place: dict) -> str:
    cat = place.get("category", "")
    for key, emoji in _CATEGORY_EMOJI.items():
        if key in cat:
            return emoji
    return "📍"


def build_map(places: list[dict]) -> folium.Map:
    if not places:
        return folium.Map(location=[49.84, 24.02], zoom_start=9)

    lats = [p["lat"] for p in places]
    lons = [p["lon"] for p in places]
    center = [sum(lats) / len(lats), sum(lons) / len(lons)]

    m = folium.Map(location=center, zoom_start=9, tiles="CartoDB positron")

    coords = []
    for i, place in enumerate(places):
        lat, lon = place["lat"], place["lon"]
        coords.append([lat, lon])

        tags_html = ", ".join(place.get("tags", []))
        popup_html = f"""
        <div style="font-family: Georgia, serif; min-width:200px;">
            <b style="font-size:15px; color:#c0607e;">#{i+1} {place['name']}</b><br>
            <span style="color:#888; font-size:12px;">{place.get('category','').title()}</span><br><br>
            <span style="font-size:13px;">{place['description'][:100]}...</span><br><br>
            <span>🕐 {place.get('time_needed','')}</span><br>
            <span>📍 {place.get('distance_from_lviv',0)} км від Львова</span><br>
            <span style="color:#c0607e; font-size:12px;">🏷 {tags_html}</span>
        </div>
        """

        icon_color = _CATEGORY_COLORS[i % len(_CATEGORY_COLORS)]
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=260),
            tooltip=f"#{i+1} {place['name']}",
            icon=folium.Icon(color=icon_color, icon="heart", prefix="fa"),
        ).add_to(m)

    if len(coords) > 1:
        folium.PolyLine(
            coords,
            color="#e8849a",
            weight=3,
            opacity=0.7,
            dash_array="8 4",
        ).add_to(m)

    return m
