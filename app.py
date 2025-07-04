from flask import Flask, request
from github import Github
import json
import os
import requests

app = Flask(__name__)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
SECRET_TOKEN = os.getenv("KEYTW")

REPO_NAME = "KylannUwU/rankCommandRCC"
BRANCH = "main"
FILE_PATH = "rangos.json"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

def leer_rangos_github():
    try:
        contenido = repo.get_contents(FILE_PATH, ref=BRANCH)
        datos = json.loads(contenido.decoded_content.decode())
        return datos, contenido.sha
    except Exception as e:
        print(f"Error leyendo rangos: {e}")
        return {}, None

def guardar_rangos_github(datos, sha, mensaje="Actualización de rangos"):
    contenido_nuevo = json.dumps(datos, ensure_ascii=False, indent=2)
    try:
        if sha:
            repo.update_file(FILE_PATH, mensaje, contenido_nuevo, sha, branch=BRANCH)
        else:
            repo.create_file(FILE_PATH, mensaje, contenido_nuevo, branch=BRANCH)
        return True
    except Exception as e:
        print(f"Error guardando rangos: {e}")
        return False

@app.route("/")
def home():
    return "API Rangos con commits a GitHub activa."

@app.route("/rango")
def obtener_rango():
    query = request.args.get("game", "").strip()
    datos, _ = leer_rangos_github()
    rangos = datos.get("rangos", {})
    emotes = datos.get("emotes", {})
    alias_map = datos.get("alias", {})

    def agregar_emote(juego, rango):
        emote = emotes.get(juego.lower(), "")
        return f"{rango} {emote}" if emote else rango

    def obtener_contenido_externo(rango):
        if rango.startswith("http://") or rango.startswith("https://"):
            try:
                r = requests.get(rango)
                if r.ok:
                    return r.text.strip()
                else:
                    return "❌ Error al obtener el rango externo."
            except Exception as e:
                return f"❌ Error externo: {e}"
        return rango

    query_lower = query.lower()

    # Buscar alias
    for alias, juego_real in alias_map.items():
        if alias.lower() in query_lower:
            rango_raw = rangos.get(juego_real)
            if rango_raw:
                rango_final = obtener_contenido_externo(rango_raw)
                return f"El rango de noli en {juego_real} ➜ {agregar_emote(juego_real, rango_final)}"

    # Buscar nombre del juego directamente
    for juego, rango_raw in rangos.items():
        if juego.lower() in query_lower:
            rango_final = obtener_contenido_externo(rango_raw)
            return f"El rango de noli en {juego} ➜ {agregar_emote(juego, rango_final)}"

    # Si nada coincide, mostrar todos
    respuesta = [
        f"{j} ➜ {agregar_emote(j, obtener_contenido_externo(r))}"
        for j, r in rangos.items()
    ]
    return " | ".join(respuesta)




@app.route("/setrango", methods=["GET", "POST"])
def set_rango():
    token = request.args.get("token")
    data = request.args.get("data", "")

    if token != SECRET_TOKEN:
        return "No autorizado."

    if "," not in data:
        return "nolleyRage Formato incorrecto, usa: Juego, Rango"

    juego_input, nuevo_rango = [x.strip() for x in data.split(",", 1)]

    if not juego_input or not nuevo_rango:
        return "nolleyRage Datos faltantes, usa: Juego, Rango"

    datos, sha = leer_rangos_github()
    rangos = datos.get("rangos", {})

    # Buscar juego en rangos ignorando mayúsculas/minúsculas
    juego_clave = None
    for clave in rangos.keys():
        if clave.lower() == juego_input.lower():
            juego_clave = clave
            break

    if juego_clave:
        # Actualizar rango en la clave encontrada
        datos["rangos"][juego_clave] = nuevo_rango
    else:
        # Si no existe, agregar con el nombre tal cual lo escribió el usuario
        if "rangos" not in datos:
            datos["rangos"] = {}
        datos["rangos"][juego_input] = nuevo_rango

    exito = guardar_rangos_github(datos, sha, mensaje=f"Actualización rango {juego_input}")

    if exito:
        return f"nolleyClap Rango de {juego_input} actualizado a: {nuevo_rango}"
    else:
        return "Error actualizando rangos nephuLost."


@app.route("/addrango", methods=["GET", "POST"])
def add_rango():
    token = request.args.get("token")
    data = request.args.get("data", "")

    if token != SECRET_TOKEN:
        return "No autorizado."

    partes = [x.strip() for x in data.split(",", 2)]
    if len(partes) != 3:
        return "nolleyRage Formato incorrecto. Usa: juego, rango, emote"

    juego, nuevo_rango, nuevo_emote = partes

    if not juego or not nuevo_rango or not nuevo_emote:
        return "nolleyRage Faltan datos. Asegúrate de escribir: juego, rango, emote"

    datos, sha = leer_rangos_github()
    if "rangos" not in datos:
        datos["rangos"] = {}
    if "emotes" not in datos:
        datos["emotes"] = {}

    # Añade juego + rango
    datos["rangos"][juego] = nuevo_rango
    # Añade o actualiza emote
    datos["emotes"][juego.lower()] = nuevo_emote

    exito = guardar_rangos_github(datos, sha, mensaje=f"Agregado rango y emote para {juego}")

    if exito:
        return f"nolleyClap Juego {juego} y rango añadidos."
    else:
        return "Error guardando el juego nolleyPipipipi."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)


