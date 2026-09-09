# -*- coding: utf-8 -*-
"""US19 - que modelos tiene disponibles la cuenta de Higgsfield.

    python tools/redes/higgsfield_modelos.py

Solo LEE la lista. No genera nada, asi que NO gasta creditos.

PARA QUE SIRVE
La documentacion de Higgsfield no publica los identificadores de los
modelos: los que tiene cada cuenta dependen del plan. Este script pregunta
por ellos y separa los de video de los de imagen, que es la diferencia que
importa aqui.

EL 9-sep-2026 la cuenta de Diego tenia TRES modelos y los tres de imagen:
soul/cinema, soul/v2/standard y soul-id. Filtrando por video la API
devolvia total=0. O sea que la llave funciona pero la cuenta todavia no
puede generar video; eso se arregla en Higgsfield, no aqui.

LAS DOS TRAMPAS, las mismas que en higgsfield_probar.py:
  · sin User-Agent de navegador, Cloudflare corta con error 1010
  · el key ID es un UUID de 36 caracteres y se copia cortado
"""
import json
import os
import sys
import urllib.error
import urllib.request

BASE = "https://api.higgsfield.ai"
NAVEGADOR = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
             "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")


def leer_llave():
    entera = (os.environ.get("HF_KEY") or "").strip()
    if entera and entera.count(":") == 1:
        ident, secreto = entera.split(":", 1)
        return ident.strip(), secreto.strip()
    for nid, nsec in (("HF_API_KEY_ID", "HF_API_KEY_SECRET"),
                      ("HF_API_KEY", "HF_API_SECRET")):
        ident = (os.environ.get(nid) or "").strip()
        secreto = (os.environ.get(nsec) or "").strip()
        if ident and secreto:
            return ident, secreto
    return "", ""


def main():
    ident, secreto = leer_llave()
    if not ident or not secreto:
        print("NO HAY LLAVE. Correr antes higgsfield_probar.py.")
        return 2

    pedido = urllib.request.Request(
        BASE + "/models?limit=100",
        headers={"Authorization": "Key " + ident + ":" + secreto,
                 "Accept": "application/json",
                 "User-Agent": NAVEGADOR})
    try:
        with urllib.request.urlopen(pedido, timeout=25) as r:
            datos = json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        cuerpo = ""
        try:
            cuerpo = e.read().decode("utf-8", "replace")[:200]
        except Exception:
            pass
        if "1010" in cuerpo:
            print("Te corto Cloudflare, no Higgsfield. Falta el User-Agent.")
        else:
            print("HTTP " + str(e.code) + "  " + cuerpo)
        return 1
    except urllib.error.URLError as e:
        print("Sin red: " + str(e.reason))
        return 1

    items = datos.get("items", [])
    print("La cuenta tiene " + str(datos.get("total", len(items))) + " modelos.")
    print("")

    videos, imagenes = [], []
    for m in items:
        (videos if m.get("output_type") == "video" else imagenes).append(m)

    def pintar(titulo, lista):
        print(titulo + " (" + str(len(lista)) + ")")
        if not lista:
            print("   -- ninguno --")
        for m in lista:
            print("   %-34s %s" % (m.get("slug", "?"), m.get("title", "")))
            print("      para: %s   cuesta: %s creditos" % (
                ", ".join(m.get("operation_type") or ["?"]),
                m.get("base_credits", "?")))
        print("")

    pintar("VIDEO", videos)
    pintar("IMAGEN", imagenes)

    if not videos:
        print("No hay ningun modelo de video en esta cuenta.")
        print("La llave funciona: lo que falta es el plan o el acceso, y")
        print("eso se resuelve en cloud.higgsfield.ai, no en este codigo.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
