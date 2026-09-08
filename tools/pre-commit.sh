#!/bin/sh
# Hook de pre-commit de US19 (paginas publicas). Se instala con
# tools/instalar_hook.sh — los hooks no viajan con el repo, hay que
# instalarlos en cada clon.
#
# Dos barreras, y las dos son de paginas que fallan en silencio:
#
#   tienda/  es lo unico que ve alguien que llega desde Instagram, y sus
#            fallos no se ven leyendo el codigo. Se ven el dia que Apps
#            Script tarda cinco segundos o Notion devuelve un 500.
#
#   ficha/   no guarda nada: su unico producto es un texto que el bot lee
#            por etiquetas. Si aqui se renombra una, la ficha se envia
#            igual, el socio lee «gracias» y el dato no llega a Notion —
#            y nadie se entera. Por eso su suite comprueba el contrato
#            contra el Codigo.js del asistente cuando lo encuentra.
RAIZ="$(git rev-parse --show-toplevel)"
CAMBIADOS="$(git diff --cached --name-only)"

if echo "$CAMBIADOS" | grep -q "^tienda/index.html$"; then
  node "$RAIZ/tools/tienda.js" "$RAIZ/tienda/index.html" \
    || { echo ""; echo "la tienda no pasa sus pruebas: commit cancelado."; exit 1; }
fi

if echo "$CAMBIADOS" | grep -q "^ficha/index.html$"; then
  node "$RAIZ/tools/ficha.js" "$RAIZ/ficha/index.html" \
    || { echo ""; echo "la ficha de ingreso no pasa sus pruebas: commit cancelado."; exit 1; }
fi

exit 0
