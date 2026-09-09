# -*- coding: utf-8 -*-
"""US19 - monta un video promocional sobre una grabacion real de la sala.

    python tools/redes/video_promo.py <video.mp4>

QUE HACE
Escala a 1080x1920 (historia y Reel), le pone encima los rotulos de la
marca en tres tiempos y guarda el mp4 en salida_video/. La musica NO se
pone aqui: se conserva el audio original.

POR QUE LOS ROTULOS SE DIBUJAN CON PILLOW Y NO CON drawtext
El filtro drawtext de ffmpeg obliga a escapar las rutas de Windows (los
dos puntos de «C:») y se come los acentos segun la consola. Dibujarlos
como PNG transparentes con las MISMAS fuentes que carrusel.py evita las
dos cosas y ademas garantiza que la tipografia sea identica a la de las
laminas: Anton para el titular, Barlow para lo demas.

REGLAS DE TEXTO, las de siempre: nada clinico, ninguna cifra sin
confirmar, ninguna promesa de resultado. «Velocidad de reaccion» es
lenguaje de entrenamiento, no de clinica, y es como lo llama Diego.
Ver [[us19-nada-de-kinesiologia]].

FFMPEG
En este PC no hay ffmpeg propio: se usa el que trae Kinovea. Si algun dia
se instala uno, se coge el del PATH primero.
"""
import os
import re
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
FUENTES = os.path.join(BASE, "fuentes")
SALIDA = os.path.join(BASE, "salida_video")

W, H = 1080, 1920
M = 80

ROJO = (226, 28, 37)
BLANCO = (255, 255, 255)

FFMPEG_POSIBLES = [
    "ffmpeg",
    r"C:\Program Files\Kinovea\ffmpeg.exe",
]

# Cada rotulo: (desde, hasta, antetitulo, titular, bajada)
#
# Cuatro tiempos en vez de tres, con la estructura de un anuncio: gancho,
# nombre, que hace y cierre. Y tres niveles de texto en vez de dos —el
# antetitulo pequeño en rojo ordena la lectura y da aire al titular.
#
# Los cortes siguen lo que pasa en la grabacion: primero el plano corto,
# despues el juego con las capsulas encendidas, y al final el plano ancho
# donde se ve la sala entera y cabe el cierre.
#
# BlazePod, no «Bladespot»: corregido por Diego el 9-sep-2026. Es un
# sistema de entrenamiento de reflejos y agilidad con capsulas de luces
# LED tactiles. Lenguaje de entrenamiento, nunca clinico.
#
# SIN PUNTOS NI PUNTOS MEDIOS COMO SEPARADORES. Diego lo pidio el
# 9-sep-2026 y mando la captura señalando el «·» de «Ultra-Sport 19 ·
# Pencahue»: dice que se ve mal. Vale para el «·» y para el punto final
# de los titulares partidos («SE ENCIENDE. LA APAGAS.»), que separan por
# puntuacion lo que ya separa el salto de linea. Donde haga falta unir,
# va una coma o una preposicion, nunca un simbolo.
GUIONES = {

    "blazepod": [
        (0.2, 3.6, "", "¿QUÉ TAN RÁPIDO\nREACCIONAS?", ""),
        (3.6, 8.2, "LO NUEVO EN LA SALA", "BLAZEPOD",
         "Cápsulas LED táctiles e inteligentes"),
        (8.2, 12.2, "CÓMO FUNCIONA", "SE ENCIENDE\nLA APAGAS",
         "Reflejos, agilidad y coordinación"),
        (12.2, 99.0, "", "PRÓXIMAMENTE\nEN LA SALA",
         "Ultra-Sport 19, Pencahue"),
    ],

    # El recorrido por la sala vacia. Los datos NO se inventan: los tres
    # que aparecen —el equipamiento, el tope de ocho por hora y la
    # direccion— son los que Diego ya tiene aprobados y programados en sus
    # propias historias de Notion.
    "sala": [
        (0.2, 3.8, "", "ASÍ ES\nPOR DENTRO", ""),
        (3.8, 8.0, "ULTRA-SPORT 19", "TODO EN\nUNA SALA",
         "Rack, barra, mancuernas, poleas y cardio aparte"),
        (8.0, 12.0, "POR QUÉ SE SIENTE DISTINTO", "MÁXIMO 8\nPOR HORA",
         "Siempre hay alguien mirando cómo lo haces"),
        (12.0, 99.0, "", "TE ESPERAMOS",
         "Hernando Bravo de Villalba 811, Pencahue"),
    ],
}


def f(nombre, tam):
    return ImageFont.truetype(os.path.join(FUENTES, nombre), tam)


def buscar_ffmpeg():
    for c in FFMPEG_POSIBLES:
        try:
            subprocess.run([c, "-version"], stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, check=True)
            return c
        except Exception:
            continue
    return None


def velo(d):
    """Degradado oscuro arriba y abajo: sin esto el texto blanco se pierde
    en los cuadros claros, que aqui son casi todos por la madera."""
    for y in range(0, 620):
        a = int(190 * (1 - y / 620.0) ** 1.4)
        d.line([(0, y), (W, y)], fill=(0, 0, 0, a))
    for y in range(H - 260, H):
        a = int(170 * ((y - (H - 260)) / 260.0) ** 1.2)
        d.line([(0, y), (W, y)], fill=(0, 0, 0, a))


def marca(d):
    """La firma de siempre, igual que en las laminas del carrusel."""
    ft = f("Anton.ttf", 42)
    x, y = M, H - 120
    d.text((x, y), "ULTRA-SPORT ", font=ft, fill=BLANCO + (235,), anchor="ls")
    x += d.textlength("ULTRA-SPORT ", font=ft)
    d.text((x, y), "19", font=ft, fill=(240, 176, 42, 255), anchor="ls")


