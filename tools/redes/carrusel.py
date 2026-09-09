# -*- coding: utf-8 -*-
"""US19 · carrusel de feed 1080x1350 — «la misma frase, otra persona».

    python tools/redes/carrusel.py

QUE ES
Cada lamina se parte en dos mitades con LA MISMA FRASE escrita en las dos.
Arriba, quien la dice al empezar; abajo, quien la dice meses despues. No
cambia la frase: cambia quien la dice. El formato viene de una referencia
que Diego trajo el 9-sep-2026 (un carrusel de 5 con 40.000 me gusta).

POR QUE NO ESTA DENTRO DE historias.py
Aquel hace 1080x1920, que es SOLO historia: el feed de Instagram admite
entre 4:5 y 1.91:1 y rechaza la vertical 9:16. Esto es 1080x1350 (4:5),
que si entra en el feed y en el muro de Facebook. Y su estructura es otra
—dos mitades espejo, sin modulo ni bloque de contacto en cada lamina—, asi
que meterlo alli habria sido llenar de condicionales un archivo que hoy
funciona. Comparten las fuentes y los colores, que es lo que importa.

LAS IMAGENES NO LAS PONE ESTE SCRIPT
Deja el hueco de cada mitad y, en modo maqueta, lo marca con su tamano
exacto para saber que encargar. Se generan dos juegos:
  salida_carrusel/maqueta/  con las guias, para trabajar
  salida_carrusel/final/    sin guias, listo para montar la ilustracion

OJO CON LOS DERECHOS
Los personajes de la referencia (One Piece, y el arte de otra cuenta) son
de otros. Esto esta pensado para ilustracion propia o encargada. El
tratamiento —dos tonos planos sobre el rojo de la marca— es lo que hace el
estilo, no el personaje.

REGLAS DE TEXTO, las mismas de piezas.py: nada clinico, ninguna cifra sin
confirmar, ninguna promesa de resultado.
"""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
FUENTES = os.path.join(BASE, "fuentes")
SALIDA = os.path.join(BASE, "salida_carrusel")
IMG = os.path.abspath(os.path.join(BASE, "..", "..", "img"))
LOGO = os.path.join(IMG, "logo.png")
# Un nombre suelto en `img_antes` se busca aqui; una ruta absoluta se usa
# tal cual, que es como entran las ilustraciones que no viven en el repo.
FOTOS = IMG
# Las ilustraciones del carrusel: NO se versionan (van en .gitignore).
# El repo de las paginas es publico y este material es de terceros.
ILUS = os.path.join(BASE, "fuentes_img")

# Dos formatos con el mismo diseno:
#   feed 1080x1350 (4:5) — el unico vertical que acepta el feed de Instagram
#   historia 1080x1920 (9:16) — el que rechaza el feed y pide la historia
# W, H y MITAD se reasignan antes de cada tanda; el resto del dibujo los lee.
FORMATOS = [("feed", 1080, 1350), ("historia", 1080, 1920)]
W, H = 1080, 1350
MITAD = H // 2
M = 72
# El contador «N/5» de la esquina: solo en historia. Ver lamina().
CONTADOR = True

ROJO = (226, 28, 37)
ROJO_OSCURO = (150, 16, 22)
BLANCO = (255, 255, 255)
DORADO = (247, 181, 56)
NEGRO = (11, 11, 12)
GUIA = (255, 255, 255, 60)


def f(n, t):
    return ImageFont.truetype(os.path.join(FUENTES, n), t)


def partir(d, texto, fnt, max_w):
    """Parte en lineas que quepan. Devuelve la lista."""
    lineas, act = [], ""
    for p in texto.split():
        prueba = (act + " " + p).strip()
        if d.textlength(prueba, font=fnt) <= max_w or not act:
            act = prueba
        else:
            lineas.append(act)
            act = p
    if act:
        lineas.append(act)
    return lineas


def frase_en(d, texto, y_centro, ancho, tam_inicial=86):
    """Escribe la frase centrada, encogiendo hasta que quepa en dos lineas.

    Anton necesita interlineado 1.08: con menos, las tildes se pisan con la
    linea de arriba. Es la misma trampa que ya estaba pagada en historias.py.
    """
    tam = tam_inicial
    while tam > 40:
        fnt = f("Anton.ttf", tam)
        lineas = partir(d, texto, fnt, ancho)
        if len(lineas) <= 2:
            break
        tam -= 4
    fnt = f("Anton.ttf", tam)
    lineas = partir(d, texto, fnt, ancho)
    alto_linea = int(tam * 1.08)
    y = y_centro - (alto_linea * len(lineas)) // 2
    for ln in lineas:
        x = (W - d.textlength(ln, font=fnt)) / 2
        # Sombra: sobre una ilustracion cualquiera el blanco solo no se lee.
        d.text((x + 3, y + 3), ln, font=fnt, fill=(0, 0, 0, 150), anchor="la")
        d.text((x, y), ln, font=fnt, fill=BLANCO, anchor="la")
        y += alto_linea
    return tam


