# -*- coding: utf-8 -*-
"""US19 - comprueba que la llave de Higgsfield esta puesta y sirve.

    python tools/redes/higgsfield_probar.py

QUE HACE Y QUE NO
Pregunta por el estado de una peticion que no existe. La respuesta dice
todo lo que hace falta saber sin generar nada:

    401  la llave falta o esta mal      -> no sirve
    404  la peticion no existe          -> LA LLAVE SIRVE
    200  existia de verdad (imposible)  -> tambien sirve

NO genera imagenes ni videos, asi que NO gasta creditos. Higgsfield cobra
por generacion correcta; las fallidas, las moderadas y las canceladas se
devuelven solas. Este chequeo no llega ni a pedir una.

LA LLAVE NO SE ESCRIBE AQUI NI EN NINGUN CHAT
Se lee de la variable de entorno HF_KEY, que es la que usa el SDK oficial
y tiene la forma "id:secreto". Se pone una sola vez, desde la terminal de
Diego:

    setx HF_KEY "TU_ID:TU_SECRETO"

y se abre una terminal nueva, porque setx no toca la que ya esta abierta.
Este script nunca imprime el valor: solo cuantos caracteres mide cada
mitad, que es suficiente para ver si quedo cortada o pegada con espacios.

DOS TRAMPAS QUE COSTARON UNA HORA (9-sep-2026)

1. CLOUDFLARE BLOQUEA A PYTHON POR EL USER-AGENT. Sin cabecera propia,
   urllib se presenta como "Python-urllib/3.14" y Cloudflare responde
   403 con error 1010, "browser_signature_banned". Eso NO es la llave:
   la peticion no llega siquiera a Higgsfield. Por eso aqui se manda un
   User-Agent de navegador. Un 403 con "error_code":1010 en el cuerpo
   siempre es esto, nunca las credenciales.

2. EL ID ES UN UUID DE 36 CARACTERES Y SE COPIA CORTADO. La primera
   llave de Diego llego con 35: le faltaba un caracter del ultimo grupo.
   La API contestaba "Invalid credentials", que manda a rehacer la llave
   cuando lo unico que hacia falta era volver a copiarla. Por eso se
   comprueba la forma del UUID ANTES de salir a la red.

DATOS DE LA API (docs.higgsfield.ai, consultados el 9-sep-2026)
  base            https://api.higgsfield.ai
  autenticacion   cabecera  Authorization: Key <id>:<secreto>
  estado          GET /requests/{id}/status
  asincrono       se pide, se recibe un status_url y se consulta hasta
                  que termina; tambien admite webhook
  retencion       los archivos de salida duran al menos 7 dias: hay que
                  bajarlos, no enlazarlos
"""
import os
import re
import sys
import urllib.error
import urllib.request

BASE = "https://api.higgsfield.ai"
# Un identificador con la forma correcta pero que no puede existir.
PETICION_FALSA = "00000000-0000-4000-8000-000000000000"

# Sin esto, Cloudflare corta la peticion antes de que Higgsfield la vea.
NAVEGADOR = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
             "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")

UUID = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}"
                  r"-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


def leer_llave():
    """HF_KEY entera, o las dos mitades por separado. Devuelve (id, secreto).

    La documentacion de Higgsfield usa TRES nombres distintos segun la
    pagina: la guia del SDK dice HF_KEY ("id:secreto"), el quickstart dice
    HF_API_KEY_ID / HF_API_KEY_SECRET y el README del cliente dice
    HF_API_KEY / HF_API_SECRET. Se aceptan los tres para que Diego no
    tenga que adivinar cual copiar.
    """
    entera = (os.environ.get("HF_KEY") or "").strip()
    if entera:
        if entera.count(":") != 1:
            return None, None
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
        print("NO HAY LLAVE.")
        print("")
        print("  Se crea en https://cloud.higgsfield.ai y son dos partes.")
        print("  Despues, en la terminal de Diego y una sola vez:")
        print("")
        print('      setx HF_KEY "TU_ID:TU_SECRETO"')
        print("")
        print("  Y abrir una terminal nueva: setx no cambia la que ya esta")
        print("  abierta. No pegar la llave en el chat.")
        return 2

    # Nunca el valor: solo el tamano, que basta para ver si quedo cortada.
    print("llave encontrada  ->  id de " + str(len(ident)) +
          " caracteres, secreto de " + str(len(secreto)))

    # Antes de salir a la red: el id tiene que ser un UUID entero. Si se
    # copio cortado, la API dice «Invalid credentials» y uno se pone a
    # rehacer la llave sin necesidad. Paso justo eso el 9-sep-2026.
    if not UUID.match(ident):
        print("")
        print("EL ID ESTA MAL COPIADO.")
        print("  Tiene que ser un UUID de 36 caracteres con la forma")
        print("  8-4-4-4-12, y este mide " + str(len(ident)) + ".")
        print("  Vuelve a copiarlo entero de cloud.higgsfield.ai; casi")
        print("  siempre es que la seleccion se comio el ultimo caracter.")
        return 1

    pedido = urllib.request.Request(
        BASE + "/requests/" + PETICION_FALSA + "/status",
        headers={"Authorization": "Key " + ident + ":" + secreto,
                 "Accept": "application/json",
                 "User-Agent": NAVEGADOR})

    try:
        with urllib.request.urlopen(pedido, timeout=20) as r:
            print("HTTP " + str(r.status) + " - la llave sirve")
            return 0
    except urllib.error.HTTPError as e:
        cuerpo = ""
        try:
            cuerpo = e.read().decode("utf-8", "replace")[:200]
        except Exception:
            pass

        if e.code == 404:
            print("HTTP 404 - LA LLAVE SIRVE.")
            print("  (404 es la respuesta correcta: la peticion que le")
            print("   preguntamos no existe, pero nos dejo preguntar.)")
            return 0
        if "1010" in cuerpo or "browser_signature" in cuerpo:
            print("HTTP " + str(e.code) + " - TE CORTO CLOUDFLARE, NO HIGGSFIELD.")
            print("  Error 1010: la peticion no llego a la API. Es el")
            print("  User-Agent, no la llave. Si sale esto es que alguien")
            print("  quito la cabecera NAVEGADOR de este archivo.")
            return 1
        if e.code in (401, 403):
            print("HTTP " + str(e.code) + " - LA LLAVE NO SIRVE.")
            print("  El id tiene forma de UUID, asi que o el secreto esta")
            print("  cortado o la llave se borro en cloud.higgsfield.ai.")
            print("  Vuelve a copiar las DOS partes enteras.")
            return 1
        print("HTTP " + str(e.code) + " - respuesta inesperada")
        if cuerpo:
            print("  " + cuerpo)
        return 1
    except urllib.error.URLError as e:
        print("NO SE PUDO LLEGAR A LA API: " + str(e.reason))
        print("  Es red, no la llave.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
