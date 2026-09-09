/* =====================================================================
 * US19 · la web pública, comprobada contra sí misma
 *
 *   node tools/web.js [ruta/index.html]
 *
 * Es la puerta de entrada: el bot la manda en siete puntos del flujo y es
 * lo que ve quien llega de Instagram. Sus fallos no se ven mirando la
 * página —se ve preciosa igual— sino en lo que dice de sí misma:
 *
 *   · Un JSON-LD roto no da error en pantalla. Simplemente Google deja de
 *     enseñar horarios, precio y teléfono, y nadie lo nota en meses.
 *   · Un ancla que apunta a una sección renombrada no avisa: el botón
 *     «Ver planes» se queda quieto y parece que la web está rota.
 *   · Si el horario del JSON-LD y el de la página dejan de coincidir,
 *     Google enseña uno y el cliente lee otro.
 *   · Y si alguien quita «No constituye diagnóstico médico», la página
 *     pasa de describir a afirmar — con Diego todavía de interno.
 *
 * Nada de lo que hay aquí inventa datos: cada cifra se compara contra lo
 * que la propia página dice en su texto visible.
 *
 * Regla de oro: si algo no se encuentra, esto FALLA.
 * ===================================================================== */

const fs = require('fs');
const path = require('path');

const ruta = process.argv[2] || path.join(__dirname, '..', 'index.html');
const src = fs.readFileSync(ruta, 'utf8');
const raiz = path.dirname(ruta);

let ok = 0;
const fallos = [], avisos = [];
const pasa = () => ok++;
const falla = (n, d) => fallos.push(n + (d ? '  →  ' + d : ''));
const comprobar = (n, c, d) => { if (c) pasa(); else falla(n, d); };
const igual = (n, a, b) => {
  if (a === b) pasa();
  else falla(n, 'esperaba ' + JSON.stringify(b) + ', obtuvo ' + JSON.stringify(a));
};
const aviso = t => avisos.push(t);
function abortar(motivo) {
  console.log('\nUS19 · web pública\narchivo: ' + ruta + '\n\n  ✗ ' + motivo + '\n');
  process.exit(1);
}

/* El texto que un cliente lee de verdad: sin scripts, sin estilos, sin
   etiquetas. Todo lo de abajo se compara contra esto, no contra el HTML. */
const visible = src
  .replace(/<script[\s\S]*?<\/script>/gi, ' ')
  .replace(/<style[\s\S]*?<\/style>/gi, ' ')
  .replace(/<[^>]+>/g, ' ')
  .replace(/&nbsp;/g, ' ')
  .replace(/\s+/g, ' ');

/* --- 1 · Lo que la página le cuenta a Google ------------------------- */

const bloques = [...src.matchAll(/<script[^>]*type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/gi)];
comprobar('datos estructurados · la página los trae', bloques.length >= 2, bloques.length + ' bloques');
if (!bloques.length) abortar('sin JSON-LD no hay nada que comprobar aquí');

const datos = [];
bloques.forEach((b, i) => {
  try { datos.push(JSON.parse(b[1])); pasa(); }
  catch (e) { falla('datos estructurados · el bloque ' + (i + 1) + ' es JSON válido', e.message); }
});