def marca(d, y):
    fnt = f("Anton.ttf", 34)
    txt = "ULTRA-SPORT "
    x = M
    d.text((x, y), txt, font=fnt, fill=BLANCO, anchor="la")
    x += d.textlength(txt, font=fnt)
    # El «19» va en el color de acento: en rojo sobre rojo desaparecia y la
    # marca se quedaba en «ULTRA-SPORT». Misma trampa que en historias.py.
    d.text((x, y), "19", font=fnt, fill=DORADO, anchor="la")


def montar(im, ruta, y0, y1, velo):
    """Encaja una imagen en la mitad que le toca, recortando por el centro.

    El velo oscuro no es decoracion: el titular va en blanco y sobre una foto
    clara desaparece. Es la misma razon por la que la piel «foto» de
    historias.py lleva degradado.
    """
    if not ruta:
        return False
    if os.path.isabs(ruta):
        p = ruta
    else:
        p = os.path.join(ILUS, ruta)
        if not os.path.exists(p):
            p = os.path.join(FOTOS, ruta)
    if not os.path.exists(p):
        print("    (no encuentro " + ruta + ", ese hueco queda liso)")
        return False

    alto = y1 - y0
    src = Image.open(p).convert("RGB")
    # Recorte por el centro al aspecto del hueco: deformar una foto de la
    # sala se nota enseguida en las lineas rectas del techo.
    escala = max(W / src.width, alto / src.height)
    nueva = src.resize((max(1, int(src.width * escala)), max(1, int(src.height * escala))))
    izq = (nueva.width - W) // 2
    arr = (nueva.height - alto) // 2
    im.paste(nueva.crop((izq, arr, izq + W, arr + alto)), (0, y0))

    if velo:
        capa = Image.new("RGBA", (W, alto), (0, 0, 0, velo))
        im.paste(Image.alpha_composite(
            im.crop((0, y0, W, y1)).convert("RGBA"), capa).convert("RGB"), (0, y0))
    return True


