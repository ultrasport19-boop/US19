#!/bin/sh
# Hook de pre-commit de US19 (paginas publicas). Se instala con
# tools/instalar_hook.sh — los hooks no viajan con el repo, hay que
# instalarlos en cada clon.
#
# Una sola barrera, pero es la que importa: la tienda es lo unico que ve
# alguien que llega desde Instagram, y sus fallos no se ven leyendo el
# codigo. Se ven el dia que Apps Script tarda cinco segundos.
RAIZ="$(git rev-parse --show-toplevel)"

if git diff --cached --name-only | grep -q "^tienda/index.html$"; then
  node "$RAIZ/tools/tienda.js" "$RAIZ/tienda/index.html" \
    || { echo ""; echo "la tienda no pasa sus pruebas: commit cancelado."; exit 1; }
fi
exit 0
