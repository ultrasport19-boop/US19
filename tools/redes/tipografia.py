# -*- coding: utf-8 -*-
"""US19 - piezas tipograficas sobre papel, al estilo @neuromark.pro.

    python tools/redes/tipografia.py

DE DONDE SALE
Diego trajo el 9-sep-2026 un carrusel de @neuromark.pro: fondo de papel
crudo, tipografia con serifa, una frase arriba y otra abajo, y trazos de
color hechos a mano —subrayado rojo en la primera, verde en la segunda,
resaltador amarillo— con una foto en medio.

    «Primero sigues el mapa  /  Luego conoces el camino»
    «No esperes a ser bueno para empezar  /  Empieza para volverte bueno»

Es el reverso del carril de anime: sin personajes, sin rojo de marca en
todo el cuadro, calmado y de lectura adulta. Sirve para la gente a la que
el anime le da igual.

LAS FOTOS SON LAS DEL GIMNASIO, no de banco de imagenes. La referencia usa
escaleras y mapas comprados; aqui hay algo mejor, que es la sala de
verdad. Una escalera de stock no vende un gimnasio de Pencahue.

LA SERIFA
No hay ninguna en fuentes/ y la descarga de Google Fonts dio 404, asi que
se busca por orden: primero fuentes/, despues las del sistema. Georgia
tiene el peso editorial que pide el formato. Si algun dia se añade una
serifa propia al repo, entra sola por delante.

REGLAS DE TEXTO: nada clinico, ninguna cifra sin confirmar, ninguna
promesa de resultado, y ningun punto ni simbolo como separador (regla de
Diego del 9-sep-2026). Ver [[us19-nada-de-kinesiologia]].

BORRADOR: esto NO programa nada. Genera los PNG y ya. Diego pidio el
9-sep-2026 ver un borrador antes de que nada entre al calendario.
"""
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
FUENTES = os.path.join(BASE, "fuentes")
IMG = os.path.abspath(os.path.join(BASE, "..", "..", "img"))
SALIDA = os.path.join(BASE, "salida_tipografia")

FORMATOS = [("historia", 1080, 1920), ("feed", 1080, 1350)]
W, H = 1080, 1920
M = 96

PAPEL = (242, 240, 235)
TINTA = (26, 24, 22)
ROJO = (200, 46, 42)
VERDE = (104, 150, 66)
AMARILLO = (247, 216, 90)
AZUL = (88, 118, 196)

SERIFAS_BOLD = [
    os.path.join(FUENTES, "LibreBaskerville-Bold.ttf"),
    r"C:\Windows\Fonts\georgiab.ttf",
    r"C:\Windows\Fonts\constanb.ttf",
    r"C:\Windows\Fonts\timesbd.ttf",
]

