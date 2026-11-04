# Auditoría web ultrasport19.com (1-nov-2026)

Rama: `nube/web-seo-1nov` (sale de `main` en `d3221e8`). **No se publicó nada:** `main` no se tocó y no hay PR.
Alcance: `index.html` (portada), más `robots.txt`, `sitemap.xml` y el atributo de idioma de `tienda/`, `sorteo/` y `ficha/`.
Pruebas después de los cambios: `node tools/web.js` da 27 OK y 0 fallos; `tools/ficha.js`, 65 OK; `tools/secretos.js`, 4 OK; los mutantes de la web (9 de 9) y de la ficha (10 de 10) caen todos. `tools/tienda.js` ya fallaba en `main` con 2 fallos de contrato contra el `Código.js` del bot (`US19_TIENDA_prenda_`); no tiene relación con estos cambios.
Revisión visual a 390 px de ancho: el logo del hero se ve igual (WebP, centrado), el menú se abre y se cierra, Escape devuelve el foco y el reel parte solo cuando aparece en pantalla.

## Resumen (10 líneas)

1. La base de SEO local ya era buena: ficha `ExerciseGym` con dirección, teléfono, horario y redes, canonical a ultrasport19.com, Open Graph completo y `lang="es-CL"` en la portada.
2. El `<title>` no decía «entrenamiento de fuerza» y la descripción no mencionaba Talca. Quedan «Gimnasio en Pencahue | Entrenamiento de fuerza | Ultra-Sport19» y una descripción de 158 caracteres con «sin viajar a Talca» (aplicado).
3. Al JSON-LD le faltaban `@id`, `areaServed`, el servicio de la sala y el nodo `WebSite`. Además, cuatro respuestas del FAQ no coincidían con el texto visible. Todo eso está aplicado. **Faltan las coordenadas `geo` y el código postal: DATO A CONFIRMAR.**
4. El `sitemap.xml` anunciaba fotos que ya no salen en la página (`hero.jpg`, `sala-1`, `sala-2`) y su fecha era del 14-sep. Ahora lista las fotos reales y la fecha es el 31-oct (aplicado).
5. `robots.txt` bloqueaba `privacidad.html`, y eso impedía que Google leyera su `noindex`. Se quitó la línea (aplicado).
6. Hay un fallo de teclado: el video del recorrido no se podía reproducir sin mouse, y los enlaces del menú cerrado del celular recibían el foco sin verse. Los dos están corregidos, y Escape ahora cierra el menú (aplicado).
7. Hay contraste insuficiente en la letra chica (`--gris-claro`: 2,6 a 2,9 sobre 1) y en las etiquetas rojas sobre fondo hielo (4,2 sobre 1). **Solo está propuesto**, porque cambia colores visibles.
8. Velocidad: el reel de 1,8 MB se descargaba al abrir la página. Ahora se descarga solo al verse. Además, el logo del hero baja de 183 KB a 57 KB (WebP) y la foto de bioimpedancia de 223 KB a 111 KB, sin cambiar cómo se ven (aplicado).
9. Lo que más pesa y queda propuesto: el video del hero (1 MB al abrir en el celular) y las fuentes de Google, que bloquean el primer dibujo (lo mejor es alojarlas en el propio sitio).
10. Lo decisivo para «gimnasio Pencahue» y, sobre todo, para «gimnasio Talca personalizado» está fuera del código: la ficha de Google Business Profile, las reseñas y las fotos. Ver la lista del final.

## Tabla de hallazgos

Impacto: **Alto** (posiciones, conversión o un bloqueo real), **Medio**, **Bajo**. Las líneas son las de `index.html` en la rama.

### 1. SEO local

