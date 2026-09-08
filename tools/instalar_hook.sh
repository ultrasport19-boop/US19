#!/bin/sh
# Deja las pruebas de la tienda corriendo antes de cada commit.
#   sh tools/instalar_hook.sh
RAIZ="$(git rev-parse --show-toplevel)"
cp "$RAIZ/tools/pre-commit.sh" "$RAIZ/.git/hooks/pre-commit"
chmod +x "$RAIZ/.git/hooks/pre-commit"
echo "Hook instalado. Cada commit que toque tienda/index.html correra tools/tienda.js."
