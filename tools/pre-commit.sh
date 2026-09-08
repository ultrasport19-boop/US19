#!/bin/sh
# Hook de pre-commit de US19 (paginas publicas). Se instala con
# tools/instalar_hook.sh — los hooks no viajan con el repo, hay que
# instalarlos en cada clon.
#
# Cuatro barreras. La primera corre SIEMPRE; las otras tres, una por pagina
# publica, solo si el commit toca su pagina.
#
#   secretos  va la primera y no depende de que se toque nada. Una
#             credencial puede aterrizar en cualquier archivo: un .py de
#             tools/redes, el sitemap, una nota. Y este es el repositorio
#             mas publico de los tres — no es que se pueda leer, es que
#             GitHub Pages lo sirve. El barrido de los 43 commits del
#             historial salio limpio; esto es para que siga siendo verdad.
#
# Las otras tres fallan en silencio, que es de lo que defienden:
#
#   tienda/  es lo unico que ve alguien que llega desde Instagram, y sus
#            fallos no se ven leyendo el codigo. Se ven el dia que Apps
#            Script tarda cinco segundos o Notion devuelve un 500.
#
#   index/   es la puerta: el bot la manda en siete puntos del flujo. Sus
#            fallos no se ven mirando la pagina —se ve preciosa igual— sino
#            en lo que dice de si misma: un JSON-LD roto deja a Google sin
#            horarios ni precio y nadie lo nota en meses, y un ancla a una
#            seccion renombrada deja un boton que no hace nada.
#
#   ficha/   no guarda nada: su unico producto es un texto que el bot lee
#            por etiquetas. Si aqui se renombra una, la ficha se envia
#            igual, el socio lee «gracias» y el dato no llega a Notion —
#            y nadie se entera. Por eso su suite comprueba el contrato
#            contra el Codigo.js del asistente cuando lo encuentra.
RAIZ="$(git rev-parse --show-toplevel)"
CAMBIADOS="$(git diff --cached --name-only)"

node "$RAIZ/tools/secretos.js" \
  || { echo ""; echo "hay algo con forma de credencial en el repositorio: commit cancelado."; exit 1; }

if echo "$CAMBIADOS" | grep -q "^tienda/index.html$"; then
  node "$RAIZ/tools/tienda.js" "$RAIZ/tienda/index.html" \
    || { echo ""; echo "la tienda no pasa sus pruebas: commit cancelado."; exit 1; }
fi

if echo "$CAMBIADOS" | grep -q "^index.html$"; then
  node "$RAIZ/tools/web.js" "$RAIZ/index.html" \
    || { echo ""; echo "la web publica no pasa sus pruebas: commit cancelado."; exit 1; }
fi

if echo "$CAMBIADOS" | grep -q "^ficha/index.html$"; then
  node "$RAIZ/tools/ficha.js" "$RAIZ/ficha/index.html" \
    || { echo ""; echo "la ficha de ingreso no pasa sus pruebas: commit cancelado."; exit 1; }
fi

exit 0
