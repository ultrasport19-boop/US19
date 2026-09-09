# -*- coding: utf-8 -*-
"""US19 - genera un video a partir de una foto, con fal.ai.

    python tools/redes/fal_video.py                 <- solo dice que haria
    python tools/redes/fal_video.py --confirmar     <- lo genera y COBRA

ESTO CUESTA DINERO. Por eso sin --confirmar no manda nada: escribe lo que
va a pedir y lo que va a costar, y para. Un descuido no vale USD 0,56.

DE DONDE SALE LA FOTO
De la web publica del gimnasio, que ya sirve las imagenes del repo:
    https://ultrasport19-boop.github.io/US19/img/hero.jpg
Asi no hace falta subir nada a fal. Cualquier archivo de US19/img/ vale
con solo cambiar FOTO.

POR QUE ESA FOTO Y NO OTRA
hero.jpg es la unica con gente entrenando de verdad y la sala entera.
sala-1 y gym-1 estan vacias, y un plano de maquinas quietas da un video
muerto: el modelo no tiene nada que mover.

LA PROPORCION LA DECIDE LA FOTO, NO UN PARAMETRO. hero.jpg es 960x1280
(vertical), asi que el video sale vertical y entra en historia y en Reel
sin recortar. Si algun dia se usa una foto apaisada, saldra apaisada.

EL PROMPT VA EN INGLES a proposito: estos modelos entienden bastante
mejor las instrucciones de movimiento en ingles. Y describe MOVIMIENTO,
no contenido: el contenido ya esta en la foto.

REGLAS DE CONTENIDO, las de siempre: nada clinico, ninguna cifra sin
confirmar, ninguna promesa de resultado. Ver [[us19-nada-de-kinesiologia]].
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

COLA = "https://queue.fal.run"
MODELO = "fal-ai/kling-video/v3/pro/image-to-video"
APP_BASE = "fal-ai/kling-video"     # el estado va al id BASE, no al modelo entero

FOTO = "https://ultrasport19-boop.github.io/US19/img/hero.jpg"
SEGUNDOS = 5
PRECIO_SEGUNDO = 0.112              # USD, Kling v3 Pro sin audio

PROMPT = (
    "Slow cinematic dolly-in, the camera pushes forward very slightly. "
    "The people keep training naturally: the woman in the foreground presses "
    "the dumbbells overhead, the woman on the right pulls the machine handles "
    "down. Warm indoor lighting, wooden ceiling, gentle haze in the light. "
    "Steady camera, one continuous shot, no cuts. "
    "Do not add people, text or logos. Keep the faces stable."
)

SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "salida_video")
NAVEGADOR = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
             "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")


def llamar(url, llave, cuerpo=None):
    cab = {"Authorization": "Key " + llave,
           "Accept": "application/json",
           "User-Agent": NAVEGADOR}
    datos = None
    if cuerpo is not None:
        datos = json.dumps(cuerpo).encode("utf-8")
        cab["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=datos, headers=cab)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8", "replace"))
        except Exception:
            return e.code, {}
    except urllib.error.URLError as e:
        return 0, {"detail": str(e.reason)}


def main():
    llave = (os.environ.get("FAL_KEY") or "").strip()
    if not llave:
        print("NO HAY LLAVE. Correr antes fal_probar.py.")
        return 2

    coste = SEGUNDOS * PRECIO_SEGUNDO
    print("modelo    " + MODELO)
    print("foto      " + FOTO)
    print("duracion  " + str(SEGUNDOS) + " s")
    print("coste     USD %.2f" % coste)
    print("")
    print("prompt:")
    print("  " + PROMPT)
    print("")

    if "--confirmar" not in sys.argv:
        print("ENSAYO. No se mando nada y no se cobro nada.")
        print("Para generarlo de verdad:")
        print("    python tools/redes/fal_video.py --confirmar")
        return 0

    print("encolando...")
    code, d = llamar(COLA + "/" + MODELO, llave, {
        "start_image_url": FOTO,
        "prompt": PROMPT,
        "duration": SEGUNDOS,
        "generate_audio": False,
    })

    if code not in (200, 201, 202):
        detalle = json.dumps(d, ensure_ascii=False)[:400]
        if "TOP_UP" in detalle or "locked" in detalle.lower():
            print("La cuenta esta bloqueada por falta de saldo.")
            print("Cargar en https://fal.ai/dashboard/billing y reintentar.")
            return 3
        print("HTTP " + str(code) + "  " + detalle)
        return 1

    pedido = d.get("request_id")
    if not pedido:
        print("fal no devolvio request_id: " + json.dumps(d)[:300])
        return 1
    print("en cola, id " + pedido)

    estado_url = COLA + "/" + APP_BASE + "/requests/" + pedido + "/status"
    resultado_url = COLA + "/" + APP_BASE + "/requests/" + pedido

    # Kling tarda del orden de minutos. Se pregunta cada 10 s y se corta a
    # los 15 min: si no salio, algo va mal y no vale seguir esperando.
    esperado = 0
    while esperado < 900:
        code, d = llamar(estado_url, llave)
        situacion = d.get("status", "?")
        print("  %4d s  %s" % (esperado, situacion))
        if situacion == "COMPLETED":
            break
        if code >= 400 and situacion == "?":
            print("  el estado dio HTTP " + str(code) + ": " +
                  json.dumps(d)[:200])
            return 1
        time.sleep(10)
        esperado += 10
    else:
        print("Pasaron 15 minutos sin terminar. Se deja ahi.")
        print("El trabajo sigue vivo en fal con el id de arriba.")
        return 1

    code, d = llamar(resultado_url, llave)
    url = ((d.get("video") or {}).get("url")) or ""
    if not url:
        print("Termino pero no vino la url del video: " +
              json.dumps(d, ensure_ascii=False)[:400])
        return 1

    os.makedirs(SALIDA, exist_ok=True)
    destino = os.path.join(SALIDA, "us19_" + time.strftime("%Y%m%d_%H%M") + ".mp4")
    req = urllib.request.Request(url, headers={"User-Agent": NAVEGADOR})
    with urllib.request.urlopen(req, timeout=180) as r, \
            open(destino, "wb") as f:
        f.write(r.read())

    print("")
    print("LISTO: " + destino)
    print("%.1f KB" % (os.path.getsize(destino) / 1024.0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
