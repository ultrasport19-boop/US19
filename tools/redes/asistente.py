# -*- coding: utf-8 -*-
"""US19 - historias que enseñan a usar el asistente de WhatsApp.

    python tools/redes/asistente.py

POR QUE EXISTEN
El asistente sabe hacer una docena de cosas y la mayoria de los socios usa
dos: preguntar el horario y mandar el comprobante. Lo demas -cambiar una
sesion sin llamar, avisar que no vas, pedir los datos de transferencia,
ver la tienda- esta ahi y nadie lo sabe. Estas historias lo enseñan de a
una cosa por vez.

UNA COSA POR HISTORIA. Es la regla. Una historia que enseña cinco funciones
no enseña ninguna: se ve tres segundos.

LO QUE SE PUEDE PROMETER
Solo lo que el bot hace HOY. Cada pieza sale de una opcion real del menu
(`enviarMenu` en Codigo.js) o de un comportamiento que se puede comprobar
leyendo el codigo. Nada de «proximamente» ni de funciones a medias: si
alguien escribe la palabra y no pasa nada, la historia hizo daño en vez de
ayudar.

EL ESTILO
El mismo de las siete primeras (US19E_A_asis_*): negro con un resplandor
rojo arriba a la izquierda, cabecera de marca, antetitulo rojo, titular
enorme en Anton partido en blanco y rojo, cuerpo en Barlow y la caja roja
del cierre con el telefono del asistente.

El logo va abajo, junto al telefono: regla de Diego del 9-sep-2026 -en toda
historia y todo video- y estas son las primeras de esta familia que lo
llevan.

REGLAS DE TEXTO: nada clinico, ninguna cifra sin confirmar, ninguna promesa
de resultado, y ningun punto ni simbolo como separador entre las dos
mitades de un titular. Ver [[us19-nada-de-kinesiologia]].
"""
import os

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
FUENTES = os.path.join(BASE, "fuentes")
IMG = os.path.abspath(os.path.join(BASE, "..", "..", "img"))
LOGO = os.path.join(IMG, "logo.png")
SALIDA = os.path.join(BASE, "salida_asistente")

W, H = 1080, 1920
M = 96

NEGRO = (5, 5, 5)
ROJO = (226, 28, 37)
BLANCO = (245, 245, 245)
GRIS = (150, 150, 150)

TELEFONO = "+56 9 6590 2238"
DIRECCION = "Hernando Bravo de Villalba 811, Pencahue"


def f(nombre, tam):
    return ImageFont.truetype(os.path.join(FUENTES, nombre), tam)


def fondo():
    """Negro con un resplandor rojo arriba a la izquierda.

    Se dibuja a un octavo y se amplia: un degradado radial pixel a pixel
    sobre 1080x1920 son dos millones de operaciones en Python y tarda mas
    que todo el resto junto."""
    p = 8
    ch, cv = W // p, H // p
    chico = Image.new("RGB", (ch, cv), NEGRO)
    px = chico.load()
    cx, cy = ch * 0.30, cv * 0.16
    rmax = (ch ** 2 + cv ** 2) ** 0.5 * 0.55
    for y in range(cv):
        for x in range(ch):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            k = max(0.0, 1.0 - d / rmax) ** 2.2
            px[x, y] = (int(5 + 58 * k), int(5 + 10 * k), int(5 + 12 * k))
    return chico.resize((W, H), Image.BILINEAR)


def cabecera(d):
    ft = f("Anton.ttf", 44)
    x, y = M, 128
    d.text((x, y), "ULTRA-SPORT ", font=ft, fill=BLANCO, anchor="ls")
    x += d.textlength("ULTRA-SPORT ", font=ft)
    d.text((x, y), "19", font=ft, fill=ROJO, anchor="ls")
    x += d.textlength("19 ", font=ft)
    fp = f("BarlowCondensed-Bold.ttf", 30)
    d.text((x + 10, y - 4), "P E N C A H U E", font=fp, fill=GRIS, anchor="ls")


def titular(d, y, lineas, corte):
    """El titular. `corte` dice cuantas lineas van en blanco; el resto, rojo."""
    ft = f("Anton.ttf", 108)
    alto = int(108 * 1.02)
    for i, ln in enumerate(lineas):
        d.text((M, y), ln.upper(), font=ft,
               fill=BLANCO if i < corte else ROJO, anchor="la")
        y += alto
    return y