const gym = datos.find(d => d && d['@type'] === 'ExerciseGym');
if (!gym) falla('datos estructurados · hay una ficha de gimnasio (ExerciseGym)');
else {
  /* El teléfono que Google enseña tiene que estar en la página. Si no,
     alguien lo cambió en un sitio y no en el otro. */
  const tel = String(gym.telephone || '').replace(/\D/g, '');
  comprobar('coherencia · el teléfono del JSON-LD está escrito en la página',
    tel.length >= 8 && visible.replace(/\D/g, '').indexOf(tel) >= 0, gym.telephone);

  /* El horario, igual: Google enseña uno y el cliente lee otro. */
  const h = (gym.openingHoursSpecification || [])[0] || {};
  const abre = String(h.opens || ''), cierra = String(h.closes || '');
  comprobar('coherencia · la hora de apertura del JSON-LD sale en la página',
    !!abre && visible.indexOf(abre) >= 0, abre);
  comprobar('coherencia · y la de cierre también',
    !!cierra && visible.indexOf(cierra) >= 0, cierra);
  const dias = (h.dayOfWeek || []).length;
  comprobar('coherencia · el JSON-LD declara los días que abre', dias > 0, JSON.stringify(h.dayOfWeek));
  aviso('horario declarado: ' + dias + ' días, ' + abre + '–' + cierra);

  /* El rango de precios contra los precios que se ven. Nada inventado:
     los extremos salen del propio texto. */
  /* Solo los precios de PLANES: los que van seguidos de «por mes» o «al
     mes». Sin ese filtro entraban los $5.000 de la bioimpedancia para
     público general, que no es un plan y hundía el mínimo. */
  const precios = [...visible.matchAll(/\$\s?(\d{1,3})\.(\d{3})\s*(?:por mes|al mes)/gi)]
    .map(m => parseInt(m[1] + m[2], 10));
  comprobar('precios · la página muestra precios de planes con su periodicidad',
    precios.length >= 2, precios.join(', ') + '  (se buscan los que dicen «por mes» o «al mes»)');
  if (precios.length >= 2 && gym.priceRange) {
    const rango = [...String(gym.priceRange).matchAll(/(\d{1,3})\.(\d{3})/g)]
      .map(m => parseInt(m[1] + m[2], 10));
    igual('precios · el mínimo del JSON-LD es el plan más barato de la página',
      rango[0], Math.min.apply(null, precios));
    comprobar('precios · el máximo del JSON-LD no es menor que el plan más caro',
      rango[1] >= Math.max.apply(null, precios),
      'JSON-LD ' + rango[1] + ' vs pagina ' + Math.max.apply(null, precios));
    aviso('precios en la pagina: ' + [...new Set(precios)].sort((a, b) => a - b).join(' · '));
  }
}

/* --- 2 · Los enlaces internos, que fallan callados ------------------- */

const ids = new Set();
(src.match(/\bid="[A-Za-z0-9_-]+"/g) || []).forEach(t => ids.add(t.slice(4, -1)));
const anclas = [...new Set((src.match(/href="#[A-Za-z0-9_-]+"/g) || []).map(t => t.slice(7, -1)))];
comprobar('enlaces · la página tiene navegación interna', anclas.length >= 5, anclas.length + ' anclas');
const rotas = anclas.filter(a => !ids.has(a));
igual('enlaces · ningún ancla apunta a una sección que ya no existe', rotas.join(', '), '');

/* Y los ids que el script pide, igual que en la tienda y en la ficha. */
const js = [...src.matchAll(/<script(?![^>]*type="application\/ld\+json")[^>]*>([\s\S]*?)<\/script>/gi)]
  .map(m => m[1]).join('\n');
