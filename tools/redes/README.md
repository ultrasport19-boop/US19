# Historias para redes

Genera las piezas de 1080×1920 de Ultra-Sport 19 con la tipografía de la marca.

```sh
sh tools/redes/bajar_fuentes.sh     # una sola vez
python tools/redes/historias.py     # deja los PNG en tools/redes/salida/
```

**Esto existe porque ya se perdió una vez.** Las 162 piezas de `img/redes/` se
hicieron con un generador que vivía en una carpeta temporal de una sesión; al
cerrarla desapareció, y con él la posibilidad de rehacerlas o de cambiarles una
coma. Lo mismo pasó antes con 28 suites de pruebas. Por eso esto está aquí y no
en el escritorio.

## Cómo está partido

| Archivo | Qué es |
|---|---|
| `piezas.py` | **Los textos.** Qué dice cada pieza y con qué piel |
| `historias.py` | **El dibujo.** Sabe pintar cuatro pieles sobre la misma estructura |
| `bajar_fuentes.sh` | Anton y Barlow desde Google Fonts |

Rehacer una tanda entera con otra piel es cambiar una palabra en `piezas.py`.

## Las cuatro pieles

- **papel** — fondo hueso, titular negro. Editorial, descansa entre tanto negro
- **rojo** — pared roja completa. Para lo que tiene que parar el dedo
- **foto** — una foto real de la sala con degradado y velo
- **dato** — carbón con acento verde lima. Para medición y bioimpedancia

Todas llevan la misma estructura: marca con logo arriba, antetítulo, titular en
Anton con una línea de acento, cuerpo, un módulo y el bloque de contacto.

## Módulos

`("lista", [(título, subtítulo), …])` · `("semana", [días marcados])` ·
`("regla", None)` · `("cifra", (número, línea1, línea2, pie))`

## Trampas ya pagadas — no deshacer sin mirar el PNG

- **Anton necesita interlineado 1.08.** Con menos, las tildes de Ñ e Í se pisan
  con la línea de arriba.
- **El «19» de la marca va en el color de acento de la piel.** Sobre el diseño
  rojo iba en rojo y desaparecía: la marca se quedaba en «ULTRA-SPORT».
- **Un halo pegado con una máscara que toca el borde de su caja deja una línea
  recta.** Hay que meter la elipse hacia dentro para que el desenfoque tenga
  dónde apagarse.
- **El generador mide antes de dibujar.** Un titular de cinco líneas se metía
  debajo del bloque de contacto y el teléfono quedaba encima del texto. Si el
  contenido no cabe, se reduce el titular; las piezas de foto se alinean abajo.
- **Las tipografías no están instaladas en Windows** y el CSS de Google Fonts
  devuelve `.woff2` a un navegador moderno: Pillow no las lee. `bajar_fuentes.sh`
  pide las `.ttf`.

## El formato manda sobre la casilla

Estas piezas son **1080×1920: solo sirven como historia de Instagram**. El feed
de Instagram admite entre 4:5 y 1.91:1, así que una vertical 9:16 la rechaza la
API, y en el muro de Facebook sale recortada.

Para feed o Facebook hacen falta piezas **1080×1350**: cambiar `W, H` y
recolocar el bloque de contacto. No es marcar una opción en Notion.

## Lo que no se pone aquí

Nada clínico. Diego es interno de kinesiología: defiende en diciembre de 2026 y
el título llega a inicios de 2027. Hasta entonces, ni «diagnóstico» ni
«tratamiento» ni «rehabilitación», y **nada sobre kinesiología** —ni insinuada,
ni como «se vienen cosas nuevas»—, que lo pidió expresamente.

Tampoco cifras sin confirmar ni promesas de resultado.
