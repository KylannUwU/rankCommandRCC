@app.route("/rango")
def obtener_rango():
    query = request.args.get("game", "").strip()
    datos, _ = leer_rangos_github()
    rangos = datos.get("rangos", {})
    emotes = datos.get("emotes", {})
    alias_map = datos.get("alias", {})

    def agregar_emote(juego, rango):
        if rango == "API_VALORANT":
            return "$(customapi https://splendid-groovy-feverfew.glitch.me/valorant/ap/Nolley/manrr?onlyRank=true)"
        emote = emotes.get(juego.lower(), "")
        return f"{rango} {emote}" if emote else rango

    query_lower = query.lower()

    # Buscar en alias
    for alias, juego_real in alias_map.items():
        if alias.lower() in query_lower:
            rango = rangos.get(juego_real)
            if rango:
                return f"El rango de noli en {juego_real} ➜ {agregar_emote(juego_real, rango)} nolleySip"

    # Buscar nombre exacto del juego
    for juego, rango in rangos.items():
        if juego.lower() in query_lower:
            return f"El rango de noli en {juego} ➜ {agregar_emote(juego, rango)} nolleySip"

    # Si nada coincide, mostrar todos
    respuesta = [
        f"{j} ➜ {agregar_emote(j, r)}"
        for j, r in rangos.items()
    ]
    return " | ".join(respuesta)