# Cada pieza. `foto` vacio = solo texto, como la lamina 6/6 de la referencia.
# Diego tumbo tres frases el 9-sep-2026 y tenia razon en las tres:
#   «cuesta la puerta / cuesta no venir»   -> doble negacion, se traba
#   «vienes por el fisico / por la cabeza» -> «la cabeza» suena a jerga
#   «te miran / te saludan»                -> sugiere que te quedan mirando,
#                                             que es justo el miedo que
#                                             tiene quien no ha entrado nunca
# Se cambian enteras, no se retocan: el problema era la idea, no la palabra.
# Las tres nuevas son concretas y se pueden ver — series, reloj, peso.
PIEZAS = [
    dict(uno="Primero cuentas las series",
         dos="Luego cuentas los meses",
         foto="hero.jpg"),

    dict(uno="Primero miras el reloj",
         dos="Luego miras el peso",
         foto="gym-1.jpg"),

    dict(uno="Primero vienes a probar",
         dos="Luego vienes sin pensarlo",
         foto="sala-1.jpg"),

    # Sin foto: la adaptacion directa de la frase de la referencia.
    dict(uno="No esperes a estar en forma para empezar",
         dos="Empieza para ponerte en forma",
         foto=""),

    # --- Enero 2027 -----------------------------------------------------
    # El 31-dic-2026 se acaba TODO el calendario, y enero es justo el mes
    # en que la gente se apunta a un gimnasio. Estas van sin foto a
    # proposito: las cuatro fotos utiles de la sala ya estan usadas, y el
    # formato de solo texto no necesita ninguna. Asi enero se llena sin
    # depender de que lleguen imagenes nuevas.
    #
    # Ninguna promete resultados ni pone plazos: la unica cifra que
    # aparece es «los ochenta», que es una edad, no una promesa.
    dict(uno="Hoy empieza el año", dos="Y también la semana uno", foto=""),

    dict(uno="No necesitas un plan perfecto",
         dos="Necesitas el primer día", foto=""),

    dict(uno="El verano no se entrena en enero",
         dos="Se entrena todo el año", foto=""),

    dict(uno="Empezar es fácil", dos="Volver es lo que cuenta", foto=""),

    dict(uno="No es fuerza de voluntad",
         dos="Es tener la hora tomada", foto=""),

    dict(uno="Lo que dejaste en diciembre",
         dos="Sigue esperándote", foto=""),

    dict(uno="Un mes seguido se nota poco",
         dos="Un año seguido lo cambia todo", foto=""),

    dict(uno="No entrenas para el espejo",
         dos="Entrenas para los ochenta", foto=""),

    dict(uno="La motivación se acaba", dos="El horario no", foto=""),

    # --- Febrero 2027 ---------------------------------------------------
    # En Chile febrero es vacaciones y calor. Nadie deja de entrenar del
    # todo: cambia de horario o se va una semana. Las frases hablan de eso
    # y no de propositos, que ya pasaron.
    dict(uno="Febrero es el mes de la verdad",
         dos="El que sigue en marzo, entrena", foto=""),

    dict(uno="No dejaste de venir",
         dos="Solo cambiaste de horario", foto=""),

    dict(uno="El calor no es la excusa",
         dos="Es un vaso de agua más", foto=""),

    dict(uno="La rutina aburre", dos="Los resultados no", foto=""),

    dict(uno="Nadie te va a preguntar",
         dos="Si viniste con ganas", foto=""),

    dict(uno="Se puede entrenar de vacaciones",
         dos="O volver el lunes", foto=""),

    dict(uno="Dos meses no son nada", dos="Y ya llevas dos", foto=""),

    dict(uno="El cuerpo no cuenta los días",
         dos="Cuenta las veces", foto=""),

    # --- Marzo 2027 -----------------------------------------------------
    # Marzo es el enero de verdad en Chile: vuelve el colegio, vuelve el
    # trabajo y vuelve la rutina. Es el mes con mas intencion de empezar de
    # todo el año.
    dict(uno="Marzo empieza de verdad",
         dos="Los propósitos ya se fueron", foto=""),

    dict(uno="Vuelve la rutina", dos="Y eso es lo bueno", foto=""),

    dict(uno="No entrenas más", dos="Entrenas siempre", foto=""),

    dict(uno="El que quedó en enero", dos="Ya no está", foto=""),

    dict(uno="Marzo pesa", dos="Por eso cuenta doble", foto=""),

    dict(uno="Se acabó el verano", dos="No la constancia", foto=""),

    dict(uno="Ningún mes es fácil", dos="Ninguno es imposible", foto=""),

    dict(uno="Volver no es empezar", dos="Es continuar", foto=""),

    dict(uno="Un año se hace en marzo", dos="No en enero", foto=""),

    # --- Abril a diciembre de 2027 --------------------------------------
    # Un martes por semana, 39 en total, para que el feed no se apague el
    # 29 de marzo. Todas sin foto: las cuatro fotos utiles de la sala ya
    # estan gastadas y este formato no necesita ninguna.
    #
    # `estilo` rota entre las cuatro composiciones para que dos semanas
    # seguidas no se vean iguales en la cuadricula del perfil.
    #
    # Chile: otono marzo-mayo, invierno junio-agosto, primavera
    # septiembre-noviembre. Las frases van pegadas a esa estacion, no a la
    # del hemisferio norte.
    dict(uno="Se acabó el verano", dos="Empieza lo que dura", foto="", estilo=""),
    dict(uno="Abril no promete nada", dos="Por eso funciona", foto="", estilo="marco"),
    dict(uno="Ya no es empezar", dos="Ahora es seguir", foto="", estilo="linea"),
    dict(uno="Con frío cuesta salir", dos="Adentro se está bien", foto="", estilo="alto"),
    dict(uno="Los días se acortan", dos="La hora sigue ahí", foto="", estilo=""),
    dict(uno="Nadie entrena con ganas siempre", dos="Se entrena igual", foto="", estilo="marco"),
    dict(uno="Mayo no se ve en el espejo", dos="Se ve en agosto", foto="", estilo="linea"),
    dict(uno="Lo difícil no es la serie", dos="Es salir de la casa", foto="", estilo="alto"),
    dict(uno="Empieza el invierno", dos="No la pausa", foto="", estilo=""),
    dict(uno="Junio parte el año en dos", dos="Mira para qué lado vas", foto="", estilo="marco"),
    dict(uno="La mitad del año", dos="Y sigues aquí", foto="", estilo="linea"),
    dict(uno="El día más corto del año", dos="Cabe igual una hora", foto="", estilo="alto"),
    dict(uno="Nadie ve lo que haces en junio", dos="Se nota en diciembre", foto="", estilo=""),
    dict(uno="Vacaciones de invierno", dos="El horario se mueve, no se borra", foto="", estilo="marco"),
    dict(uno="Si te vas dos semanas", dos="Vuelves a la tercera", foto="", estilo="linea"),
    dict(uno="Frío afuera", dos="Pesas adentro", foto="", estilo="alto"),
    dict(uno="Julio se pasa rápido", dos="Agosto también", foto="", estilo=""),
    dict(uno="Agosto es el último frío", dos="Después viene lo bueno", foto="", estilo="marco"),
    dict(uno="Falta poco para la primavera", dos="Empieza ahora, no en septiembre", foto="", estilo="linea"),
    dict(uno="El cuerpo no sabe que es agosto", dos="Solo sabe si viniste", foto="", estilo="alto"),
    dict(uno="Lo que empieces hoy", dos="Se nota en noviembre", foto="", estilo=""),
    dict(uno="Se acaba el invierno", dos="Y tú no paraste", foto="", estilo="marco"),
    dict(uno="Septiembre llega con todo", dos="La rutina aguanta", foto="", estilo="linea"),
    dict(uno="Vienen las fiestas", dos="Y después el lunes", foto="", estilo="alto"),
    dict(uno="Nadie entrena el 18", dos="Todos vuelven el 20", foto="", estilo=""),
    dict(uno="Empieza la primavera", dos="Y el verano se prepara ahora", foto="", estilo="marco"),
    dict(uno="Octubre es el mes justo", dos="Ni tarde ni temprano", foto="", estilo="linea"),
    dict(uno="El verano no se improvisa", dos="Octubre es el momento", foto="", estilo="alto"),
    dict(uno="Quedan meses de sobra", dos="Si empiezas hoy", foto="", estilo=""),
    dict(uno="Se viene el calor", dos="Y tú vienes preparado", foto="", estilo="marco"),
    dict(uno="Ya no falta nada", dos="Y tú llevas meses", foto="", estilo="linea"),
    dict(uno="Ya se siente el verano", dos="Ya se nota el trabajo", foto="", estilo="alto"),
    dict(uno="No empieces en enero", dos="Enero ya viene tarde", foto="", estilo=""),
    dict(uno="Un mes y medio", dos="Da para mucho", foto="", estilo="marco"),
    dict(uno="Diciembre está ahí", dos="Llega entrenando", foto="", estilo="linea"),
    dict(uno="Fin de año es ruido", dos="La hora sigue siendo tuya", foto="", estilo="alto"),
    dict(uno="Entre asado y asado", dos="Cabe una hora", foto="", estilo=""),
    dict(uno="El 25 se come", dos="El 26 se vuelve", foto="", estilo="marco"),
    dict(uno="El año se acaba", dos="La costumbre no", foto="", estilo="linea"),
]


