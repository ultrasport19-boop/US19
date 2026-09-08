#!/bin/sh
# Deja las pruebas de las paginas publicas corriendo antes de cada commit.
#   sh tools/instalar_hook.sh
RAIZ="$(git rev-parse --show-toplevel)"
cp "$RAIZ/tools/pre-commit.sh" "$RAIZ/.git/hooks/pre-commit"
chmod +x "$RAIZ/.git/hooks/pre-commit"
echo "Hook instalado: index.html -> web.js, tienda/index.html -> tienda.js, ficha/index.html -> ficha.js."
