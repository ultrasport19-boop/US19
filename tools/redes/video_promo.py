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

# El logo de la casa. Vive en el repositorio de las paginas, que es de
# donde lo sirve la web, para no tener dos copias que se separen.
LOGO = os.path.abspath(os.path.join(BASE, "..", "..", "img", "logo.png"))
LOGO_ALTO = 162

# El numero del asistente, el mismo de toda la web publica.
TELEFONO = "+56 9 6590 2238"

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
# El cierre es el mismo en las cinco versiones de la oferta: una sola
# salida, el numero del asistente y la direccion. Definirlo una vez
# evita que cambie el telefono en una y se quede viejo en las otras.
CIERRE = (12.6, 99.0, "", "ESCRÍBENOS\nPOR WHATSAPP",
          TELEFONO + "\nHernando Bravo de Villalba 811, Pencahue")

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

    # La escasez va primero: en una historia se ven tres segundos, y si el
    # gancho es la presentacion, el que ya conoce el gimnasio pasa de largo.
    #
    # El numero de cupos lo pone Diego, que es quien sabe que horas estan
    # llenas: el tope de la sala es 85 y hay 62 activos, asi que los tres
    # no salen del total sino de una hora concreta.
    #
    # Los otros dos datos son los que el bot ya responde a «precios».
    "cupos": [
        (0.2, 4.0, "", "QUEDAN\n3 CUPOS", ""),
        (4.0, 8.4, "ULTRA-SPORT 19", "MÁXIMO 8\nPOR HORA",
         "Por eso los cupos se acaban"),
        (8.4, 12.6, "LO QUE INCLUYE", "UN PLAN\nPARA TI",
         "Evaluación inicial y seguimiento personalizado"),
        CIERRE,
    ],

    # Las cuatro de abajo son la MISMA oferta contada por otro lado. Se
    # reparten con semanas de por medio para que quien vio una en
    # septiembre no reconozca la de noviembre: cambia el gancho, cambia el
    # dato y cambia el motivo para escribir.

    # 2 · El horario, para quien cree que no le va a calzar.
    "horarios": [
        (0.2, 4.0, "", "ENTRENA A LA HORA\nQUE PUEDAS", ""),
        # 9-sep-2026 — decia «lunes a sabado, de 07:00 a 22:00», que era un
        # dato mio equivocado: salia de la ventana de Calendly, no del
        # horario del gimnasio. El bot y la web dicen lo mismo y dicen esto.
        (4.0, 8.4, "HORARIO", "LUNES\nA VIERNES", "De 06:00 a 22:00"),
        (8.4, 12.6, "CÓMO SE AGENDA", "ELIGES\nTU HORA",
         "Y la cambias si se te complica la semana"),
        CIERRE,
    ],

    # 3 · La medicion, que es lo que de verdad distingue a la casa.
    "incluye": [
        (0.2, 4.0, "", "ACÁ NO SE\nENTRENA A CIEGAS", ""),
        (4.0, 8.4, "LO QUE INCLUYE", "MEDIMOS TU\nCOMPOSICIÓN",
         "Masa muscular, grasa, agua y perímetros"),
        (8.4, 12.6, "CADA MES", "VUELVES\nA MEDIRTE",
         "Y el plan se ajusta a lo que muestran los números"),
        CIERRE,
    ],

    # 4 · El precio. Va cuarta a proposito: primero se cuenta que hay, y
    # recien despues cuanto cuesta.
    "precio": [
        (0.2, 4.0, "", "DESDE $15.000\nAL MES", ""),
        (4.0, 8.4, "PLANES", "2, 3 O 4 VECES\nPOR SEMANA",
         "$15.000, $25.000 y $35.000 al mes"),
        (8.4, 12.6, "TODOS INCLUYEN", "EVALUACIÓN\nY SEGUIMIENTO",
         "El plan se arma contigo, no se te entrega hecho"),
        CIERRE,
    ],

    # 6 · Sin matricula. Es la unica pieza que ataca el miedo a quedar
    # amarrado, y dice lo mismo que la seccion «El plan y el dinero» de la
    # ficha de ingreso: no hace falta congelar un plan si dejar de venir no
    # cuesta nada. Los tres datos estan comprobados —«sin matricula» y
    # «desde $15.000» salen de la web, y las mediciones de quien se va
    # siguen en Notion porque Inactivo no borra nada—.
    "sinmatricula": [
        (0.2, 4.0, "", "SIN MATRÍCULA\nSIN AMARRE", ""),
        (4.0, 8.4, "LO QUE PAGAS", "SOLO EL MES\nQUE ENTRENAS",
         "Desde $15.000, y si paras no te cobramos"),
        (8.4, 12.6, "Y SI VUELVES", "RETOMAS DONDE\nLO DEJASTE",
         "Tu ficha y tus mediciones quedan guardadas"),
        CIERRE,
    ],

    # 5 · La sala vacia como argumento, para quien viene de un gimnasio lleno.
    "sinmasificar": [
        (0.2, 4.0, "", "SIN ESPERAR\nMÁQUINA", ""),
        (4.0, 8.4, "POR QUÉ", "MÁXIMO 8\nPOR HORA",
         "Siempre hay alguien mirando cómo lo haces"),
        (8.4, 12.6, "LA SALA", "TODO EN\nUN SOLO SITIO",
         "Rack, barra, mancuernas, poleas y cardio aparte"),
        CIERRE,
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


def velo(d, alto=620):
    """Degradado oscuro arriba y abajo: sin esto el texto blanco se pierde
    en los cuadros claros, que aqui son casi todos por la madera.

    En la version de foto el bloque de texto es mas largo -lleva el gancho
    y el cierre juntos- y el velo tiene que llegar mas abajo con el."""
    for y in range(0, alto):
        a = int(190 * (1 - y / float(alto)) ** 1.4)
        d.line([(0, y), (W, y)], fill=(0, 0, 0, a))
    for y in range(H - 260, H):
        a = int(170 * ((y - (H - 260)) / 260.0) ** 1.2)
        d.line([(0, y), (W, y)], fill=(0, 0, 0, a))


def marca(d, im=None):
    """La firma: el logo de la casa y el nombre a su derecha.

    El logo se queda en todos los fotogramas, no solo en el cierre. Una
    marca que sale al final se ve una vez; una que esta siempre acompaña
    cada fotograma que alguien pause o comparta.

    Si el archivo del logo no esta, se dibuja solo el nombre: un video a
    medio montar es peor que un video sin insignia.
    """
    x, y = M, H - 120
    if im is not None and os.path.exists(LOGO):
        ins = Image.open(LOGO).convert("RGBA")
        lado = LOGO_ALTO
        ins = ins.resize((lado, lado), Image.LANCZOS)
        arriba = H - 116 - lado // 2
        im.alpha_composite(ins, (M, arriba))
        x = M + lado + 26

    ft = f("Anton.ttf", 42)
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
        # Varias lineas separadas por salto: hace falta para el cierre, que
        # lleva telefono y direccion. Los guiones viejos pasan una sola y
        # se comportan igual que antes.
        fb = f("Barlow-SemiBold.ttf", 44)
        yy = y + 18
        for ln in bajada.split("\n"):
            d.text((M, yy), ln, font=fb, fill=(255, 255, 255, 230),
                   anchor="la")
            yy += 56

    marca(d, im)
    return im


def foto(rotulos, fondo):
    """La historia fija: gancho arriba, cierre debajo, todo de una vez.

    `fondo` es un fotograma ya escalado a 1080x1920. Se dibuja sobre el
    porque el fondo tiene que verse: es la sala de verdad, que es el unico
    argumento que ningun texto puede dar.
    """
    _, _, ante, tit, baj = rotulos[0]
    _, _, _, _, cierre = rotulos[-1]

    im = fondo.convert("RGBA")
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    velo(d, alto=1040)

    y = 168
    if ante:
        fa = f("BarlowCondensed-Bold.ttf", 40)
        d.rectangle([M, y + 12, M + 46, y + 20], fill=ROJO + (255,))
        d.text((M + 66, y - 4), ante.upper(), font=fa,
               fill=(255, 255, 255, 210), anchor="la")
        y += 62
    else:
        d.rectangle([M, y, M + 120, y + 10], fill=ROJO + (255,))
        y += 44

    ft = f("Anton.ttf", 108)
    for ln in tit.split("\n"):
        d.text((M, y), ln, font=ft, fill=BLANCO + (255,), anchor="la")
        y += int(108 * 1.06)

    if baj:
        fb = f("Barlow-SemiBold.ttf", 44)
        for ln in baj.split("\n"):
            d.text((M, y + 18), ln, font=fb, fill=(255, 255, 255, 230),
                   anchor="la")
            y += 56

    # El cierre. Va separado por un filete rojo porque es otra cosa: hasta
    # aqui se cuenta, de aqui para abajo se pide que escriban.
    y += 54
    d.rectangle([M, y, M + 120, y + 10], fill=ROJO + (255,))
    y += 40

    fc = f("BarlowCondensed-Bold.ttf", 46)
    d.text((M, y), "ESCRÍBENOS POR WHATSAPP", font=fc,
           fill=(255, 255, 255, 220), anchor="la")
    y += 58

    lineas = [l for l in cierre.split("\n") if l]
    if lineas:
        fn = f("Anton.ttf", 76)
        d.text((M, y), lineas[0], font=fn, fill=BLANCO + (255,), anchor="la")
        y += 92
    for ln in lineas[1:]:
        fd = f("Barlow-SemiBold.ttf", 40)
        d.text((M, y), ln, font=fd, fill=(255, 255, 255, 220), anchor="la")
        y += 52

    marca(d, capa)
    return Image.alpha_composite(im, capa).convert("RGB")


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
        print("    python tools/redes/video_promo.py <video.mp4> <guion> [foto]")
        print("    «foto» saca la historia fija en JPG, que es la que SI se")
        print("    puede programar en Notion: el bot no publica video")
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
    solo_foto = len(sys.argv) > 3 and sys.argv[3].lower() == "foto"

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

    if solo_foto:
        # El fotograma se saca a los 2 s: el primer segundo suele traer el
        # tiron de la mano al empezar a grabar.
        crudo = os.path.join(tmp, "fondo_" + clave + ".png")
        cmd = [ff, "-hide_banner", "-loglevel", "error", "-y",
               "-ss", "2", "-i", entrada, "-frames:v", "1",
               "-vf", "scale=%d:%d:flags=lanczos" % (W, H), crudo]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print("ffmpeg fallo al sacar el fotograma:")
            print(r.stderr[-800:])
            return 1
        destino = os.path.join(SALIDA, "us19_historia_" + clave + ".jpg")
        foto(rotulos, Image.open(crudo)).save(destino, "JPEG", quality=90,
                                              optimize=True)
        print("LISTO: " + destino)
        print("%.0f KB" % (os.path.getsize(destino) / 1024.0))
        return 0

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