def serifa(tam, negrita=True):
    for ruta in SERIFAS_BOLD:
        if os.path.exists(ruta):
            return ImageFont.truetype(ruta, tam)
    raise SystemExit("No se encontro ninguna tipografia con serifa.")


def papel():
    """El fondo. Un grano muy fino, que es lo que separa esto de un PNG
    plano y le da el aire de hoja impresa que tiene la referencia."""
    im = Image.new("RGB", (W, H), PAPEL)
    ruido = Image.new("L", (W // 2, H // 2))
    al = random.Random(19)
    ruido.putdata([128 + al.randint(-16, 16) for _ in range(ruido.width * ruido.height)])
    ruido = ruido.resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(0.6))
    gris = Image.new("RGB", (W, H), (255, 255, 255))
    return Image.blend(im, Image.composite(im, gris, ruido), 0.35)


def partir(d, texto, fuente, ancho):
    lineas, actual = [], ""
    for p in texto.split():
        prueba = (actual + " " + p).strip()
        if d.textlength(prueba, font=fuente) <= ancho:
            actual = prueba
        else:
            if actual:
                lineas.append(actual)
            actual = p
    if actual:
        lineas.append(actual)
    return lineas


def trazo(d, x1, x2, y, color, grosor=7, semilla=0, desvio=3):
    """Un subrayado que no es una recta: tres segmentos con un pelo de
    desvio y grosor variable. A mano alzada, como en la referencia.

    `desvio` se baja para los trazos cortos. Los 3 px de un subrayado de
    800 px se leen como pulso; los mismos 3 px en un separador de 200 px
    se leen como una linea rota."""
    al = random.Random(semilla)
    n = 3
    px, py = x1, y
    for i in range(1, n + 1):
        nx = x1 + (x2 - x1) * i / float(n)
        ny = y + al.randint(-desvio, desvio)
        d.line([(px, py), (nx, ny)], fill=color + (235,),
               width=max(3, grosor + al.randint(-2, 2)))
        px, py = nx, ny


def filete(d, semilla):
    """El marco de la variante «marco». Cuatro trazos sueltos, uno por
    lado, con el mismo desvio que el subrayado. No se cierran en las
    esquinas a proposito: un rectangulo perfecto delata la maquina."""
    m = int(M * 0.55)
    # El lado de abajo NO va a la misma distancia que el de arriba: la
    # firma vive en H - 78 y el marco le pasaba por encima, tachandola.
    # Los dos formatos comparten firma, asi que un solo numero sirve.
    abajo = H - 132
    trazo(d, m, W - m, m, TINTA, grosor=4, semilla=semilla + 11)
    trazo(d, m, W - m, abajo, TINTA, grosor=4, semilla=semilla + 12)
    for x, sem in ((m, semilla + 13), (W - m, semilla + 14)):
        al = random.Random(sem)
        py = m
        for i in range(1, 4):
            ny = m + (abajo - m) * i / 3.0
            d.line([(x + al.randint(-3, 3), py), (x + al.randint(-3, 3), ny)],
                   fill=TINTA + (235,), width=4)
            py = ny


def resaltar(d, x1, x2, y1, y2, color):
    """El resaltador: una banda translucida con los bordes desiguales."""
    d.rounded_rectangle([x1 - 8, y1, x2 + 8, y2], radius=6,
                        fill=color + (140,))


def bloque(im, d, texto, y, tam, color_trazo, semilla, resalta=False):
    """Escribe el texto centrado y le pone su marca de color. Devuelve la
    y por debajo de lo escrito."""
    ft = serifa(tam)
    lineas = partir(d, texto, ft, W - 2 * M)
    alto = int(tam * 1.34)
    for i, ln in enumerate(lineas):
        ancho = d.textlength(ln, font=ft)
        x = (W - ancho) / 2
        yy = y + i * alto

        # La marca va SOLO en la ultima linea, como en la referencia: si
        # se subraya todo, deja de ser un enfasis y pasa a ser decoracion.
        if i == len(lineas) - 1:
            if resalta:
                resaltar(d, x, x + ancho, yy + tam * 0.18, yy + tam * 1.02,
                         color_trazo)
            else:
                trazo(d, x, x + ancho, yy + tam * 1.16, color_trazo,
                      semilla=semilla)

        d.text((x, yy), ln, font=ft, fill=TINTA + (255,), anchor="la")
    return y + alto * len(lineas)


def foto_en(im, ruta, y, alto):
    f = Image.open(ruta).convert("RGB")
    ancho = W - 2 * M
    escala = max(ancho / f.width, alto / f.height)
    f = f.resize((int(f.width * escala), int(f.height * escala)), Image.LANCZOS)
    izq = (f.width - ancho) // 2
    arr = (f.height - alto) // 2
    f = f.crop((izq, arr, izq + ancho, arr + alto))
    im.paste(f, (M, y))


def marca(d):
    ft = serifa(30)
    d.text((W / 2, H - 78), "ULTRA-SPORT 19", font=ft,
           fill=(120, 116, 110, 255), anchor="ma")


def alto_de(d, texto, tam):
    """Cuanto ocupa un bloque de texto. Hace falta ANTES de dibujar para
    poder centrar el conjunto: la primera version dejaba la mitad de abajo
    vacia y la pieza se veia caida."""
    ft = serifa(tam)
    return len(partir(d, texto, ft, W - 2 * M)) * int(tam * 1.34)


def pieza(p, semilla):
    im = papel()
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)

    tam = 62 if len(p["uno"]) > 32 or len(p["dos"]) > 32 else 72

    a1 = alto_de(d, p["uno"], tam)
    a2 = alto_de(d, p["dos"], tam)

    if p["foto"]:
        alto_foto = int(H * 0.32)
        hueco = 70
        total = a1 + hueco + alto_foto + hueco + a2
        y = (H - total) / 2 - H * 0.03      # un pelo por encima del centro
        bloque(im, d, p["uno"], y, tam, ROJO, semilla)
        y_foto = int(y + a1 + hueco)
        bloque(im, d, p["dos"], y_foto + alto_foto + hueco, tam, VERDE,
               semilla + 1)
        # La foto va DEBAJO de la capa de texto, asi que se pega antes de
        # componer: si se pegara despues, taparia los subrayados.
        foto_en(im, os.path.join(IMG, p["foto"]), y_foto, alto_foto)
    elif p.get("estilo") == "marco":
        # Un filete en el margen, con el mismo pulso tembloroso del
        # subrayado. Encierra la pieza sin cerrarla: los cuatro lados se
        # dibujan por separado y las esquinas no llegan a tocarse.
        hueco = 130
        total = a1 + hueco + a2
        y = (H - total) / 2 - H * 0.02
        filete(d, semilla)
        bloque(im, d, p["uno"], y, tam, VERDE, semilla, resalta=True)
        bloque(im, d, p["dos"], y + a1 + hueco, tam, ROJO, semilla + 1)
    elif p.get("estilo") == "linea":
        # Un filete corto entre las dos frases. Es el gesto de separador
        # de un libro, y hace el trabajo que Diego no quiere que haga un
        # punto ni un simbolo.
        hueco = 150
        total = a1 + hueco + a2
        y = (H - total) / 2 - H * 0.02
        bloque(im, d, p["uno"], y, tam, AZUL, semilla)
        medio = int(y + a1 + hueco / 2)
        trazo(d, W * 0.36, W * 0.64, medio, TINTA, grosor=5,
              semilla=semilla + 5, desvio=1)
        bloque(im, d, p["dos"], y + a1 + hueco, tam, AMARILLO, semilla + 1,
               resalta=True)
    elif p.get("estilo") == "alto":
        # El bloque subido y todo el aire abajo. En el feed 4:5 es donde
        # mas se nota, porque la cuadricula del perfil recorta por abajo.
        hueco = 130
        y = H * 0.24
        bloque(im, d, p["uno"], y, tam, ROJO, semilla)
        bloque(im, d, p["dos"], y + a1 + hueco, tam, VERDE, semilla + 1)
    else:
        hueco = 130
        total = a1 + hueco + a2
        y = (H - total) / 2 - H * 0.02
        bloque(im, d, p["uno"], y, tam, AMARILLO, semilla, resalta=True)
        bloque(im, d, p["dos"], y + a1 + hueco, tam, AZUL, semilla + 1)

    marca(d)
    return Image.alpha_composite(im.convert("RGBA"), capa).convert("RGB")


def main():
    global W, H
    for nombre_f, ancho, alto in FORMATOS:
        W, H = ancho, alto
        carpeta = os.path.join(SALIDA, nombre_f)
        os.makedirs(carpeta, exist_ok=True)
        for viejo in os.listdir(carpeta):
            if viejo.lower().endswith(".png"):
                os.remove(os.path.join(carpeta, viejo))
        print("  " + nombre_f + "  " + str(W) + "x" + str(H))
        for i, p in enumerate(PIEZAS, 1):
            if p["foto"] and not os.path.exists(os.path.join(IMG, p["foto"])):
                print("    falta " + p["foto"] + ", se salta")
                continue
            nom = "US19_TIPO_%02d.png" % i
            pieza(p, i * 7).save(os.path.join(carpeta, nom), "PNG")
            print("    " + nom + "  " + p["uno"] + " / " + p["dos"])
    print("")
    print("  BORRADOR en " + SALIDA + " (no se programo nada)")


if __name__ == "__main__":
    main()
