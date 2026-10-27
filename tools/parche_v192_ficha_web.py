# -*- coding: utf-8 -*-
"""
parche_v192_ficha_web.py · T5 de la auditoría integral (26-oct-2026)

La ficha web (ficha/index.html, LF) pregunta el objetivo y obliga a decir
cómo nos conoció. Y su suite (tools/ficha.js) aprende las dos reglas nuevas.

    python parche_v192_ficha_web.py <raíz del repo web>

Anclas de texto EXACTO, una sola coincidencia cada una (si no, aborta sin
escribir). Se guarda una copia previa «.antes_v192.bak» junto a cada archivo.
Los dos archivos van en LF: se leen y escriben con newline="" para no
cambiar ni un salto de línea.
"""
import io
import os
import sys

raiz = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()


def leer(ruta):
    with io.open(ruta, "r", encoding="utf-8", newline="") as f:
        return f.read()


def escribir(ruta, texto):
    with io.open(ruta, "w", encoding="utf-8", newline="") as f:
        f.write(texto)


def reemplazar(texto, ancla, nuevo, nombre):
    n = texto.count(ancla)
    assert n == 1, "ancla «%s»: %d coincidencias (se esperaba 1)" % (nombre, n)
    return texto.replace(ancla, nuevo)


# ---------------------------------------------------------------- ficha/index.html
ruta_html = os.path.join(raiz, "ficha", "index.html")
html = leer(ruta_html)
assert "\r" not in html, "ficha/index.html tiene CR: se esperaba LF"
assert "id=\"objetivo\"" not in html, "ficha/index.html ya está parchado"

# (1) «Cómo nos conoció» obligatorio: se va «Prefiero no decir». Queda un marcador
#     deshabilitado con value="" para que el navegador NO preseleccione Instagram
#     (sin marcador, el primer <option> sale elegido solo y el dato se inventa).
html = reemplazar(
    html,
    '        <option value="">Prefiero no decir</option>\n',
    '        <option value="" disabled selected>Elige una opción</option>\n',
    "select: Prefiero no decir",
)

# (2) La pregunta del objetivo, después de «quién te lo recomendó».
ANCLA_QUIEN = (
    '    <label class="campo ancho"><span>Si te lo recomendó alguien, ¿quién? <em>(opcional, para agradecérselo)</em></span>'
    '<input type="text" id="quienrecomendo" placeholder="Nombre de quien te habló de nosotros"></label>\n'
)
CAMPO_OBJETIVO = ANCLA_QUIEN + (
    '    <!-- v192 (26-oct-2026): el objetivo, obligatorio. Estaba vacío en 59 de 62\n'
    '         activos porque nadie lo preguntaba al entrar. Viaja con etiqueta propia\n'
    '         («Objetivo:») y el bot lo escribe en «Objetivo» solo si la ficha no\n'
    '         tiene ya uno. Tope de 200 caracteres aquí y en el bot. -->\n'
    '    <label class="campo ancho"><span>¿Qué quieres lograr en los próximos 3 meses?</span>'
    '<input type="text" id="objetivo" maxlength="200" '
    'placeholder="Por ejemplo: ganar fuerza, bajar grasa, rendir mejor en mi deporte, más energía, volver a entrenar, otro"></label>\n'
)
html = reemplazar(html, ANCLA_QUIEN, CAMPO_OBJETIVO, "label quienrecomendo")

# (3) Las seis opciones válidas, al lado del número del bot.
html = reemplazar(
    html,
    "  var BOT = '56965902238';\n",
    "  var BOT = '56965902238';\n"
    "  /* v192: las mismas seis opciones del <select id=\"comollegaste\"> y de Notion.\n"
    "     Sin una de estas no se envía: «Cómo nos conoció» estaba vacío en 41 de 62. */\n"
    "  var CANALES = ['Instagram', 'Facebook', 'Recomendación', 'Pasó por el gym', 'Google / Web', 'Otro'];\n",
    "var BOT",
)

# (4) La línea «Objetivo: …» del mensaje, al final y con etiqueta propia.
html = reemplazar(
    html,
    "      'Quien recomendo: ' + (limpio($('quienrecomendo').value) || '-')\n"
    "    ].join('\\n');\n",
    "      'Quien recomendo: ' + (limpio($('quienrecomendo').value) || '-'),\n"
    "      /* v192: el objetivo. Etiqueta propia para US19_FICHA_campo_; el bot lo\n"
    "         escribe en «Objetivo» si la ficha no tiene uno. Tope 200. */\n"
    "      'Objetivo: ' + (limpio($('objetivo').value).slice(0, 200) || '-')\n"
    "    ].join('\\n');\n",
    "armar(): Quien recomendo",
)

# (5) Validación: en el orden de la página (nombre → objetivo → canal → acepta → fotos).
html = reemplazar(
    html,
    "    if (!limpio($('nombre').value)) return falla('Falta tu nombre completo.', $('nombre'));\n",
    "    if (!limpio($('nombre').value)) return falla('Falta tu nombre completo.', $('nombre'));\n"
    "    if (!limpio($('objetivo').value)) return falla('Falta decir que quieres lograr en los proximos 3 meses, en la seccion 2.', $('objetivo'));\n"
    "    if (CANALES.indexOf($('comollegaste').value) < 0) return falla('Falta elegir como llegaste a Ultra-Sport 19, en la seccion 2.', $('comollegaste'));\n",
    "validación nombre",
)