| Impacto | Archivo:línea | Problema | Cambio |
|---|---|---|---|
| Alto | index.html:6 | El title no tenía «entrenamiento de fuerza». | **Aplicado:** «Gimnasio en Pencahue \| Entrenamiento de fuerza \| Ultra-Sport19» (62 caracteres). |
| Alto | index.html:7 | La descripción no nombraba Talca y llevaba el precio, que puede quedar desactualizado. | **Aplicado:** «Gimnasio boutique de fuerza en Pencahue, sin viajar a Talca: máximo 8 personas por hora, rutina a tu medida y entrenador en la tarde. Escríbenos por WhatsApp.» Cada dato ya está en la página. |
| Alto | index.html:779 | El H1 («Máximo 8 personas por hora…») no dice «gimnasio» ni «Pencahue». Lo dice el kicker (778), pero ese es un `<p>`. | **Propuesto** (es texto visible). Opción A: que el kicker sea parte del H1, con el mismo aspecto: `<h1><span class="hero__kicker">Gimnasio boutique de fuerza en Pencahue</span> Máximo 8 personas…</h1>`. Opción B: dejar el H1 y rehacer el kicker como «Gimnasio boutique de fuerza en Pencahue, Maule». |
| Alto | index.html:43-84 | Faltaban `@id`, `areaServed` y `amenityFeature`, y la `description` no decía «fuerza». | **Aplicado:** `@id` #gimnasio, `inLanguage` es-CL, `areaServed` Pencahue y Región del Maule, 3 `amenityFeature` (sala de fuerza, sala de cardio, entrenador de 16:00 a 22:00) e imágenes reales (hero-sala, sala-rack, sala-pesolibre). |
| Alto | index.html:58-63 | Sin `geo` (latitud y longitud) ni `postalCode`. | **DATO A CONFIRMAR.** No se inventan. Copiar las coordenadas exactas del pin de Google Business Profile y añadir `"geo":{"@type":"GeoCoordinates","latitude":…,"longitude":…}` y `"postalCode"`. Con las mismas coordenadas, añadir `<meta name="geo.position">` e `ICBM` junto a la línea 28. |
| Medio | index.html:44 | El nombre aparece como «Ultra-Sport19» (web y JSON-LD) y como «Ultra-Sport 19» (marca, tienda, ficha). Google cruza nombre, dirección y teléfono. | **Propuesto:** usar en `name` el nombre **exacto** de la ficha de Google (DATO A CONFIRMAR) y dejar el otro en `alternateName`. |
| Medio | index.html:107-120 | Cuatro respuestas del FAQ en JSON-LD no coincidían con lo que se ve. Además, Google ya no muestra resultados enriquecidos de FAQ para gimnasios (desde ago-2023). | **Aplicado:** respuestas iguales al texto visible. **Propuesto:** la pregunta «¿Cuánto cuestan los planes?» (115) no está en el FAQ visible. Hay que agregarla al FAQ visible o quitarla del JSON-LD. |
| Medio | index.html:56, 85-90, 115 | Los precios están repetidos en `priceRange`, `makesOffer`, el FAQ JSON-LD, el texto visible y el mensaje de compartir. | **Propuesto:** si los precios cambian (2027, DATO A CONFIRMAR), cambiar los cinco lugares en el mismo commit. `tools/web.js` ya cruza el mínimo y el máximo. |
| Medio | index.html:99-105 | No había nodo `WebSite`. | **Aplicado:** `WebSite` con `inLanguage` es-CL y `publisher` apuntando al gimnasio. El `VideoObject` también apunta al gimnasio. |
| Medio | index.html:1485 | El enlace «Compartir con un amigo» mandaba a `ultrasport19-boop.github.io/US19/`, que redirige. | **Aplicado:** ahora manda a `https://ultrasport19.com/`. |
| Medio | sitemap.xml | Fecha 14-sep; imágenes `hero.jpg`, `sala-1.jpg` y `sala-2.jpg`, que ya no salen en la portada; `image:title` (Google dejó de leerlo en 2022). | **Aplicado:** fecha 2026-10-31 (último commit de la portada y de la tienda) y las 6 fotos que se ven hoy. Se mantiene el video. |
| Medio | robots.txt:3 | `Disallow: /privacidad.html` impedía que Google viera el `noindex` de esa página, así que podía indexar la URL sin contenido. | **Aplicado:** se quitó la línea. El `noindex,follow` de privacidad hace el trabajo. |
| Bajo | tienda/index.html:2, sorteo/index.html:2, ficha/index.html:2, ficha/index_imprimible.html:2 | `lang="es"`, frente a `es-CL` en la portada. | **Aplicado:** `es-CL`. |
| Bajo | tienda/index.html:34 | El `Store` de la tienda no está ligado al gimnasio. | **Propuesto:** añadir `"parentOrganization":{"@id":"https://ultrasport19.com/#gimnasio"}`. No se aplicó porque `tools/tienda.js` ya falla por otro motivo. |
| Bajo | index.html:16, 24 | El og:title y el twitter:title no llevan «fuerza». | **Propuesto, opcional:** «Ultra-Sport19 \| Gimnasio boutique de fuerza en Pencahue». |
| Bajo | index.html:1277 | `img/comunidad-1.jpg` no existe ni en `main` ni en la copia local. La sección «Nuestra comunidad» no se dibuja, porque el `onerror` la borra. | **Propuesto:** subir la foto, con autorización de imagen de quienes aparecen, o quitar la figura. |

