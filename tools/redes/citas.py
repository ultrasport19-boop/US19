# -*- coding: utf-8 -*-
"""US19 - cartas de cita al estilo de la referencia de Diego.

    python tools/redes/citas.py

DE DONDE SALE
Diego trajo el 9-sep-2026 un carrusel de @4life_arg: personajes de anime
en dos tonos planos sobre un rojo casi identico al de la marca, con una
comilla grande, la frase en amarillo y blanco alternados, y la firma de
la cuenta abajo. Pidio lo mismo con SU marca, recortando las imagenes y
manteniendo los personajes.

COMO SE CONSIGUE EL DUOTONO
La referencia usa ilustracion recortada sobre un fondo rojo plano. Estos
fotogramas tienen fondo propio y no se pueden recortar a mano uno a uno,
asi que en vez de recortar se mapea TODA la imagen a una rampa de tres
paradas: sombras a azul muy oscuro, medios a azul, y luces al rojo de la
marca. Queda la misma paleta de dos colores planos, que es lo que hace el
estilo, y ademas el rojo aparece solo donde la luz lo pone.

LA FRASE NO SE ATRIBUYE A NINGUN PERSONAJE. La referencia cita a Thors o
a Canuto de verdad; inventar una frase y ponersela en la boca a un
personaje seria falsificar una cita. Aqui las frases son de la casa y van
firmadas por la casa, que ademas es lo que Diego pidio: su marca.

SIN PUNTOS NI SIMBOLOS COMO SEPARADORES, regla suya del 9-sep-2026: las
frases se cortan con coma o con salto de linea, nunca con un punto ni un
punto medio.

REGLAS DE TEXTO: nada clinico, ninguna cifra sin confirmar, ninguna
promesa de resultado. Ver [[us19-nada-de-kinesiologia]].

DERECHOS: los personajes son de terceros. Diego afirma el 9-sep-2026 que
cuenta con autorizacion. Las fuentes viven en fuentes_img/, que esta en
.gitignore porque este repositorio es publico.
"""
import os

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
FUENTES = os.path.join(BASE, "fuentes")
ILUS = os.path.join(BASE, "fuentes_img")
IMG = os.path.abspath(os.path.join(BASE, "..", "..", "img"))
LOGO = os.path.join(IMG, "logo.png")
SALIDA = os.path.join(BASE, "salida_citas")

FORMATOS = [("feed", 1080, 1350), ("historia", 1080, 1920)]
W, H = 1080, 1350
M = 84

ROJO = (226, 28, 37)
ORO = (240, 176, 42)
BLANCO = (255, 255, 255)

# La rampa del duotono. Tres paradas: de la sombra a la luz.
RAMPA = [
    (0.00, (10, 12, 42)),      # azul casi negro, para las lineas
    (0.55, (58, 66, 186)),     # el azul plano de la referencia
    (1.00, ROJO),              # las luces se van al rojo de la marca
]

# Cada carta: la frase partida en lineas (se alternan oro y blanco, como
# en la referencia), de que fotograma sale y como se encaja.
#
# ENCAJE
#   "llenar"  recorta al centro hasta llenar el cuadro. Sirve cuando la
#             imagen es vertical o cuadrada y el personaje esta centrado.
#   "abajo"   escala a todo el ancho y la apoya abajo, dejando arriba el
#             rojo plano de la marca para la frase. Es como coloca el arte
#             la referencia de @4life_arg, y es la unica forma decente de
#             usar una imagen MUY apaisada: recortar un 780x390 a 9:16 deja
#             una tira central donde no se entiende que se ve. Paso con la
#             tercera carta de la primera tanda y no se repite.
CARTAS = [
    # --- Primera tanda: One Piece y Dragon Ball -----------------------
    dict(lineas=["La fuerza", "no se hereda,", "se construye"],
         img="despues.jpg", encaje="llenar"),

    dict(lineas=["No busques", "motivación,", "busca horario"],
         img="antes_goku.jpg", encaje="llenar"),

    dict(lineas=["Lo difícil", "es la puerta,", "lo demás", "ya está resuelto"],
         img="antes.jpg", encaje="llenar"),

    dict(lineas=["Nadie llega", "sabiendo,", "para eso", "estamos"],
         img="despues_goku.jpg", encaje="llenar"),

    # --- Segunda tanda: Caballeros del Zodiaco ------------------------
    # Diego las trajo el 9-sep-2026 pidiendo frases para «la otra
    # generacion»: los que crecieron viendo esta serie. El gancho es la
    # nostalgia, nunca la edad — nada de «a los 40», que suena a reproche.
    dict(lineas=["Creciste", "viendo héroes,", "ahora te toca", "a ti"],
         img="seiya_pegaso.jpg", encaje="abajo"),

    dict(lineas=["Nadie llega solo,", "aquí tampoco"],
         img="caballeros_perfil.jpg", encaje="abajo"),

    dict(lineas=["Levantarse", "otra vez,", "eso ya sabes", "hacerlo"],
         img="seiya_brazos.jpg", encaje="llenar"),

    dict(lineas=["No hace falta", "ser joven,", "hace falta", "empezar"],
         img="armadura_dorada.jpg", encaje="llenar"),

    dict(lineas=["Lo difícil", "no es la fuerza,", "es volver", "mañana"],
         img="thorfinn.jpg", encaje="abajo"),

    # --- Tercera tanda: los jueves que quedan de 2026 ------------------
    # Mismas ilustraciones, frases nuevas. Entre tanda y tanda hay dos
    # meses, asi que no se lee como repeticion.
    dict(lineas=["No se trata", "de poder,", "se trata de venir"],
         img="despues.jpg", encaje="llenar"),

    dict(lineas=["Empezar", "cuesta una vez,", "no volver", "cuesta siempre"],
         img="antes_goku.jpg", encaje="llenar"),

    dict(lineas=["Aquí nadie mira", "lo que levantas"],
         img="caballeros_perfil.jpg", encaje="abajo"),

    dict(lineas=["Un mes", "no se nota,", "tres meses", "no se disimulan"],
         img="despues_goku.jpg", encaje="llenar"),

    dict(lineas=["Descansar", "es parte del plan,", "rendirse no"],
         img="seiya_brazos.jpg", encaje="llenar"),

    dict(lineas=["No compitas", "con nadie,", "solo con", "el de ayer"],
         img="seiya_pegaso.jpg", encaje="abajo"),

    # 24 de diciembre. Ni culpa ni sermon: es Nochebuena.
    dict(lineas=["Come rico,", "ríete,", "y vuelve", "el lunes"],
         img="antes.jpg", encaje="llenar"),

    # 31 de diciembre, justo antes del proposito de año nuevo.
    dict(lineas=["El de enero", "te va a", "agradecer esto"],
         img="armadura_dorada.jpg", encaje="llenar"),
]


