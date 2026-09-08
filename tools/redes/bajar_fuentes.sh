#!/bin/sh
# Baja las tipografías de la marca a ./fuentes/. Se ejecuta una vez.
#   sh tools/redes/bajar_fuentes.sh
#
# No se versionan a propósito: son SIL OFL y redistribuirlas obliga a
# incluir su licencia. Bajarlas es una orden, así que no vale la pena.
#
# El truco: se le pide el CSS a Google Fonts con user-agent de escritorio;
# a un navegador moderno le devuelve .woff2, que Pillow no sabe leer.
D="$(dirname "$0")/fuentes"
mkdir -p "$D"
b() { curl -sS --max-time 60 "$1" -o "$D/$2" && echo "  $2"; }
echo "Bajando a $D"
b "https://fonts.gstatic.com/s/anton/v27/1Ptgg87LROyAm0K0.ttf" "Anton.ttf"
b "https://fonts.gstatic.com/s/barlow/v13/7cHpv4kjgoGqM7EPCw.ttf" "Barlow-Regular.ttf"
b "https://fonts.gstatic.com/s/barlow/v13/7cHqv4kjgoGqM7E30-8c4A.ttf" "Barlow-SemiBold.ttf"
b "https://fonts.gstatic.com/s/barlow/v13/7cHqv4kjgoGqM7E3t-4c4A.ttf" "Barlow-Bold.ttf"
b "https://fonts.gstatic.com/s/barlowcondensed/v13/HTxwL3I-JCGChYJ8VI-L6OO_au7B46r2_3E.ttf" "BarlowCondensed-SemiBold.ttf"
b "https://fonts.gstatic.com/s/barlowcondensed/v13/HTxwL3I-JCGChYJ8VI-L6OO_au7B4873_3E.ttf" "BarlowCondensed-Bold.ttf"
echo "Listo. Ahora: python tools/redes/historias.py"
