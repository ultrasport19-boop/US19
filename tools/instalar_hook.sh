#!/bin/sh
# Deja las pruebas de las paginas publicas corriendo antes de cada commit.
#   sh tools/instalar_hook.sh
RAIZ="$(git rev-parse --show-toplevel)"
cp "$RAIZ/tools/pre-commit.sh" "$RAIZ/.git/hooks/pre-commit"
chmod +x "$RAIZ/.git/hooks/pre-commit"
echo "Hook instalado: tienda/index.html -> tools/tienda.js, ficha/index.html -> tools/ficha.js."