### 2. Accesibilidad (WCAG 2.2 AA)

| Impacto | Archivo:línea | Problema | Cambio |
|---|---|---|---|
| Alto | index.html:907 y script | 2.1.1 Teclado: el video del recorrido solo se reproducía con un clic. Sin controles, el `<video>` no recibe el foco. | **Aplicado:** `tabindex="0"`, Enter o Espacio lo reproducen y activan los controles nativos, y el `aria-label` lo indica. |
| Alto | index.html:247-248 | 2.4.3 y 2.4.11: con el menú del celular cerrado (`max-height:0`), el tabulador recorría 10 enlaces invisibles. | **Aplicado:** `visibility:hidden` mientras está cerrado, con una transición que no cambia la animación. Escape cierra el menú y devuelve el foco al botón (línea 1670). |
| Alto | index.html:150, 393, 430, 473, 520, 610, 641 | 1.4.3 Contraste: `--gris-claro #8A98AB` da 2,93:1 sobre blanco y 2,61:1 sobre hielo. Afecta a la letra chica («No constituye diagnóstico médico», fuentes y avisos) y a la columna «Gimnasio masivo». | **Propuesto** (cambia el color): `--gris-claro:#5B6B80` (5,4:1 sobre blanco, 4,85:1 sobre hielo). |
| Medio | index.html:182 (y 319) | 1.4.3: el rojo `#E21C25` en las etiquetas (0,8 rem) da 4,23:1 sobre el fondo hielo `#EEF2F9`. Sobre blanco da 4,74:1 y pasa. | **Propuesto:** en las secciones con fondo hielo, usar `#C8161F` en las etiquetas (5,2:1). El rojo de marca se mantiene en los botones y en lo grande. |
| Medio | index.html:624 | 1.4.3: la etiqueta móvil «Gimnasio masivo» en `#B8C3D1` da 1,78:1. | **Propuesto:** `color:var(--gris)`. |
| Medio | index.html:774, 920, 427, 672 | 2.2.2 Pausar: el video del hero, el reel y las luces BlazePod se mueven más de 5 s sin un botón de pausa. Se respeta «reducir movimiento», pero eso no basta para AA. | **Aplicado en parte:** el reel ahora se queda quieto con «reducir movimiento» (antes solo el hero), y se pausa al salir de pantalla. **Propuesto:** un botón chico «Pausar video» en el hero y otro en el reel. |
| Medio | index.html:650 y script | En el celular, las secciones plegadas (`.plegable`) esconden contenido con `overflow`, pero sus enlaces siguen recibiendo el foco. | **Propuesto:** marcar como `inert` lo que queda bajo el pliegue, o desplegar la sección cuando recibe el foco (`focusin`, que agrega `.abierta`). |
| Medio | index.html:163-164 | 2.4.11: al tabular, el elemento con foco podía quedar bajo la barra fija (72 px) o bajo la barra inferior del celular. | **Aplicado:** `scroll-padding-top` igual a la altura de la barra y `scroll-padding-bottom:84px` en el celular. Reemplaza al `scroll-margin-top` de las secciones, así que las anclas quedan igual. |
| Bajo | index.html:1291-1316 | 4.1.2: el `aria-label="5 de 5 estrellas"` estaba en un `<div>` genérico, y los lectores de pantalla no lo leen. | **Aplicado:** `role="img"`. |
| Bajo | index.html (49 iconos SVG) | Iconos decorativos sin `aria-hidden`. | **Aplicado:** `aria-hidden="true" focusable="false"` en todos. |
| Bajo | index.html:1595 | `aria-label` en un `<div>` sin rol. | **Aplicado:** `role="group"`. |
| Bajo | index.html:1435-1440, 1561 | Saltos en los encabezados: la sección del asistente tiene un `h3` sin `h2`, y el pie usa `h4`. | **Propuesto:** subir «Todo por WhatsApp, a cualquier hora» a `h2`, con la misma clase y el mismo aspecto, y usar `h2` en el pie. |
| Bajo | index.html:838 | En la tabla comparativa, la primera columna es `<td>`, cuando son encabezados de fila. | **Propuesto:** `<th scope="row">`, ajustando los selectores `.vs td:first-child`. |
| Bajo | ficha/index.html:102 | 1.3.5: la fecha de nacimiento no declaraba su propósito. | **Aplicado:** `autocomplete="bday"`. Los formularios de la ficha y de la tienda ya tienen etiquetas bien asociadas. |
| Bajo | index.html:1402 | La pregunta del FAQ habla de «lesión» y «síntomas nuevos». La regla de marca, ante dolor, es «Si el dolor persiste, consulta a un profesional de salud». | **Propuesto, con cuidado:** reformular en tono de prevención y acondicionamiento. Ojo: `tools/web.js` protege la frase «consultar primero a tu médico». Cambiar la frase y la prueba en el mismo commit, con el «sí» de Diego. |

