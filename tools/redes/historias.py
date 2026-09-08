# -*- coding: utf-8 -*-
"""US19 · generador de historias 1080x1920.

Cuatro pieles sobre la misma estructura: marca arriba, antetitulo, titular
en Anton con una linea de acento, cuerpo, un modulo y el bloque de
contacto. Los textos viven en piezas.py, aparte del dibujo.

    python historias.py

Trampas ya pagadas (no deshacer sin mirar el PNG resultante):
  · Anton necesita interlineado 1.08. Con menos, las tildes de N e I se
    pisan con la linea de arriba.
  · El «19» de la marca va en el color de acento de la piel. En rojo sobre
    rojo desaparecia y la marca se quedaba en «ULTRA-SPORT».
  · Un halo pegado con una mascara que toca el borde de su caja deja una
    linea recta: hay que meter la elipse hacia dentro para que el
    desenfoque tenga donde apagarse.
  · Anton a 200 px se comia la linea de abajo; el telefono a 72 px pisaba
    la direccion.
  · Las tipografias NO estan instaladas en Windows. Se bajan a ./fuentes/
    pidiendo el CSS de Google Fonts con user-agent de escritorio, que
    devuelve .ttf: Anton, Barlow 400/700 y Barlow Condensed 700.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = os.path.dirname(os.path.abspath(__file__))
FUENTES = os.path.join(BASE, "fuentes")
SALIDA = os.path.join(BASE, "salida")
# Relativas al propio script, no al directorio desde el que se ejecuta:
# si no, solo funciona haciendo cd a esta carpeta.
IMG = os.path.abspath(os.path.join(BASE, '..', '..', 'img'))
LOGO = os.path.join(IMG, 'logo.png')
FOTOS = IMG

W, H = 1080, 1920
M = 96

ROJO   = (226, 28, 37)
ROJO_C = (255, 90, 96)
NEGRO  = (11, 11, 12)
CARBON = (16, 20, 24)
HUESO  = (244, 242, 238)
GRIS   = (150, 150, 158)
LIMA   = (168, 209, 57)
TEL    = "+56 9 6590 2238"
DIR    = "Hernando Bravo de Villalba 811, Pencahue"


def f(n, t): return ImageFont.truetype(os.path.join(FUENTES, n), t)
def anton(t): return f("Anton.ttf", t)
def barlow(t): return f("Barlow-Regular.ttf", t)
def barlowB(t): return f("Barlow-Bold.ttf", t)
def cond(t): return f("BarlowCondensed-Bold.ttf", t)


def escribir(d, xy, txt, fnt, color, track=0):
    x, y = xy
    if track == 0:
        d.text((x, y), txt, font=fnt, fill=color, anchor="la")
        return d.textlength(txt, font=fnt)
    x0 = x
    for ch in txt:
        d.text((x, y), ch, font=fnt, fill=color, anchor="la")
        x += d.textlength(ch, font=fnt) + track
    return x - x0 - track


def partir(d, texto, fnt, max_w):
    lineas, act = [], ""
    for p in texto.split():
        prueba = (act + " " + p).strip()
        if d.textlength(prueba, font=fnt) <= max_w or not act:
            act = prueba
        else:
            lineas.append(act); act = p
    if act:
        lineas.append(act)
    return lineas


def titular(d, y, lineas, color, color_acento, tam=118, acento=None):
    fnt = anton(tam)
    while max(d.textlength(l, font=fnt) for l in lineas) > W - 2 * M and tam > 40:
        tam -= 4
        fnt = anton(tam)
    ac = acento if isinstance(acento, (list, tuple)) else ([acento] if acento is not None else [])
    paso = int(tam * 1.08)
    for i, l in enumerate(lineas):
        d.text((M, y), l, font=fnt, fill=(color_acento if i in ac else color), anchor="la")
        y += paso
    return y


def resplandor(im, centro, radio, color, fuerza=90):
    capa = Image.new("L", (radio * 2, radio * 2), 0)
    m = radio // 3
    ImageDraw.Draw(capa).ellipse((m, m, radio * 2 - m, radio * 2 - m), fill=fuerza)
    capa = capa.filter(ImageFilter.GaussianBlur(m // 2))
    im.paste(Image.new("RGB", capa.size, color), (centro[0] - radio, centro[1] - radio), capa)


def cabecera(im, d, tinta, acento, sub):
    y = 92
    lg = Image.open(LOGO).convert("RGBA").resize((132, 132), Image.LANCZOS)
    im.paste(lg, (M, y - 22), lg)
    x = M + 158
    w = escribir(d, (x, y + 6), "ULTRA-SPORT ", cond(56), tinta)
    escribir(d, (x + w, y + 6), "19", cond(56), acento)
    escribir(d, (x, y + 66), "PENCAHUE · MAULE", cond(28), sub, track=7)
    return y + 132


def cta(d, tono):
    alto, y0 = 292, H - 292 - 84
    fondo, tinta, sub = {
        "rojo":  (ROJO,  HUESO, (255, 214, 216)),
        "negro": (NEGRO, HUESO, GRIS),
        "hueso": (HUESO, NEGRO, (110, 110, 116)),
    }[tono]
    d.rounded_rectangle((M, y0, W - M, y0 + alto), radius=14, fill=fondo)
    escribir(d, (M + 44, y0 + 44), "ESCRÍBENOS POR WHATSAPP", cond(40), tinta, track=5)
    d.text((M + 44, y0 + 104), TEL, font=anton(76), fill=tinta, anchor="la")
    d.text((M + 44, y0 + 218), DIR, font=barlow(30), fill=sub, anchor="la")


def cuerpo(d, y, texto, color, tam=40, ancho=None):
    fnt = barlow(tam)
    for l in partir(d, texto, fnt, ancho or (W - 2 * M)):
        d.text((M, y), l, font=fnt, fill=color, anchor="la")
        y += int(tam * 1.34)
    return y


PIELES = {
    "papel": dict(fondo=HUESO, tinta=NEGRO, acento=ROJO, eyebrow=ROJO,
                  cuerpo=(70, 70, 76), sub=(120, 120, 126), cta="negro",
                  caja=(232, 229, 223), linea=(200, 196, 189)),
    "rojo":  dict(fondo=ROJO, tinta=HUESO, acento=NEGRO, eyebrow=(255, 205, 207),
                  cuerpo=(255, 222, 224), sub=(255, 190, 193), cta="negro",
                  caja=(198, 22, 30), linea=(255, 150, 154)),
    "foto":  dict(fondo=NEGRO, tinta=HUESO, acento=ROJO_C, eyebrow=ROJO_C,
                  cuerpo=(222, 222, 226), sub=GRIS, cta="rojo",
                  caja=(28, 28, 32), linea=(70, 70, 76)),
    "dato":  dict(fondo=CARBON, tinta=HUESO, acento=LIMA, eyebrow=LIMA,
                  cuerpo=(196, 196, 202), sub=GRIS, cta="rojo",
                  caja=(22, 27, 32), linea=(44, 52, 60)),
}


def fondo_foto(archivo):
    im = Image.open(os.path.join(FOTOS, archivo)).convert("RGB")
    r = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    ox, oy = (im.width - W) // 2, int((im.height - H) * 0.35)
    im = im.crop((ox, oy, ox + W, oy + H))
    grad = Image.new("L", (1, H))
    for y in range(H):
        grad.putpixel((0, y), int(30 + 225 * ((y / H) ** 1.25)))
    im = Image.composite(Image.new("RGB", (W, H), NEGRO), im, grad.resize((W, H)))
    # Un velo arriba (ahi va la marca) y otro abajo (ahi va el titular): una
    # foto con luces no deja leer Anton en blanco por mucho degradado general.
    for caja, fuerza in (((0, 0, W, 420), 185), ((0, 900, W, H), 120)):
        velo = Image.new("L", (W, H), 0)
        ImageDraw.Draw(velo).rectangle(caja, fill=fuerza)
        im = Image.composite(Image.new("RGB", (W, H), NEGRO), im,
                             velo.filter(ImageFilter.GaussianBlur(70)))
    return im


def modulo(d, y, tipo, datos, P):
    if tipo == "lista":
        for t, s in datos:
            d.rectangle((M, y, M + 8, y + 76), fill=P["acento"])
            d.text((M + 30, y + 2), t, font=barlowB(42), fill=P["tinta"], anchor="la")
            d.text((M + 30, y + 50), s, font=barlow(30), fill=P["sub"], anchor="la")
            y += 122
        return y
    if tipo == "semana":
        escribir(d, (M, y), "TU SEMANA", cond(32), P["sub"], track=8)
        y += 56
        lado, hueco = 104, 22
        for i, dia in enumerate("LMMJVSD"):
            x = M + i * (lado + hueco)
            on = i in datos
            d.rounded_rectangle((x, y, x + lado, y + lado), radius=10,
                                fill=P["acento"] if on else None,
                                outline=P["linea"], width=0 if on else 3)
            d.text((x + lado // 2, y + lado + 34), dia, font=cond(38),
                   fill=P["tinta"] if on else P["sub"], anchor="ma")
        return y + lado + 92
    if tipo == "regla":
        d.rectangle((M, y + 10, M + 180, y + 16), fill=P["acento"])
        return y + 60
    if tipo == "cifra":
        num, l1, l2, pie = datos
        d.rounded_rectangle((M, y, W - M, y + 344), radius=16, fill=P["caja"])
        d.text((M + 52, y + 34), num, font=anton(176), fill=P["acento"], anchor="la")
        xt = M + 52 + d.textlength(num, font=anton(176)) + 60
        d.text((xt, y + 74), l1, font=barlowB(52), fill=P["tinta"], anchor="la")
        d.text((xt, y + 138), l2, font=barlowB(52), fill=P["tinta"], anchor="la")
        d.line((M + 52, y + 250, W - M - 52, y + 250), fill=P["linea"], width=2)
        d.text((M + 52, y + 276), pie, font=barlow(32), fill=P["sub"], anchor="la")
        return y + 404
    raise ValueError("modulo desconocido: " + str(tipo))


TOPE_CTA = H - 292 - 84          # donde empieza el bloque de contacto


def alto_modulo(tipo, datos):
    if tipo == "lista":  return 122 * len(datos)
    if tipo == "semana": return 56 + 104 + 92
    if tipo == "regla":  return 60
    if tipo == "cifra":  return 404
    raise ValueError(tipo)


def medir(d, spec, tam):
    """Cuanto ocupa el contenido con ese tamano de titular. Sin esto, un
       titular de cinco lineas se metia DEBAJO del bloque de contacto y el
       telefono quedaba encima del texto."""
    fnt = anton(tam)
    while max(d.textlength(l, font=fnt) for l in spec["titular"]) > W - 2 * M and tam > 40:
        tam -= 4
        fnt = anton(tam)
    alto = 58                                        # antetitulo
    alto += len(spec["titular"]) * int(tam * 1.08)   # titular
    alto += 74                                       # aire
    nl = len(partir(d, spec["cuerpo"], barlow(40), W - 2 * M - 40))
    alto += nl * int(40 * 1.34)                      # cuerpo
    alto += 56                                       # aire
    alto += alto_modulo(*spec["modulo"])             # modulo
    return alto, tam


def pintar(spec):
    P = PIELES[spec["piel"]]
    if spec["piel"] == "foto":
        im = fondo_foto(spec.get("foto", "gym-2.jpg"))
    else:
        im = Image.new("RGB", (W, H), P["fondo"])
        if spec["piel"] == "dato":
            resplandor(im, (W - 120, 260), 460, (60, 84, 20), fuerza=110)
        if spec["piel"] == "papel":
            ImageDraw.Draw(im).rectangle((0, 0, W, 14), fill=ROJO)
    d = ImageDraw.Draw(im)
    y_marca = cabecera(im, d, P["tinta"], P["acento"], P["sub"])

    # Se busca el titular mas grande que quepa. La foto ademas se alinea
    # abajo: el texto tiene que descansar sobre el contacto, no flotar.
    tam = 124 if len(spec["titular"]) <= 3 else 108
    disponible = TOPE_CTA - (y_marca + 90) - 30
    while tam > 76:
        alto, real = medir(d, spec, tam)
        if alto <= disponible:
            break
        tam -= 6
    alto, tam = medir(d, spec, tam)
    if spec["piel"] == "foto":
        y = max(y_marca + 120, TOPE_CTA - 40 - alto)
    else:
        y = y_marca + 90
        if alto < disponible - 80:
            y += min(120, (disponible - alto) // 3)   # centrar un poco el bloque

    escribir(d, (M, y), spec["eyebrow"].upper(), cond(34), P["eyebrow"], track=9)
    y += 58
    y = titular(d, y, spec["titular"], P["tinta"], P["acento"],
                tam=tam, acento=spec.get("acento"))
    y = cuerpo(d, y + 74, spec["cuerpo"], P["cuerpo"], ancho=W - 2 * M - 40)
    tipo, datos = spec["modulo"]
    y = modulo(d, y + 56, tipo, datos, P)
    if y > TOPE_CTA - 12:
        print("     OJO: el contenido llega a %d y el contacto empieza en %d"
              % (y, TOPE_CTA))
    cta(d, P["cta"])
    return im


def generar(tanda, prefijo):
    os.makedirs(SALIDA, exist_ok=True)
    hechos = []
    for i, spec in enumerate(tanda, 1):
        im = pintar(spec)
        nom = "%s_%02d_%s.png" % (prefijo, i, spec["piel"])
        p = os.path.join(SALIDA, nom)
        im.save(p, "PNG", optimize=True)
        hechos.append(p)
        print("  %-28s %-6s %4d KB" % (nom, spec["piel"], os.path.getsize(p) // 1024))
    return hechos


def contactos(rutas, nombre, cols=4):
    """Todas las piezas en una imagen, para revisarlas de un vistazo."""
    tw, th, g = 260, 462, 14
    filas = (len(rutas) + cols - 1) // cols
    hoja = Image.new("RGB", (cols * tw + (cols + 1) * g, filas * th + (filas + 1) * g), (26, 26, 28))
    for i, r in enumerate(rutas):
        hoja.paste(Image.open(r).resize((tw, th), Image.LANCZOS),
                   (g + (i % cols) * (tw + g), g + (i // cols) * (th + g)))
    p = os.path.join(SALIDA, nombre)
    hoja.save(p, "PNG", optimize=True)
    print("  %-28s %sx%s  %d KB" % (nombre, hoja.size[0], hoja.size[1], os.path.getsize(p) // 1024))
    return p


if __name__ == "__main__":
    import piezas
    print("US19 · tanda RECLUTAR")
    r = generar(piezas.RECLUTAR, "US19R")
    print("")
    contactos(r, "US19_hoja_reclutar.png")
    print("  total: %d piezas" % len(r))