# ---------------------------------------------------------------- tools/ficha.js
ruta_js = os.path.join(raiz, "tools", "ficha.js")
js = leer(ruta_js)
assert "\r" not in js, "tools/ficha.js tiene CR: se esperaba LF"
assert "objetivo" not in js, "tools/ficha.js ya está parchado"

js = reemplazar(
    js,
    "  comollegaste: 'Recomendación', quienrecomendo: 'Pedro', acepta: true,\n",
    "  comollegaste: 'Recomendación', quienrecomendo: 'Pedro', objetivo: '  Ganar fuerza  ', acepta: true,\n",
    "COMPLETA",
)

ANCLA_NO_FOTOS = "/* Que un NO a las fotos SI deje enviar: si no, el consentimiento no seria\n"
PRUEBAS_NUEVAS = (
    "/* v192 (26-oct-2026): el objetivo y el canal, obligatorios. Vacíos en 59 y 41\n"
    "   de 62 activos porque nada obligaba a decirlos al entrar. */\n"
    "E = nuevoEntorno(Object.assign({}, COMPLETA, { objetivo: '   ' }), { imagen: 'Si' });\n"
    "E.pulsar();\n"
    "igual('validacion · sin objetivo no se envia', E.destino(), '');\n"
    "comprobar('validacion · y el foco va al objetivo', E.enfocado.indexOf('objetivo') >= 0);\n"
    "comprobar('validacion · con un aviso que habla de lograr', /lograr/i.test(E.els.aviso.textContent), E.els.aviso.textContent);\n"
    "\n"
    "E = nuevoEntorno(Object.assign({}, COMPLETA, { comollegaste: '' }), { imagen: 'Si' });\n"
    "E.pulsar();\n"
    "igual('validacion · sin elegir como llego no se envia', E.destino(), '');\n"
    "comprobar('validacion · y el foco va al desplegable', E.enfocado.indexOf('comollegaste') >= 0);\n"
    "comprobar('validacion · con un aviso que habla de como llegaste', /llegaste/i.test(E.els.aviso.textContent), E.els.aviso.textContent);\n"
    "\n"
    "E = nuevoEntorno(Object.assign({}, COMPLETA, { comollegaste: 'Prefiero no decir' }), { imagen: 'Si' });\n"
    "E.pulsar();\n"
    "igual('validacion · un canal que no es de los seis de Notion tampoco se envia', E.destino(), '');\n"
    "\n"
    "['Instagram', 'Facebook', 'Recomendación', 'Pasó por el gym', 'Google / Web', 'Otro'].forEach(function (canal) {\n"
    "  const F = nuevoEntorno(Object.assign({}, COMPLETA, { comollegaste: canal }), { imagen: 'Si' });\n"
    "  F.pulsar();\n"
    "  comprobar('validacion · el canal «' + canal + '» deja enviar', F.destino().indexOf('wa.me') > 0);\n"
    "});\n"
    "\n"
    "comprobar('marcado · ya no existe la opcion «Prefiero no decir»', src.indexOf('Prefiero no decir') < 0);\n"
    "comprobar('marcado · el desplegable arranca sin canal elegido (marcador deshabilitado con value=\"\")',\n"
    "  /<option value=\"\" disabled selected>/.test(src), 'sin marcador el navegador preselecciona el primer canal y el dato se inventa');\n"
    "comprobar('marcado · el objetivo tiene tope de 200 caracteres en el campo',\n"
    "  /id=\"objetivo\" maxlength=\"200\"/.test(src));\n"
    "\n"
    "E = nuevoEntorno(Object.assign({}, COMPLETA, { objetivo: 'x'.repeat(250) }), { imagen: 'Si' });\n"
    "E.pulsar();\n"
    "igual('mensaje · un objetivo de 250 caracteres viaja recortado a 200',\n"
    "  ((E.mensaje().match(/^Objetivo: (.*)$/m) || [])[1] || '').length, 200);\n"
    "\n"
) + ANCLA_NO_FOTOS
js = reemplazar(js, ANCLA_NO_FOTOS, PRUEBAS_NUEVAS, "comentario NO a las fotos")

js = reemplazar(
    js,
    "comprobar('mensaje · y quien recomendo tambien', /^Quien recomendo: Pedro$/m.test(MSG));\n",
    "comprobar('mensaje · y quien recomendo tambien', /^Quien recomendo: Pedro$/m.test(MSG));\n"
    "comprobar('mensaje · el objetivo viaja limpio y con su etiqueta', /^Objetivo: Ganar fuerza$/m.test(MSG), (MSG.match(/^Objetivo:.*$/m) || [])[0]);\n",
    "mensaje quien recomendo",
)

js = reemplazar(
    js,
    "    igual('contrato · el bot lee quien recomendo', api.campo(MSG, 'Quien recomendo'), 'Pedro');\n",
    "    igual('contrato · el bot lee quien recomendo', api.campo(MSG, 'Quien recomendo'), 'Pedro');\n"
    "    igual('contrato · el bot lee el objetivo', api.campo(MSG, 'Objetivo'), 'Ganar fuerza');\n",
    "contrato quien recomendo",
)

# ---------------------------------------------------------------- escribir
for ruta, texto in ((ruta_html, html), (ruta_js, js)):
    previa = ruta + ".antes_v192.bak"
    if not os.path.exists(previa):
        escribir(previa, leer(ruta))
    escribir(ruta, texto)
    print("parchado:", ruta, "(copia previa en", previa + ")")