const pedidos = [...new Set(
  (js.match(/getElementById\(\s*['"][A-Za-z0-9_-]+['"]\s*\)/g) || [])
    .map(t => t.replace(/.*['"]([A-Za-z0-9_-]+)['"].*/, '$1'))
)];
comprobar('marcado · el script pide elementos por id', pedidos.length > 0);
const sinId = pedidos.filter(id => !ids.has(id));
igual('marcado · el script no pide ningún id que ya no esté en la página', sinId.join(', '), '');

/* --- 3 · El número del asistente, el mismo en las tres páginas ------- */

const numeros = [...new Set((src.match(/wa\.me\/(\d{9,})/g) || []).map(t => t.split('/')[1]))];
comprobar('contacto · la página enlaza a WhatsApp', numeros.length > 0);
['ficha/index.html', 'tienda/index.html'].forEach(rel => {
  const p = path.join(raiz, rel);
  if (!fs.existsSync(p)) { aviso('no encuentro ' + rel + ': no comparo el número con esa página'); return; }
  const otra = fs.readFileSync(p, 'utf8');
  const suyos = [...new Set((otra.match(/\b(569\d{8})\b/g) || []))];
  const comunes = suyos.filter(n => numeros.indexOf(n) >= 0);
  comprobar('contacto · el número del asistente coincide con ' + rel,
    comunes.length > 0, 'web: ' + numeros.join(', ') + '  ·  ' + rel + ': ' + suyos.join(', '));
});

/* --- 4 · Lo que protege a Diego mientras es interno ------------------ */
/* No se prohíben las palabras: la página las usa BIEN, negando. Lo que
   no puede desaparecer son las frases que hacen que sea una negación. */

const PROTEGEN = [
  ['la bioimpedancia no se vende como diagnóstico', /no constituye diagn[oó]stico m[eé]dico/i],
  ['ante una molestia se remite al médico',          /consultar primero a tu m[eé]dico/i],
];
PROTEGEN.forEach(([queEs, re]) => {
  comprobar('salvaguarda · ' + queEs, re.test(visible),
    'esa frase es lo que convierte una descripción en una negación; sin ella la página afirma');
});

/* Tripwire: términos clínicos que NO estén dentro de una de las frases
   conocidas y revisadas. Si aparece uno nuevo, hay que mirarlo a mano. */
const CONOCIDAS = [
  /no constituye diagn[oó]stico m[eé]dico/gi,
  /lesiones, molestias, experiencia previa/gi,
  /¿puedo entrenar si tengo una molestia o lesi[oó]n\?/gi,
  /si hay dolor agudo, lesi[oó]n reciente o s[ií]ntomas nuevos/gi,
];
let restante = visible;
CONOCIDAS.forEach(re => { restante = restante.replace(re, ' '); });
const CLINICO = /\b(diagn[oó]stic\w*|tratamiento\w*|rehabilitaci\w*|paciente\w*|patolog\w*|terapia\w*|kinesi[oó]log\w*|fisioterap\w*|d[eé]ficit)\b/gi;
const nuevos = [...new Set((restante.match(CLINICO) || []).map(s => s.toLowerCase()))];
igual('vocabulario · no aparece lenguaje clínico fuera de las frases ya revisadas',
  nuevos.join(', '), '');

/* --- 5 · Higiene que se nota cuando falta --------------------------- */

const imgs = [...src.matchAll(/<img\b[^>]*>/gi)].map(m => m[0]);
const sinAlt = imgs.filter(t => !/\balt\s*=/.test(t));
comprobar('accesibilidad · todas las imágenes llevan alt', sinAlt.length === 0,
  sinAlt.slice(0, 2).map(t => t.slice(0, 70)).join(' | '));

const externos = [...src.matchAll(/<a\b[^>]*href="https?:\/\/[^"]*"[^>]*>/gi)].map(m => m[0]);
const conBlank = externos.filter(t => /target="_blank"/i.test(t));
const sinNoopener = conBlank.filter(t => !/rel="[^"]*noopener/i.test(t));
comprobar('seguridad · los enlaces que abren pestaña llevan rel="noopener"',
  sinNoopener.length === 0, sinNoopener.slice(0, 2).map(t => t.slice(0, 80)).join(' | '));
aviso(imgs.length + ' imágenes · ' + externos.length + ' enlaces externos, ' + conBlank.length + ' en pestaña nueva');

/* --- El telefono: uno solo, y el del bot -----------------------------
   El 9-sep-2026 la pagina publicaba DOS numeros: los 18 botones de accion
   llevaban al asistente y el JSON-LD —lo que lee Google— mas la seccion
   Contacto llevaban al movil PERSONAL de Diego.

   No daba ningun error. Simplemente, quien pulsaba el telefono en la ficha
   de Google le escribia a Diego: sin ficha, sin portero, sin registro. Esa
   persona no entraba al sistema y nadie se enteraba. */

const telsWa = [...new Set((src.match(/wa\.me\/(\d{9,15})/g) || []).map(t => t.split("/")[1]))];
const telLd  = gym && gym.telephone ? String(gym.telephone).replace(/[^0-9]/g, "") : "";

comprobar('telefono · la pagina lleva a algun WhatsApp', telsWa.length > 0);
igual('telefono · TODOS los enlaces de WhatsApp van al mismo numero',
  telsWa.length, 1);
if (telsWa.length > 1) {
  falla('telefono · los numeros distintos que aparecen', telsWa.join(" y ") +
    '. El que no sea el del asistente recibe gente que no entra al sistema');
}

comprobar('telefono · el JSON-LD declara un telefono', !!telLd,
  'sin el, Google no muestra numero en la ficha del negocio');
if (telLd && telsWa.length) {
  igual('telefono · el que ve Google es el mismo de los botones',
    telLd, telsWa[0]);
}
if (telLd) aviso('telefono · uno solo en toda la pagina, y es el del asistente');

/* --- salida ---------------------------------------------------------- */

console.log('\nUS19 · web pública');
console.log('archivo: ' + ruta + '\n');
avisos.forEach(a => console.log('  · ' + a));
console.log('');
if (fallos.length) {
  console.log('FALLOS (' + fallos.length + '):');
  fallos.forEach(f => console.log('  ✗ ' + f));
  console.log('\ncomprobaciones OK: ' + ok + '  ·  FALLIDAS: ' + fallos.length);
  process.exit(1);
}
console.log('comprobaciones OK: ' + ok + '  ·  sin fallos');
process.exit(0);