### 3. Velocidad (Core Web Vitals en el celular)

| Impacto | Archivo:línea | Problema | Cambio |
|---|---|---|---|
| Alto | index.html:920 y script | El reel «Así se entrena» (1,8 MB) tenía `autoplay` y se descargaba al abrir la página, aunque está muy abajo. | **Aplicado:** `preload="none"` y parte solo al entrar en pantalla (IntersectionObserver). Comprobado: al abrir no descarga nada y al llegar se reproduce. |
| Alto | index.html:777 | El logo del hero (en el primer pantallazo) pesaba 183 KB: un PNG de 700×797 que se muestra a 220 px. | **Aplicado:** `<picture>` con `logo-hielo-440.webp` (57 KB) y `logo-hielo-440.png` (120 KB) para navegadores antiguos, y `fetchpriority="high"`. El original queda en el repositorio por si otro sistema lo enlaza. |
| Alto | index.html:774 | El video del hero (1 MB, `preload="auto"`) se descarga apenas se abre la página, también con datos móviles. | **Propuesto:** en pantallas de 720 px o menos, o con `navigator.connection.saveData`, mostrar solo la portada `hero-sala.jpg` (56 KB) y cargar el video solo en computador. También recodificar a 720p y a menos de 500 kbps (H.264 CRF 28), o una versión WebM/AV1. |
| Alto | index.html:34-36 | Google Fonts bloquea el primer dibujo: es una hoja CSS externa con 8 archivos de fuente (Anton, Barlow 400/500/600/700/400 itálica, Barlow Condensed 600/700). | **Propuesto:** alojar las fuentes en `/fonts/` en WOFF2 con subconjunto latino, poner `@font-face` en el `<style>`, precargar Anton y Barlow 500, y usar `size-adjust` en la fuente de respaldo para que Anton no mueva el diseño (CLS). Barlow 400 normal parece no usarse; se podría quitar (comprobar). |
| Medio | index.html:890 | La foto de bioimpedancia pesaba 223 KB (953×1271), cuando se muestra a unos 280 px. | **Aplicado:** `sala-bio-640.jpg` (111 KB), con la misma proporción y `width`/`height` actualizados. |
| Medio | img/sala-*.jpg | Las demás fotos ya están en una calidad JPEG cercana a 80. Recomprimirlas casi no ahorra (menos del 6 %). | **Propuesto:** versiones WebP o AVIF con `<picture>` (entre 25 y 40 % menos). Hay que ajustar el CSS de `.foto`, por eso no se aplicó. |
| Medio | media/promo.mp4 | 4,4 MB para 23 s a 848×478. Con `preload="metadata"` está bien, pero cuesta mucho a quien lo reproduce. | **Propuesto:** recodificar a unos 1,5 MB (CRF 26, AAC 96k). |
| Bajo | index.html | 127 KB de HTML (29 KB comprimido) con CSS y JS en línea. Está bien para una página única, porque no hay otras peticiones que bloqueen. | Sin cambio. |
| Bajo | site.webmanifest | El `theme_color` y el `background_color` son `#0b0b0c`; la página usa navy `#102A43`. | **Propuesto:** `#102A43`. |

**Core Web Vitals esperables en el celular (4G, estimación sin medición en terreno; DATO A CONFIRMAR con PageSpeed Insights o Search Console):**