def f(nombre, tam):
    return ImageFont.truetype(os.path.join(FUENTES, nombre), tam)


def duotono(im):
    """Mapa de degradado sobre la luminancia. Es lo que convierte un
    fotograma cualquiera en la paleta de la referencia."""
    gris = im.convert("L")
    tabla = []
    for canal in range(3):
        col = []
        for v in range(256):
            t = v / 255.0
            # entre que dos paradas cae
            for i in range(len(RAMPA) - 1):
                t0, c0 = RAMPA[i]
                t1, c1 = RAMPA[i + 1]
                if t <= t1 or i == len(RAMPA) - 2:
                    k = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
                    k = max(0.0, min(1.0, k))
                    col.append(int(round(c0[canal] + (c1[canal] - c0[canal]) * k)))
                    break
        tabla.extend(col)
    return gris.convert("RGB").point(tabla)


def rellenar(ruta):
    """Recorta al centro para llenar el formato entero, sin deformar.
    «Recorten las imagenes», que es justo lo que pidio Diego."""
    im = Image.open(ruta).convert("RGB")
    escala = max(W / im.width, H / im.height)
    nueva = im.resize((max(W, int(im.width * escala)),
                       max(H, int(im.height * escala))), Image.LANCZOS)
    izq = (nueva.width - W) // 2
    arr = (nueva.height - H) // 2
    return nueva.crop((izq, arr, izq + W, arr + H))


def apoyar_abajo(ruta):
    """La imagen a todo el ancho, apoyada abajo, y el resto rojo plano.

    Es la composicion de la referencia y la unica que respeta una imagen
    muy apaisada: recortarla a 4:5 o a 9:16 se lleva por delante casi
    todo el encuadre. Ademas deja arriba una zona limpia de un solo color
    donde la frase se lee sin velo ninguno.
    """
    im = Image.open(ruta).convert("RGB")

    # A lo ancho y ya esta, salvo que quede una tira demasiado baja. Una
    # imagen 16:9 puesta a 1080 de ancho ocupa 608 px, que en una historia
    # de 1920 es un tercio: queda un rojo enorme y vacio. Se pide un minimo
    # de MINIMO_ALTO del alto total y, si hace falta llegar, se agranda y se
    # recorta por los lados. Es el punto medio entre no ver el dibujo y
    # perder el encuadre entero.
    MINIMO_ALTO = 0.48
    escala = max(W / float(im.width), (H * MINIMO_ALTO) / float(im.height))
    im = im.resize((int(round(im.width * escala)),
                    int(round(im.height * escala))), Image.LANCZOS)
    if im.width > W:
        izq = (im.width - W) // 2
        im = im.crop((izq, 0, izq + W, im.height))
    im = duotono(im)

    fondo = Image.new("RGB", (W, H), ROJO)
    if im.height >= H:
        # Cabe justa o se pasa: se apoya abajo y se recorta lo que sobre
        # por arriba, que es donde ira la frase de todos modos.
        fondo.paste(im.crop((0, im.height - H, W, im.height)), (0, 0))
    else:
        fondo.paste(im, (0, H - im.height))
    return fondo


