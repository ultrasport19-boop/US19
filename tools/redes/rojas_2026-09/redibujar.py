# -*- coding: utf-8 -*-
"""Redibuja las historias negro+rojo programadas con las 5 pieles nuevas (Diego, 27-sep-2026).

python redibujar.py prueba   -> solo a ./redibujadas/ + hoja de contacto (no toca el repo)
python redibujar.py final    -> además copia encima de img/redes/ con el MISMO nombre
"""
import os, sys, io, json, glob, re, copy, shutil
REDES = r"C:\Users\diego\OneDrive\Documentos\GitHub\US19\tools\redes"
IMG = r"C:\Users\diego\OneDrive\Documentos\GitHub\US19\img\redes"
sys.path.insert(0, REDES)
import historias as H
import segno
from PIL import Image, ImageDraw

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "redibujadas")
os.makedirs(OUT, exist_ok=True)
TIENDA = "https://ultrasport19-boop.github.io/US19/tienda/"
PIELES = ["noche", "arena", "bosque", "grafito", "amarillo"]

# Correcciones de contenido (reglas de la casa). Se aplican a todo el texto.
REEMPLAZOS = [
    (r"\s*·\s*", ", "),
    (r"[^.]*diagn[oó]stic[^.]*\.?", ""),   # regla de la casa: la palabra no aparece, ni en negación
]
# Piezas que cambian entero
FIJAS = {
    "US19K_con03_ochenta5.jpg": dict(eyebrow="POR QUÉ NO CRECEMOS MÁS", titular=["UN TOPE,", "A PROPÓSITO."], acento=0,
        cuerpo="No es marketing: cuando la sala se llena, dejamos de sumar gente para que cada hora siga siendo de ocho. "
               "Cuando se llena, se llena. Por eso los cupos se avisan con tiempo.", lista=[], extra=""),
}
EXCLUIR = {"US19_fiestas-patrias-2026.jpg"}   # no es del diseño rojo: se queda como está
# Correcciones puntuales por archivo (se llenan tras leer las notas de los agentes)
AJUSTES = {}
if os.path.exists(os.path.join(AQUI, "ajustes.json")):
    AJUSTES = json.load(io.open(os.path.join(AQUI, "ajustes.json"), encoding="utf-8"))


def limpiar(t):
    t_orig = t
    t = str(t or "")
    for a, b in REEMPLAZOS:
        t = re.sub(a, b, t)
    t = re.sub(r"^\s*,\s*|\s*,\s*$", "", t) if "·" in str(t_orig) else t
    return t.strip()


def qr(lado):
    b = io.BytesIO()
    segno.make(TIENDA, error="h").save(b, kind="png", scale=10, border=2, dark="#111111", light="#ffffff")
    b.seek(0)
    return Image.open(b).convert("RGB").resize((lado, lado), Image.NEAREST)


QR = qr(190)