| Métrica | Antes (estimado) | Con la rama | Con todo lo propuesto |
|---|---|---|---|
| LCP (portada del hero o H1) | 2,8 a 3,5 s: el CSS de las fuentes y el logo de 183 KB compiten con la portada | 2,5 a 3 s | menos de 2 s |
| CLS | bajo (las imágenes tienen medidas), pero cuando carga Anton el titular cambia de tamaño | igual | casi 0 con `size-adjust` |
| INP | bueno: JS mínimo | igual | igual |
| Bytes al abrir la página | unos 3,3 MB (video hero 1 MB, reel 1,8 MB, logo 183 KB, fuentes, etc.) | unos 1,4 MB | unos 0,4 MB en el celular |

## Lo que el dueño debe hacer fuera del código

Ordenado por impacto en «gimnasio Pencahue», «entrenamiento de fuerza Pencahue» y «gimnasio Talca personalizado».

1. **Google Business Profile** (el factor n.º 1 en búsquedas locales):
   - Categoría principal «Gimnasio». Secundarias: «Entrenador personal» si corresponde, o «Centro de fitness». DATO A CONFIRMAR cuáles ofrece Google en Chile.
   - Nombre **idéntico** al de la web. Sitio web `https://ultrasport19.com/` (no github.io). Teléfono +56 9 6590 2238.
   - Horario: lunes a viernes, 06:00 a 22:00. Los fines de semana, solo si se atiende con cita.
   - Descripción con «entrenamiento de fuerza» y «Pencahue». Sin lenguaje clínico.
   - Servicios: Plan 2, 3 y 4 veces por semana, y evaluación de bioimpedancia, con los precios que ya están en la web.
   - Fotos reales, de 10 a 20 (sala de fuerza, cardio, rack, fachada y entrada). Subir una o dos nuevas al mes.
   - Publicaciones de Google (una por semana) con el CTA «Escríbenos por WhatsApp».
2. **Reseñas:** seguir pidiendo reseñas con el enlace `g.page/r/CecsBNgcP8uGEAE/review` (ya está en la web) y responderlas todas. Si las reseñas mencionan «fuerza», «Pencahue» o «Talca» de forma natural, ayuda; no hay que pedir palabras concretas.
3. **«Gimnasio Talca personalizado», expectativa realista:** Google ordena las búsquedas locales por cercanía, y Pencahue está a unos 45 minutos de Talca según la web. Una búsqueda hecha desde Talca casi nunca mostrará un gimnasio de Pencahue en el mapa. Lo que sí sirve: (a) una página propia de «entrenamiento de fuerza personalizado» que explique para quién vale el viaje; (b) anuncios de Meta o Google segmentados a Talca, si algún día se decide (DATO A CONFIRMAR); (c) estar en directorios regionales.
4. **Consistencia de nombre, dirección y teléfono:** el mismo nombre, la dirección «Hernando Bravo de Villalba 811, Pencahue» y el mismo teléfono en Instagram, Facebook, Google y los directorios chilenos.
5. **Google Search Console:** verificar `ultrasport19.com` (registro DNS TXT), enviar `https://ultrasport19.com/sitemap.xml`, pedir la indexación de la portada y revisar «Experiencia en la página» y Core Web Vitals después de publicar.
6. **Bing Webmaster Tools:** importar desde Search Console (2 minutos).
7. **Datos que faltan para el JSON-LD (DATO A CONFIRMAR):** latitud y longitud exactas del pin de Google, código postal, y si los fines de semana hay un horario fijo de evaluaciones.
8. **Foto «Nuestra comunidad»** (`img/comunidad-1.jpg`): subirla con la autorización de imagen firmada en la ficha, o decidir quitar la sección.

## Archivos que cambian en la rama

`index.html`, `robots.txt`, `sitemap.xml`, `tienda/index.html`, `sorteo/index.html`, `ficha/index.html`, `ficha/index_imprimible.html` y `tools/mutantes_web.json`. El ancla de ese mutante apuntaba a `img/hero.jpg`, que no está en la portada desde el rediseño del 17-oct: el mutante «una imagen se queda sin alt» no probaba nada, y ahora usa `sala-cardio.jpg`.
Imágenes nuevas: `img/logo-hielo-440.webp`, `img/logo-hielo-440.png` y `img/sala-bio-640.jpg`. Los originales no se tocaron.
Los finales de línea respetan `.gitattributes`: CRLF en la portada, la tienda y el sorteo, y LF en la ficha.

**Para publicar** (cuando Diego levante el bloqueo): revisar este informe, hacer merge de `nube/web-seo-1nov` en `main` y comprobar en `https://ultrasport19.com` con PageSpeed Insights y la prueba de resultados enriquecidos de Google.