def rotulo(antetitulo, titular, bajada):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    velo(d)

    y = 168

    # El filo rojo de la marca. Sin antetitulo va solo; con antetitulo se
    # pone a su izquierda, como una viñeta, y los dos ocupan una linea.
    if antetitulo:
        fa = f("BarlowCondensed-Bold.ttf", 40)
        d.rectangle([M, y + 12, M + 46, y + 20], fill=ROJO + (255,))
        d.text((M + 66, y - 4), antetitulo.upper(), font=fa,
               fill=(255, 255, 255, 210), anchor="la")
        y += 62
    else:
        d.rectangle([M, y, M + 120, y + 10], fill=ROJO + (255,))
        y += 44

    ft = f("Anton.ttf", 108)
    alto = int(108 * 1.06)
    for ln in titular.split("\n"):
        d.text((M, y), ln, font=ft, fill=BLANCO + (255,), anchor="la")
        y += alto

    if bajada:
        fb = f("Barlow-SemiBold.ttf", 44)
        d.text((M, y + 18), bajada, font=fb, fill=(255, 255, 255, 230),
               anchor="la")

    marca(d)
    return im


def medir(ff, entrada):
    """Ancho y alto del video, sacados de la salida de ffmpeg -i.

    Se lee asi y no con ffprobe porque el ffmpeg de Kinovea viene solo:
    no trae ffprobe al lado.
    """
    r = subprocess.run([ff, "-hide_banner", "-i", entrada],
                       capture_output=True, text=True)
    texto = (r.stderr or "") + (r.stdout or "")
    m = re.search(r"Video:.*?, (\d{2,5})x(\d{2,5})", texto)
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2))


def main():
    if len(sys.argv) < 3:
        print("Faltan argumentos.")
        print("    python tools/redes/video_promo.py <video.mp4> <guion>")
        print("    guiones: " + ", ".join(sorted(GUIONES)))
        return 2
    entrada, clave = sys.argv[1], sys.argv[2]
    if not os.path.exists(entrada):
        print("No existe: " + entrada)
        return 2
    if clave not in GUIONES:
        print("No hay guion «" + clave + "». Hay: " + ", ".join(sorted(GUIONES)))
        return 2
    rotulos = GUIONES[clave]

    ff = buscar_ffmpeg()
    if not ff:
        print("No se encontro ffmpeg. Probadas: " + ", ".join(FFMPEG_POSIBLES))
        return 1

    ancho, alto = medir(ff, entrada)
    if not ancho:
        print("No se pudo leer el tamaño del video.")
        return 1
    apaisado = ancho > alto
    print("entrada   %dx%d  (%s)" % (ancho, alto,
                                     "apaisado" if apaisado else "vertical"))

    os.makedirs(SALIDA, exist_ok=True)
    tmp = os.path.join(SALIDA, "_rotulos")
    os.makedirs(tmp, exist_ok=True)

    pngs = []
    for i, (a, b, ante, tit, baj) in enumerate(rotulos, 1):
        p = os.path.join(tmp, "rotulo%d.png" % i)
        rotulo(ante, tit, baj).save(p, "PNG")
        pngs.append(p)
        print("rotulo %d  %5.1f-%.1f s  %s" % (i, a, b, tit.replace("\n", " ")))

    salida = os.path.join(SALIDA, "us19_promo_" + clave + ".mp4")

    if apaisado:
        # Un video apaisado en una historia deja franjas negras, y recortarlo
        # a 9:16 se come los lados, que en un recorrido por la sala son
        # justo lo que hay que enseñar. Se pone el video entero en el centro
        # y detras una copia suya ampliada y desenfocada, que rellena sin
        # inventar nada. Ademas deja arriba y abajo una banda tranquila
        # donde el texto se lee mucho mejor que sobre la imagen.
        cadena = (
            "[0:v]scale=%d:%d:force_original_aspect_ratio=increase,"
            "crop=%d:%d,boxblur=42:2,setsar=1[fondo];"
            "[0:v]scale=%d:-2:flags=lanczos,setsar=1[frente];"
            "[fondo][frente]overlay=(W-w)/2:(H-h)/2[v0]"
        ) % (W, H, W, H, W)
    else:
        cadena = "[0:v]scale=%d:%d:flags=lanczos,setsar=1[v0]" % (W, H)

    prev = "v0"
    for i, (a, b, _, _, _) in enumerate(rotulos, 1):
        sig = "v%d" % i
        cadena += ";[%s][%d:v]overlay=0:0:enable='between(t,%s,%s)'[%s]" % (
            prev, i, a, b, sig)
        prev = sig

    cmd = [ff, "-hide_banner", "-loglevel", "error", "-y", "-i", entrada]
    for p in pngs:
        cmd += ["-i", p]
    cmd += ["-filter_complex", cadena,
            "-map", "[" + prev + "]", "-map", "0:a?",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-pix_fmt", "yuv420p",
            # El audio se COPIA tal cual. El ffmpeg de Kinovea es viejo y su
            # codificador aac esta marcado como experimental: pide -strict -2
            # y encima recodificaria sin ninguna necesidad, porque la fuente
            # ya viene en aac.
            "-c:a", "copy",
            "-movflags", "+faststart",
            salida]

    print("")
    print("montando...")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("ffmpeg fallo:")
        print(r.stderr[-1500:])
        return 1

    print("LISTO: " + salida)
    print("%.1f MB" % (os.path.getsize(salida) / 1048576.0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