def velo(d, hasta):
    """Sombra suave detras del texto. Sin esto la frase se pierde justo
    donde el duotono se va al rojo."""
    for y in range(0, hasta):
        a = int(170 * (1 - y / float(hasta)) ** 1.3)
        d.line([(0, y), (W, y)], fill=(0, 0, 0, a))
    for y in range(H - 220, H):
        a = int(150 * ((y - (H - 220)) / 220.0) ** 1.2)
        d.line([(0, y), (W, y)], fill=(0, 0, 0, a))


def insignia(destino, x, y, lado):
    """Pega el logo de la casa. Devuelve el ancho que ocupo, 0 si no esta.

    El archivo esta en modo paleta: sin convert("RGBA") se pierde la
    transparencia y sale un cuadro blanco alrededor del circulo. Y si
    faltara, se devuelve 0 y la firma queda como estaba: una pieza a medio
    dibujar es peor que una sin insignia.
    """
    if not os.path.exists(LOGO):
        return 0
    lg = Image.open(LOGO).convert("RGBA").resize((lado, lado), Image.LANCZOS)
    if destino.mode == "RGBA":
        destino.alpha_composite(lg, (int(x), int(y)))
    else:
        destino.paste(lg, (int(x), int(y)), lg)
    return lado


def marca(capa, d):
    ft = f("Anton.ttf", 40)
    x, y = M, H - 84
    # Cabe holgado: el velo de abajo empieza en H-220, asi que el logo cae
    # entero sobre zona oscurecida y no compite con la ilustracion.
    ancho = insignia(capa, M, y - 78, 96)
    if ancho:
        x = M + ancho + 20
    d.text((x, y), "ULTRA-SPORT ", font=ft, fill=BLANCO + (235,), anchor="ls")
    x += d.textlength("ULTRA-SPORT ", font=ft)
    d.text((x, y), "19", font=ft, fill=ORO + (255,), anchor="ls")


def carta(lineas, ruta_img, encaje="llenar"):
    if encaje == "abajo":
        im = apoyar_abajo(ruta_img)
    else:
        im = duotono(rellenar(ruta_img))
    im = im.convert("RGBA")

    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)

    tam = 82 if len(lineas) <= 3 else 74
    ft = f("Barlow-Bold.ttf", tam)
    alto = int(tam * 1.16)

    # Con la imagen apoyada abajo, arriba ya hay un rojo plano: el velo
    # solo ensuciaria. Solo se pone cuando el texto cae sobre la foto.
    if encaje != "abajo":
        velo(d, 200 + alto * len(lineas))
    else:
        for y in range(H - 220, H):
            a = int(150 * ((y - (H - 220)) / 220.0) ** 1.2)
            d.line([(0, y), (W, y)], fill=(0, 0, 0, a))

    # La comilla grande de la referencia, en blanco y bien arriba.
    fc = f("Anton.ttf", 150)
    d.text((M - 6, 96), "“", font=fc, fill=BLANCO + (255,), anchor="la")

    y = 250
    for i, ln in enumerate(lineas):
        # Oro y blanco alternados, igual que en la referencia.
        color = ORO if i % 2 == 0 else BLANCO
        d.text((M, y), ln, font=ft, fill=color + (255,), anchor="la")
        y += alto

    fa = f("Barlow-SemiBold.ttf", 44)
    d.text((M, y + 16), "— Ultra-Sport 19", font=fa,
           fill=(255, 255, 255, 210), anchor="la")

    marca(capa, d)
    return Image.alpha_composite(im, capa).convert("RGB")


def main():
    global W, H
    if not os.path.isdir(ILUS):
        print("Falta la carpeta " + ILUS)
        return 1

    for nombre_f, ancho, alto in FORMATOS:
        W, H = ancho, alto
        carpeta = os.path.join(SALIDA, nombre_f)
        os.makedirs(carpeta, exist_ok=True)
        for viejo in os.listdir(carpeta):
            if viejo.lower().endswith(".png"):
                os.remove(os.path.join(carpeta, viejo))

        print("  " + nombre_f + "  " + str(W) + "x" + str(H))
        for i, c in enumerate(CARTAS, 1):
            ruta = os.path.join(ILUS, c["img"])
            if not os.path.exists(ruta):
                print("    falta " + c["img"] + ", se salta")
                continue
            im = carta(c["lineas"], ruta, c.get("encaje", "llenar"))
            nom = "US19_CITA_%02d_%s.png" % (
                i, "-".join(c["lineas"][0].lower().split())
                .replace("á", "a").replace("é", "e").replace("í", "i")
                .replace("ó", "o").replace("ú", "u").replace("ñ", "n")
                .replace(",", ""))
            im.save(os.path.join(carpeta, nom), "PNG")
            print("    " + nom)

    print("")
    print("  Todo en " + SALIDA)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
