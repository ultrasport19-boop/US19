# -*- coding: utf-8 -*-
"""US19 - comprueba que la llave de fal.ai esta puesta y sirve.

    python tools/redes/fal_probar.py

NO genera video, asi que NO gasta un peso. fal cobra por segundo de video
producido; esto no llega ni a pedir uno.

COMO SE COMPRUEBA, Y POR QUE ASI
Se hace un GET al endpoint del modelo. Ese endpoint solo acepta POST, asi
que nunca va a generar nada; pero fal revisa la cuenta ANTES de mirar el
metodo, y en esa respuesta se ve todo:

    401 / «Unauthorized»          la llave esta mal
    403 / «User is locked ... TOP_UP»  la llave SIRVE, falta cargar saldo
    otra cosa                     la llave sirve y la cuenta esta operativa

LO QUE NO SIRVE PARA COMPROBAR (probado el 9-sep-2026)
Preguntar por el estado de un trabajo inventado devuelve 404 con llave y
SIN llave: ese endpoint no autentica los ids desconocidos, asi que su 404
no prueba nada. Fue el primer intento y era un falso positivo.

Y ojo con la forma de esa URL, que no es la que uno supone: el estado va
al id BASE de la aplicacion, no a la ruta completa del modelo.
    bien   /fal-ai/kling-video/requests/{id}/status
    mal    /fal-ai/kling-video/v3/pro/image-to-video/requests/{id}/status  -> 405

LA LLAVE NO SE ESCRIBE EN NINGUN CHAT
Se lee de FAL_KEY, la variable que usa el propio fal. Se pone una vez:

    setx FAL_KEY "LA_LLAVE_COMPLETA"

y se abre una terminal nueva. Este script nunca imprime el valor.

LA TRAMPA HEREDADA DE HIGGSFIELD
Sin User-Agent de navegador, Cloudflare corta a Python con 403 y el error
1010 «browser_signature_banned», que parece llave mala y no lo es.

DATOS DE LA API (fal.ai/docs, consultados el 9-sep-2026)
  cola            https://queue.fal.run
  sincrono        https://fal.run
  autenticacion   cabecera  Authorization: Key <llave>   (UNA sola)
  encolar         POST /{modelo}
  estado          GET  /{app-base}/requests/{id}/status
  resultado       GET  /{app-base}/requests/{id}
  cobro           por segundo de video. Kling v3 Pro imagen-a-video:
                  USD 0,112/s sin audio, de 3 a 15 s, 5 por defecto.
                  La proporcion la decide la foto de partida, no un
                  parametro: foto vertical -> video vertical.
"""
import os
import sys
import urllib.error
import urllib.request

MODELO = "fal-ai/kling-video/v3/pro/image-to-video"
SINCRONO = "https://fal.run/" + MODELO

NAVEGADOR = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
             "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")


def main():
    llave = (os.environ.get("FAL_KEY") or "").strip()

    if not llave:
        print("NO HAY LLAVE.")
        print("")
        print("  Se crea en https://fal.ai/dashboard/keys")
        print("  Despues, en la terminal de Diego y una sola vez:")
        print("")
        print('      setx FAL_KEY "LA_LLAVE_COMPLETA"')
        print("")
        print("  Y abrir una terminal nueva: setx no cambia la que ya")
        print("  esta abierta. No pegar la llave en el chat.")
        return 2

    print("llave encontrada  ->  " + str(len(llave)) + " caracteres")
    if " " in llave:
        print("  OJO: lleva espacios. Casi seguro se colaron al pegarla.")

    pedido = urllib.request.Request(SINCRONO, headers={
        "Authorization": "Key " + llave,
        "Accept": "application/json",
        "User-Agent": NAVEGADOR})

    try:
        with urllib.request.urlopen(pedido, timeout=25) as r:
            print("HTTP " + str(r.status) + " - la llave sirve")
            return 0
    except urllib.error.HTTPError as e:
        cuerpo = ""
        try:
            cuerpo = e.read().decode("utf-8", "replace")[:300]
        except Exception:
            pass
        plano = cuerpo.replace("\n", " ")

        if "1010" in cuerpo or "browser_signature" in cuerpo:
            print("HTTP " + str(e.code) + " - TE CORTO CLOUDFLARE, NO FAL.")
            print("  No es la llave: falta el User-Agent de navegador.")
            return 1

        if "TOP_UP" in cuerpo or "locked" in cuerpo.lower():
            print("HTTP " + str(e.code) + " - LA LLAVE SIRVE, PERO FALTA SALDO.")
            print("  fal reconocio la cuenta y la tiene bloqueada hasta que")
            print("  cargues fondos, en https://fal.ai/dashboard/billing")
            print("  Referencia: un video de 5 s con Kling v3 Pro son")
            print("  USD 0,56, asi que con poco alcanza para probar.")
            print("  dice: " + plano)
            return 3

        if e.code == 401 or "unauthor" in cuerpo.lower():
            print("HTTP " + str(e.code) + " - LA LLAVE NO SIRVE.")
            print("  Vuelve a copiarla entera de fal.ai/dashboard/keys.")
            print("  dice: " + plano)
            return 1

        # 405 y compania: el endpoint pide POST. Que conteste eso en vez de
        # un error de cuenta significa que la cuenta esta bien.
        print("HTTP " + str(e.code) + " - la llave sirve y la cuenta responde.")
        if plano:
            print("  dice: " + plano)
        return 0

    except urllib.error.URLError as e:
        print("NO SE PUDO LLEGAR A FAL: " + str(e.reason))
        print("  Es red, no la llave.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
