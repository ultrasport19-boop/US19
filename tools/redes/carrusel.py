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

W, H = 1080, 1350          # 4:5 — el unico vertical que acepta el feed
MITAD = H // 2
M = 72

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


def lamina(idx, frase, antes, despues, maqueta, img_antes=None, img_despues=None):
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
    frase_en(d, frase, MITAD // 2, W - 2 * M)
    frase_en(d, frase, MITAD + MITAD // 2, W - 2 * M)

    marca(d, H - 62)
    fp = f("Barlow-Bold.ttf", 26)
    pie = str(idx) + "/5"
    d.text((W - M, H - 56), pie, font=fp, fill=(255, 255, 255, 170), anchor="ra")

    return im


# =========================================================================
#  LOS TEXTOS. Cambiar aqui, no en el dibujo.
#  Cada entrada: la frase que se repite, y que se ve en cada mitad.
# =========================================================================
LAMINAS = [
    dict(frase="No tengo tiempo.",
         antes="La excusa: sentado, agotado, mirando el telefono.",
         despues="La prioridad: la hora reservada y aparecer.",
         img_antes="antes.jpg", img_despues="despues.jpg"),

    dict(frase="Me esta costando.",
         antes="Suena a queja, a mitad de la serie.",
         despues="Suena a orgullo: cuesta porque estas subiendo.",
         img_antes="antes.jpg", img_despues="despues.jpg"),

    dict(frase="Solo llevo una semana.",
         antes="Impaciencia, comparandose con el de al lado.",
         despues="Una semana mas que quien no empezo.",
         img_antes="antes.jpg", img_despues="despues.jpg"),

    dict(frase="Hoy no tenia ganas.",
         antes="La razon para no ir.",
         despues="Y fue igual. Eso es lo que lo cambia todo.",
         img_antes="antes.jpg", img_despues="despues.jpg"),

    dict(frase="Voy lento.",
         antes="Verguenza, ultimo del grupo.",
         despues="Lento sigue siendo hacia adelante.",
         img_antes="antes.jpg", img_despues="despues.jpg"),
]


def main():
    for carpeta in ("maqueta", "final"):
        os.makedirs(os.path.join(SALIDA, carpeta), exist_ok=True)

    print("US19 · carrusel «la misma frase, otra persona»  " + str(W) + "x" + str(H))
    print("")
    for i, p in enumerate(LAMINAS, 1):
        for carpeta, maq in (("maqueta", True), ("final", False)):
            im = lamina(i, p["frase"], p["antes"], p["despues"], maq,
                        p.get("img_antes"), p.get("img_despues"))
            nom = "US19C_%02d_%s.png" % (i, p["frase"].lower()
                                         .replace(" ", "-").replace(".", "")
                                         .replace("á", "a").replace("é", "e")
                                         .replace("í", "i").replace("ó", "o")
                                         .replace("ú", "u"))
            ruta = os.path.join(SALIDA, carpeta, nom)
            im.save(ruta, "PNG")
        print("  %d/5  «%s»" % (i, p["frase"]))

    print("")
    print("  maqueta -> " + os.path.join(SALIDA, "maqueta") + "   (con guias y que va en cada hueco)")
    print("  final   -> " + os.path.join(SALIDA, "final") + "   (limpio, para montar la ilustracion)")
    print("")
    print("  Cada hueco de ilustracion mide " + str(W - M) + "x" + str(MITAD - M) + " px.")


if __name__ == "__main__":
    main()