def parrafo(d, y, texto, ancho=None, tam=40, color=None):
    ft = f("Barlow-SemiBold.ttf", tam)
    ancho = ancho or (W - 2 * M)
    lineas, actual = [], ""
    for p in texto.split():
        prueba = (actual + " " + p).strip()
        if d.textlength(prueba, font=ft) <= ancho:
            actual = prueba
        else:
            if actual:
                lineas.append(actual)
            actual = p
    if actual:
        lineas.append(actual)
    for ln in lineas:
        d.text((M, y), ln, font=ft, fill=color or (225, 225, 225), anchor="la")
        y += int(tam * 1.42)
    return y


def lista(d, y, titulo, filas):
    """La lista de dos columnas con la viñeta roja."""
    if titulo:
        ft = f("BarlowCondensed-Bold.ttf", 30)
        d.text((M, y), titulo.upper(), font=ft, fill=GRIS, anchor="la")
        y += 54
    ft = f("Barlow-SemiBold.ttf", 36)
    col = (W - 2 * M) // 2
    for i, txt in enumerate(filas):
        cx = M + (i % 2) * col
        cy = y + (i // 2) * 62
        d.rectangle([cx, cy + 12, cx + 14, cy + 26], fill=ROJO)
        d.text((cx + 30, cy), txt, font=ft, fill=(225, 225, 225), anchor="la")
    return y + ((len(filas) + 1) // 2) * 62


def cierre(im, d):
    """La caja roja del final, con el telefono y el logo de la casa."""
    y0 = H - 330
    d.rounded_rectangle([M, y0, W - M, H - 120], radius=18, fill=ROJO)

    fe = f("BarlowCondensed-Bold.ttf", 38)
    d.text((M + 42, y0 + 38), "E S C R Í B E N O S   P O R   W H A T S A P P",
           font=fe, fill=(255, 235, 235), anchor="la")
    ft = f("Anton.ttf", 62)
    d.text((M + 42, y0 + 92), TELEFONO, font=ft, fill=BLANCO, anchor="la")
    fd = f("Barlow-SemiBold.ttf", 30)
    d.text((M + 42, y0 + 168), DIRECCION, font=fd, fill=(255, 225, 225), anchor="la")

    # El logo, a la derecha del telefono. Regla de Diego del 9-sep-2026:
    # en toda historia y todo video.
    if os.path.exists(LOGO):
        lado = 118
        lg = Image.open(LOGO).convert("RGBA").resize((lado, lado), Image.LANCZOS)
        im.paste(lg, (W - M - lado - 34, y0 + 56), lg)


def pieza(p):
    im = fondo()
    d = ImageDraw.Draw(im, "RGBA")

    cabecera(d)

    # El bloque de texto arranca mas abajo cuando NO hay lista. Si no, el
    # texto se apelotona arriba, la caja del cierre esta abajo del todo y
    # entre medio quedan seiscientos pixeles de nada que se leen como «falta
    # algo» en vez de como aire.
    y0 = 210 if p.get("lista") else 430

    fe = f("BarlowCondensed-Bold.ttf", 34)
    d.text((M, y0), p["ante"].upper(), font=fe, fill=ROJO, anchor="la")

    y = titular(d, y0 + 48, p["titular"], p.get("corte", 1))
    y = parrafo(d, y + 34, p["cuerpo"], ancho=int((W - 2 * M) * 0.86))

    # La lista va anclada abajo, como en las siete originales: es lo que
    # llena el hueco entre el parrafo y la caja roja.
    if p.get("lista"):
        lista(d, max(y + 60, 1120), p.get("lista_titulo", ""), p["lista"])

    cierre(im, d)
    return im


PIEZAS = [

    # 1 · La que mas falta hace: avisar que no vas. Sin esto, el cupo se
    #     queda ocupado y alguien de la lista de espera se queda fuera.
    dict(id="no_asistire", ante="tu asistente en whatsapp",
         titular=["si no vas,", "avisa."], corte=1,
         cuerpo="En el menú está «Avisar que no asistiré». Un toque y listo: "
                "nadie te va a preguntar por qué, y ese cupo queda libre para "
                "alguien que lo estaba esperando.",
         lista_titulo="para qué sirve",
         lista=["Liberas tu cupo", "No queda como falta",
                "Nadie tiene que llamarte", "Toma dos segundos"]),

    # 2 · Cancelar, que no es lo mismo que avisar.
    dict(id="cancelar", ante="una cosa distinta", titular=["cancelar", "no es faltar."],
         corte=1,
         cuerpo="Cancelar quita la reserva del sistema. Avisar que no asistirás "
                "es para cuando ya no alcanzas a cancelar. Las dos están en el "
                "menú y las dos sirven: la peor opción es no hacer ninguna."),

    # 3 · Agendar otra sesion.
    dict(id="agendar_otra", ante="tu asistente en whatsapp",
         titular=["¿te queda", "una hora libre?"], corte=1,
         cuerpo="Escribe «agendar» y el asistente te muestra las horas que quedan "
                "esa semana. Si ya entrenas con nosotros, lo resuelves ahí mismo "
                "sin esperar a que alguien te conteste."),

    # 4 · Transferir.
    dict(id="transferir", ante="para pagar", titular=["los datos", "sin buscarlos."],
         corte=1,
         cuerpo="«Datos para transferir» en el menú y aparecen la cuenta, el rut y "
                "el correo. No hace falta que los tengas guardados ni que se los "
                "pidas a nadie."),

    # 5 · Como llegar.
    dict(id="llegar", ante="la primera vez", titular=["te manda", "el mapa."],
         corte=1,
         cuerpo="«Cómo llegar» te abre la ubicación exacta. Es el pin del gimnasio, "
                "no la calle: buscarnos por la dirección a veces deja a la gente "
                "media cuadra más allá."),

    # 6 · Tienda.
    dict(id="tienda", ante="también por whatsapp", titular=["la ropa,", "en el mismo chat."],
         corte=1,
         cuerpo="Escribe «tienda» y te muestra lo que hay, con talla y precio. "
                "Cada prenda es única: cuando alguien la aparta, desaparece de la "
                "lista. Por eso lo que ves es lo que queda de verdad."),

    # 7 · Precios, para el que todavia no entra.
    dict(id="precios", ante="antes de decidirte", titular=["pregunta", "el precio."],
         corte=1,
         cuerpo="Escribe «precios» y te llegan los tres planes con lo que incluye "
                "cada uno. Sin hablar con nadie y sin que te insistan después.",
         lista_titulo="los planes",
         lista=["2 veces por semana", "3 veces por semana",
                "4 veces por semana", "Todos con evaluación"]),

    # 8 · El recordatorio, que ya reciben pero no saben de donde sale.
    dict(id="recordatorio", ante="cada mañana", titular=["te acordamos", "tu hora."],
         corte=1,
         cuerpo="Si tienes sesión hoy, el asistente te escribe temprano. No hay que "
                "pedirlo ni activarlo: sale solo con la reserva que ya tienes."),

    # 9 · La ficha, para el que recien llega.
    dict(id="ficha", ante="para entrar", titular=["primero", "la ficha."], corte=1,
         cuerpo="Es el primer paso y toma dos minutos. Con ella lista, Diego revisa "
                "si hay cupo en tu horario y te confirma por acá. Los cupos son "
                "ocho por hora, así que no siempre hay para todos a la vez."),

    # 10 · Que no hace falta el menu.
    dict(id="palabras", ante="ni siquiera hace falta el menú",
         titular=["escríbele", "como hablas."], corte=1,
         cuerpo="«¿A qué hora abren?», «quiero cambiar mi hora», «¿tienen poleras "
                "talla M?». Lo entiende igual. El menú está por si prefieres tocar "
                "en vez de escribir, no porque haya que usarlo."),
]


def main():
    os.makedirs(SALIDA, exist_ok=True)
    for viejo in os.listdir(SALIDA):
        if viejo.lower().endswith(".jpg"):
            os.remove(os.path.join(SALIDA, viejo))
    for p in PIEZAS:
        ruta = os.path.join(SALIDA, "US19E_B_" + p["id"] + ".jpg")
        pieza(p).save(ruta, "JPEG", quality=88, optimize=True)
        print("  " + p["id"] + "  " + " ".join(p["titular"]))
    print("")
    print("  BORRADOR en " + SALIDA + " (no se programo nada)")


if __name__ == "__main__":
    main()