def lamina(idx, frase, antes, despues, maqueta, img_antes=None,
           img_despues=None, frase2=None):
    im = Image.new("RGB", (W, H), ROJO)
    d = ImageDraw.Draw(im, "RGBA")

    # La mitad de abajo, un punto mas oscura: separa las dos escenas sin
    # necesidad de una linea, que ensuciaria el montaje de la ilustracion.
    d.rectangle([0, MITAD, W, H], fill=ROJO_OSCURO)

    if not maqueta:
        # Arriba mas apagado y abajo mas limpio: quien empieza y quien ya
        # lleva tiempo. El contraste cuenta la historia sin decirla.
        montar(im, img_antes, 0, MITAD, 150)
        montar(im, img_despues, MITAD, H, 90)
        d = ImageDraw.Draw(im, "RGBA")

    if maqueta:
        for (y0, y1, etiqueta) in ((0, MITAD, antes), (MITAD, H, despues)):
            d.rectangle([M // 2, y0 + M // 2, W - M // 2, y1 - M // 2],
                        outline=GUIA, width=3)
            ft = f("Barlow-Bold.ttf", 26)
            d.text((M, y0 + M // 2 + 18), "ILUSTRACION " + str(W - M) + "x" + str(MITAD - M),
                   font=ft, fill=(255, 255, 255, 140), anchor="la")
            fd = f("Barlow-Regular.ttf", 30)
            for i, ln in enumerate(partir(d, etiqueta, fd, W - 2 * M)):
                d.text((M, y0 + M // 2 + 60 + i * 38), ln, font=fd,
                       fill=(255, 255, 255, 170), anchor="la")

    # La MISMA frase en las dos mitades: es todo el chiste del formato.
    # Con `frase2` las dos mitades dicen cosas DISTINTAS: arriba lo que
    # nadie te exige y abajo lo minimo que si. Es el formato que Diego
    # trajo de @vulcanuzxz el 9-sep-2026, y usa exactamente esta misma
    # geometria. Sin `frase2` se repite la frase arriba y abajo, que es
    # el chiste del formato original.
    frase_en(d, frase, MITAD // 2, W - 2 * M)
    frase_en(d, frase2 or frase, MITAD + MITAD // 2, W - 2 * M)

    marca(d, H - 62)
    # El «N/5» solo dice la verdad cuando las cinco laminas se ven
    # seguidas, que es lo que pasa en historias. En el feed cada una se
    # publica SOLA —MODULO_POST sube files[0], una imagen por fila, no
    # hay carrusel—, asi que ahi el numero promete cuatro piezas que
    # nadie va a poder deslizar.
    if CONTADOR:
        fp = f("Barlow-Bold.ttf", 26)
        pie = str(idx) + "/5"
        d.text((W - M, H - 56), pie, font=fp, fill=(255, 255, 255, 170), anchor="ra")

    return im


# =========================================================================
#  LOS TEXTOS. Cambiar aqui, no en el dibujo.
#  Cada entrada: la frase que se repite, y que se ve en cada mitad.
# =========================================================================
LAMINAS = [
    dict(frase="Me subió el peso.",
         antes="La báscula. Cara de derrota.",
         despues="La barra. La misma frase, otra cosa.",
         img_antes="antes.jpg", img_despues="despues.jpg"),

    dict(frase="Mañana toca pierna.",
         antes="Pánico. Ya duele solo de pensarlo.",
         despues="Ganas. Es el día bueno de la semana.",
         img_antes="antes.jpg", img_despues="despues.jpg"),

    dict(frase="No puedo más.",
         antes="Rendirse en la serie tres.",
         despues="La última repetición, la que cuenta.",
         img_antes="antes.jpg", img_despues="despues.jpg"),

    dict(frase="Me duele todo.",
         antes="Queja del día siguiente.",
         despues="Medalla del día siguiente.",
         img_antes="antes.jpg", img_despues="despues.jpg"),

    dict(frase="Otra vez aquí.",
         antes="Suena a condena.",
         despues="Suena a casa.",
         img_antes="antes.jpg", img_despues="despues.jpg"),
]


# Segunda tanda, con el otro par de caras. Mismo formato: la misma frase
# dicha desde el agotamiento y desde la satisfaccion. Aqui el «antes» esta
# sentado y reventado, asi que las frases van del esfuerzo y no del miedo.
LAMINAS_B = [
    dict(frase="Terminé la rutina.",
         antes="Reventado, sentado, sin aire.",
         despues="Orgulloso. La misma frase, otro dia.",
         img_antes="antes_goku.jpg", img_despues="despues_goku.jpg"),

    dict(frase="No siento las piernas.",
         antes="Justo después del día de pierna.",
         despues="Y volvería a hacerlo mañana.",
         img_antes="antes_goku.jpg", img_despues="despues_goku.jpg"),

    dict(frase="Me falta la última serie.",
         antes="Agonía. Falta una y pesa como diez.",
         despues="Recta final. Falta una y ya está.",
         img_antes="antes_goku.jpg", img_despues="despues_goku.jpg"),

    dict(frase="Llevo tres meses viniendo.",
         antes="Dicho con cansancio.",
         despues="Dicho como lo que es: una racha.",
         img_antes="antes_goku.jpg", img_despues="despues_goku.jpg"),

    dict(frase="Hoy vine solo.",
         antes="Nadie me acompañó.",
         despues="No necesité que nadie me acompañara.",
         img_antes="antes_goku.jpg", img_despues="despues_goku.jpg"),
]


# Tercera tanda: alterna los dos pares de caras dentro de la misma serie,
# para que cinco historias seguidas no sean siempre el mismo personaje.
LAMINAS_C = [
    dict(frase="Hoy es día de descanso.",
         antes="Dicho con culpa, como si fuera hacer trampa.",
         despues="Dicho como lo que es: parte del plan.",
         img_antes="antes.jpg", img_despues="despues.jpg"),

    dict(frase="Mañana empiezo.",
         antes="La promesa de siempre.",
         despues="Y esta vez fue verdad.",
         img_antes="antes_goku.jpg", img_despues="despues_goku.jpg"),

    dict(frase="Solo vengo a cardio.",
         antes="La excusa para no tocar una pesa.",
         despues="La decisión de quien ya sabe qué le sirve.",
         img_antes="antes.jpg", img_despues="despues.jpg"),

    dict(frase="Me falta técnica.",
         antes="Vergüenza. Por eso no se acerca a la barra.",
         despues="Lo dice quien ya progresó lo suficiente para notarlo.",
         img_antes="antes_goku.jpg", img_despues="despues_goku.jpg"),

    dict(frase="Vine a las seis de la mañana.",
         antes="Sacrificio, con cara de sueño.",
         despues="Privilegio: el gimnasio entero para ti.",
         img_antes="antes.jpg", img_despues="despues.jpg"),
]


# Cuarta y quinta tanda: los dos formatos de @vulcanuzxz, con frase
# distinta arriba y abajo. Van al FEED de noviembre y diciembre, que es
# el hueco real del calendario: en esos dos meses hay 50 y 47 historias
# programadas pero solo 1 y 0 publicaciones de feed.
#
# Sin puntos al final, por la regla de Diego del 9-sep-2026. La
# referencia los lleva; aqui no.
LAMINAS_D = [
    dict(frase="No tienes que esperar a enero",
         frase2="Empieza esta semana",
         antes="El proposito de siempre.",
         despues="El dia que fue verdad.",
         img_antes="antes.jpg", img_despues="despues.jpg"),

    dict(frase="No tienes que entrenar todos los dias",
         frase2="Empieza con dos a la semana",
         antes="La exigencia imposible.",
         despues="Lo que si se sostiene.",
         img_antes="antes_goku.jpg", img_despues="despues_goku.jpg"),

    dict(frase="No tienes que llegar en forma",
         frase2="Empieza como estas",
         antes="La excusa mas repetida.",
         despues="Esa parte es la que se entrena.",
         img_antes="seiya_pegaso.jpg", img_despues="seiya_brazos.jpg"),

    dict(frase="No tienes que levantar pesado",
         frase2="Empieza con la barra sola",
         antes="El miedo a la sala de pesas.",
         despues="Por donde empieza todo el mundo.",
         img_antes="thorfinn.jpg", img_despues="armadura_dorada.jpg"),
]

LAMINAS_E = [
    dict(frase="El precio de la fuerza",
         frase2="Es aparecer",
         antes="Lo que todos quieren.",
         despues="Lo que casi nadie hace.",
         img_antes="antes_goku.jpg", img_despues="despues.jpg"),

    dict(frase="El precio del progreso",
         frase2="Es la constancia",
         antes="El resultado.",
         despues="Lo que cuesta de verdad.",
         img_antes="thorfinn.jpg", img_despues="seiya_brazos.jpg"),

    dict(frase="El precio de sentirte bien",
         frase2="Es empezar",
         antes="La meta.",
         despues="El unico paso que falta.",
         img_antes="antes.jpg", img_despues="despues_goku.jpg"),

    dict(frase="El precio de un cuerpo fuerte",
         frase2="Es el trabajo de todas las semanas",
         antes="Lo que se admira.",
         despues="Lo que nadie ve.",
         img_antes="caballeros_perfil.jpg",
         img_despues="armadura_dorada.jpg"),
]


TANDAS = [("US19C", LAMINAS), ("US19D", LAMINAS_B), ("US19E", LAMINAS_C),
          ("US19F", LAMINAS_D), ("US19G", LAMINAS_E)]


def main():
    global W, H, MITAD, CONTADOR
    # Se vacia antes de generar: si no, al cambiar una frase queda el PNG
    # viejo al lado del nuevo y acabas subiendo la tanda equivocada.
    carpetas = [f + "_" + c for (f, _, _) in FORMATOS for c in ("maqueta", "final")]
    for carpeta in carpetas:
        ruta = os.path.join(SALIDA, carpeta)
        os.makedirs(ruta, exist_ok=True)
        for viejo in os.listdir(ruta):
            if viejo.lower().endswith(".png"):
                os.remove(os.path.join(ruta, viejo))

    print("US19 · «la misma frase, otra persona»")
    print("")
    for nombre_f, ancho, alto in FORMATOS:
      W, H = ancho, alto
      MITAD = H // 2
      CONTADOR = (nombre_f != "feed")
      print("  " + nombre_f + "  " + str(W) + "x" + str(H))
      for prefijo, laminas in TANDAS:
       for i, p in enumerate(laminas, 1):
        for sufijo, maq in (("maqueta", True), ("final", False)):
            carpeta = nombre_f + "_" + sufijo
            im = lamina(i, p["frase"], p["antes"], p["despues"], maq,
                        p.get("img_antes"), p.get("img_despues"),
                        p.get("frase2"))
            nom = prefijo + "_%02d_%s.png" % (i, p["frase"].lower()
                                         .replace(" ", "-").replace(".", "")
                                         .replace("á", "a").replace("é", "e")
                                         .replace("í", "i").replace("ó", "o")
                                         .replace("ú", "u")
                                         .replace("ñ", "n"))
            ruta = os.path.join(SALIDA, carpeta, nom)
            im.save(ruta, "PNG")
       print("    " + prefijo + ": " + str(len(laminas)) + " laminas")

    print("")
    print("  Todo en " + SALIDA)
    print("  <formato>_final    limpio, para publicar")
    print("  <formato>_maqueta  con guias, para encargar la ilustracion")


if __name__ == "__main__":
    main()
