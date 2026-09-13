# US19 — Contexto para agentes de IA

Sitio público de Ultra-Sport19, gimnasio de entrenamiento personalizado en Pencahue, Maule, Chile. Propietario: Diego Valenzuela. Moneda: CLP. Zona horaria: `America/Santiago`. Se sirve en GitHub Pages: `https://ultrasport19-boop.github.io/US19/`.

Este repositorio es `US19`, remoto `ultrasport19-boop/US19`. Es **público**: todo lo que se commitee se publica.

## 1. Repo y rutas reales

En este PC:

- Raíz: `C:\Users\diego\OneDrive\Documentos\GitHub\US19`
- Home: `index.html`
- Tienda: `tienda\index.html`
- Ficha de ingreso: `ficha\index.html` y `ficha\index_imprimible.html`
- Privacidad: `privacidad.html`
- 404: `404.html`
- Pruebas de la web: `tools\web.js`
- Pruebas de la tienda: `tools\tienda.js`
- Pruebas de la ficha: `tools\ficha.js`
- Barrido de secretos: `tools\secretos.js`
- Mutaciones: `tools\mutantes.js` + `tools\mutantes_*.json`
- Finales de línea: `.gitattributes`

Repos hermanos, no viven aquí:

- Asistente (privado): `..\..\RESPALDO_ASISTENTE_APPSSCRIPT`
- App interna (pública): `..\US19-APP`

No asumir que existe `Código.js` ni `proyecto_clasp` en este repo.

## 2. Qué es este repo

Páginas estáticas. No hay backend propio, no hay Apps Script, no hay Node en producción.

- La home y la ficha no piden datos al asistente.
- La tienda pide el catálogo público `?tipo=tienda` del despliegue de catálogo, **no** el webhook de Meta.
- La ficha arma un mensaje de WhatsApp y lo envía el propio socio; no hay `fetch` ni almacenamiento local.

## 3. Reglas duras

1. Repositorio público: nunca escribir tokens, claves ni `US19_CLAVE_APP`. El catálogo no lleva clave.
2. No poner aquí la URL del webhook de Meta. Esa entra mensajes de WhatsApp. La tienda solo puede usar el despliegue de catálogo que ya está en `tienda/index.html`.
3. Hasta el título en 2027, no introducir kinesiología ni lenguaje clínico en contenido público. Las únicas apariciones válidas son negaciones ya revisadas («no constituye diagnóstico médico», textos legales de la ficha).
4. `Disponibilidad` del catálogo es stock real, no modalidad de venta.
5. Notion manda sobre precios y stock; este repo no inventa cifras.
6. No desplegar el asistente ni ejecutar `clasp`.
7. Preservar los EOL declarados en `.gitattributes`: `index.html`, `404.html`, `privacidad.html` y `tienda/index.html` van en CRLF; `ficha/*.html` y las herramientas van en LF.
8. Antes de crear utilidades, buscar en `tools\`.
9. Verificar con `node tools/web.js`, `node tools/tienda.js`, `node tools/ficha.js`, `node tools/secretos.js` y los mutantes que correspondan.

## 4. Contrato con el asistente

- Catálogo: `US19_TIENDA_leer_` y `US19_TIENDA_catalogo_` en el `Código.js` del asistente. `tools\tienda.js` compara los campos.
- Ficha: `US19_FICHA_esFormulario_` y `US19_FICHA_campo_` en el asistente. `tools\ficha.js` les entrega el mensaje que produce esta página.
- Teléfono público de WhatsApp: `56965902238`. Tiene que coincidir en home, ficha y tienda.

## 5. Cómo trabajar

1. Leer completa la página o función que se vaya a modificar.
2. Parches con anclas exactas; abortar si la coincidencia no es única.
3. No commitear secretos ni la URL del webhook.
4. Resumir archivos tocados y validaciones.

## 6. Glosario

- **Catálogo**: JSON público `?tipo=tienda`. Distinto del webhook de Meta.
- **Ficha**: formulario de ingreso que sale por WhatsApp, no por servidor.
- **Home**: puerta de Instagram y del bot.