def pintar(spec):
    """Copia de historias.pintar que además devuelve dónde termina el contenido."""
    P = H.PIELES[spec["piel"]]
    im = Image.new("RGB", (H.W, H.H), P["fondo"])
    d = ImageDraw.Draw(im)
    y_marca = H.cabecera(im, d, P["tinta"], P["acento"], P["sub"])
    tam = 124 if len(spec["titular"]) <= 3 else 108
    disponible = H.TOPE_CTA - (y_marca + 90) - 30
    while tam > 70:
        alto, real = H.medir(d, spec, tam)
        if alto <= disponible:
            break
        tam -= 6
    alto, tam = H.medir(d, spec, tam)
    y = y_marca + 90
    if alto < disponible - 80:
        y += min(120, (disponible - alto) // 3)
    H.escribir(d, (H.M, y), spec["eyebrow"].upper(), H.cond(34), P["eyebrow"], track=9)
    y += 58
    y = H.titular(d, y, spec["titular"], P["tinta"], P["acento"], tam=tam, acento=spec.get("acento"))
    if spec.get("cuerpo"):
        y = H.cuerpo(d, y + 74, spec["cuerpo"], P["cuerpo"], ancho=H.W - 2 * H.M - 40)
    tipo, datos = spec["modulo"]
    y = H.modulo(d, y + 56, tipo, datos, P)
    H.cta(d, P["cta"])
    return im, y, P


def poner_qr(im, y_fin, P):
    caja = 214
    y0 = H.H - 292 - 84 - 26 - caja - 34
    if y_fin > y0 - 16:
        return False            # no cabe sin tapar texto: esta pieza va sin QR
    d = ImageDraw.Draw(im)
    x1 = H.W - H.M
    x0 = x1 - caja
    d.rounded_rectangle((x0, y0, x1, y0 + caja), radius=12, fill=(255, 255, 255))
    im.paste(QR, (x0 + 12, y0 + 12))
    H.escribir(d, (x0 - 4, y0 + caja + 6), "TIENDA US19", H.cond(26), P["sub"], track=4)
    return True


def spec_de(t, piel):
    a = FIJAS.get(t["archivo"]) or t
    a = dict(a, **AJUSTES.get(t["archivo"], {}))
    tit = [limpiar(x).upper() for x in (a.get("titular") or []) if limpiar(x)]
    if not tit:
        return None
    cuerpo = limpiar(a.get("cuerpo"))
    # «extra» trae descripciones de los agentes mezcladas con texto: no se usa solo (lo necesario va en ajustes.json)
    lista = [[limpiar(x[0]), limpiar(x[1] if len(x) > 1 else "")] for x in (a.get("lista") or []) if limpiar(x[0])]
    for it in lista:   # regla vigente: la reevaluación va incluida desde el plan de 3 veces
        if re.search(r"reevaluaci[oó]n (mensual|cada mes)", it[0], re.I):
            it[1] = "incluida desde el plan de 3 veces"
    ac = a.get("acento")
    if not isinstance(ac, int) or not (0 <= ac < len(tit)):
        ac = len(tit) - 1 if len(tit) > 1 else None
    return dict(piel=piel, eyebrow=limpiar(a.get("eyebrow")) or "ULTRA-SPORT 19", titular=tit, acento=ac,
                cuerpo=cuerpo, modulo=("lista", lista[:4]) if lista else ("regla", None))


def main(modo):
    orden = [x["archivo"] for x in json.load(io.open(os.path.join(AQUI, "rojas.json"), encoding="utf-8"))]
    textos = {}
    for f in sorted(glob.glob(os.path.join(AQUI, "textos_*.json"))):
        for t in json.load(io.open(f, encoding="utf-8")):
            textos[t["archivo"]] = t
    hechos, sin_qr, saltados, asignado = [], [], [], {}
    i = 0
    for arch in orden:
        if arch in EXCLUIR:
            saltados.append(arch + " (fuera de la tanda)")
            continue
        t = textos.get(arch)
        if not t:
            saltados.append(arch + " (sin texto)")
            continue
        piel = PIELES[i % len(PIELES)]
        s = spec_de(t, piel)
        if not s:
            saltados.append(arch + " (sin titular)")
            continue
        i += 1
        im, y, P = pintar(s)
        if not poner_qr(im, y, P):
            sin_qr.append(arch)
        if y > H.TOPE_CTA - 12:
            saltados.append(arch + " (el texto no cabe: revisar)")
            continue
        destino = os.path.join(OUT, arch)
        if arch.lower().endswith(".png"):
            im.save(destino, "PNG", optimize=True)
        else:
            im.save(destino, "JPEG", quality=88)
        hechos.append(destino)
        asignado[arch] = piel
    json.dump(asignado, io.open(os.path.join(AQUI, "pieles_asignadas.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # hoja de contacto
    tw, th, g, cols = 180, 320, 8, 10
    filas = (len(hechos) + cols - 1) // cols
    hoja = Image.new("RGB", (cols * tw + (cols + 1) * g, max(1, filas) * th + (filas + 1) * g), (26, 26, 28))
    for k, r in enumerate(hechos):
        hoja.paste(Image.open(r).convert("RGB").resize((tw, th), Image.LANCZOS), (g + (k % cols) * (tw + g), g + (k // cols) * (th + g)))
    hoja.save(os.path.join(AQUI, "HOJA_redibujadas.jpg"), quality=85)
    print("hechas:", len(hechos), "| sin QR (no cabía):", len(sin_qr), "| saltadas:", len(saltados))
    for x in saltados:
        print("  saltada:", x)
    if modo == "final":
        for r in hechos:
            shutil.copyfile(r, os.path.join(IMG, os.path.basename(r)))
        print("copiadas encima de img/redes:", len(hechos))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "prueba")
