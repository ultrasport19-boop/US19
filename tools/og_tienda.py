"""Fase 6 · og:image de la tienda (1200x630) con seis portadas reales y el logo.
Negro y rojo, como el gimnasio. Sin inventar nada: solo lo que ya dice la página."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps

FOTOS = r"C:\yupoo_fotos"
REPO = r"C:\Users\diego\OneDrive\Documentos\GitHub\US19"
SALIDA = os.path.join(REPO, "img", "og-tienda.jpg")
# id de álbum → archivo frontal elegido en la revisión (lote 15, 14-sep-2026)
CAMISETAS = [("115305227", "2.jpg"), ("114155575", "2.jpg"), ("118915481", "7.jpg"),
             ("114158441", "2.jpg"), ("119012550", "7.jpg"), ("117649073", "7.jpg")]
W, H = 1200, 630
NEGRO, ROJO, BLANCO, GRIS = (11, 11, 12), (214, 30, 40), (245, 245, 245), (170, 170, 175)

img = Image.new("RGB", (W, H), NEGRO)
d = ImageDraw.Draw(img)
# franja roja arriba, como la cabecera de la página
d.rectangle([0, 0, W, 8], fill=ROJO)

# --- seis camisetas en fila, recortadas al centro (la prenda cuelga centrada) ---
ancho, alto, y0, sep = 176, 214, 40, 12
x = W - 6 * ancho - 5 * sep - 40
for aid, arch in CAMISETAS:
    ruta = os.path.join(FOTOS, aid, arch)
    foto = Image.open(ruta).convert("RGB")
    fw, fh = foto.size
    # recorte central: la camiseta ocupa ~el 70% del ancho y del 20% al 95% del alto
    caja = (int(fw * 0.14), int(fh * 0.12), int(fw * 0.86), int(fh * 0.98))
    foto = foto.crop(caja)
    foto = ImageOps.fit(foto, (ancho, alto), Image.LANCZOS, centering=(0.5, 0.45))
    marco = Image.new("RGB", (ancho + 6, alto + 6), (40, 40, 44))
    marco.paste(foto, (3, 3))
    img.paste(marco, (x, y0))
    x += ancho + sep

# --- logo, a la izquierda abajo ---
logo = Image.open(os.path.join(REPO, "img", "logo.png")).convert("RGBA")
logo = logo.resize((190, 190), Image.LANCZOS)
img.paste(logo, (40, 300), logo)

# --- textos ---
def fuente(nombre, tam):
    try:
        return ImageFont.truetype(os.path.join(r"C:\Windows\Fonts", nombre), tam)
    except Exception:
        return ImageFont.load_default()

f1, f2, f3 = fuente("impact.ttf", 78), fuente("bahnschrift.ttf", 34), fuente("bahnschrift.ttf", 27)
d.text((256, 312), "CAMISETAS DE FÚTBOL", font=f1, fill=BLANCO)
d.text((256, 392), "POR ENCARGO", font=f1, fill=ROJO)
d.text((258, 488), "Eliges tu talla · Estampado con tu nombre y número", font=f2, fill=BLANCO)
d.text((258, 532), "Pides por WhatsApp · Ultra-Sport 19, Pencahue", font=f3, fill=GRIS)
d.rectangle([0, H - 8, W, H], fill=ROJO)

img.save(SALIDA, "JPEG", quality=84, optimize=True, progressive=True)
print(SALIDA, os.path.getsize(SALIDA) // 1024, "KB")
