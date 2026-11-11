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
 *     pasa de describir a afirmar, que es justo lo que no puede hacer.
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

/* DOS COSAS DISTINTAS, y confundirlas costo el lote de mutantes entero.

   `src` es el contenido BAJO PRUEBA. `sitio` es el repositorio DE VERDAD.
   Normalmente coinciden, pero tools/mutantes.js ejecuta esta suite contra
   una COPIA de index.html en una carpeta temporal, y a esa copia no la
   acompanan ni las imagenes, ni el video, ni ficha/ ni tienda/.

   Mientras `raiz` fue `path.dirname(ruta)`, la comprobacion de recursos
   resolvia las 13 imagenes contra la carpeta temporal, las daba TODAS por
   rotas y el corredor se plantaba con «la suite ya falla SIN mutar». O sea
   que desde el 9-sep-2026 (commit d8b38fa, el que anadio esa comprobacion)
   estas comprobaciones eran las unicas del ecosistema que nadie verificaba,
   y no se noto porque `node tools/web.js` a secas seguia dando verde.
   La comparacion del telefono con ficha/ y tienda/ se degradaba igual, pero
   en silencio: salia por el `aviso` de «no encuentro», no por un fallo.

   Resolver contra el sitio real NO afloja nada: si un mutante cambia una
   ruta por otra que no existe, se sigue buscando donde de verdad tiene que
   estar y se sigue cazando. */
const sitio = path.join(__dirname, '..');

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
  const p = path.join(sitio, rel);
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

/* --- Los archivos que la pagina pide y no estan ----------------------
   `img/comunidad-1.jpg` se pedia y no existia, y no se veia roto porque
   un `onerror` borra la figura entera: la seccion «Nuestra comunidad»
   simplemente no aparecia en la pagina publicada. Es el fallo tipico de
   esta suite: no se ve mirando la web.

   Se distinguen dos casos a proposito. Sin red de seguridad, un archivo
   que falta deja un icono roto delante del cliente y eso es FALLO. Con
   `onerror`, es un hueco que hay que saber pero que no puede bloquear un
   commit por una foto que todavia no se ha sacado.

   Ojo con las rutas absolutas: `/US19/img/...` SI existe, porque GitHub
   Pages sirve este repositorio bajo `/US19/`. Resolverlas contra el disco
   sin quitar ese prefijo las da por rotas a todas. */
{
  const paginas = fs.readdirSync(sitio).filter(f => f.endsWith('.html'));
  const rotos = [], huecos = [];
  paginas.forEach(function (pag) {
    /* La pagina bajo prueba se lee de `src`, no del disco: es la unica que
       puede venir mutada, y leerla del repositorio devolveria el original. */
    const html = (pag === path.basename(ruta))
      ? src
      : fs.readFileSync(path.join(sitio, pag), 'utf8');
    const re = /(?:src|href|content)="([^"]+\.(?:jpg|jpeg|png|webp|svg|gif|ico|mp4|pdf))"/g;
    let m;
    while ((m = re.exec(html)) !== null) {
      const u = m[1];
      if (/^(https?:)?\/\//.test(u) || u.indexOf('data:') === 0) continue;
      let rel = u;
      if (rel.indexOf('/US19/') === 0) rel = rel.slice(6);   // lo que sirve Pages
      else if (rel.charAt(0) === '/') rel = rel.slice(1);
      if (fs.existsSync(path.join(sitio, rel))) continue;
      /* ¿lleva red de seguridad? Se mira la etiqueta entera, desde el «<»
         anterior hasta el «>» siguiente. */
      const ini = html.lastIndexOf('<', m.index);
      const fin = html.indexOf('>', m.index);
      const etiqueta = html.slice(ini, fin + 1);
      (etiqueta.indexOf('onerror') >= 0 ? huecos : rotos).push(pag + ' → ' + u);
    }
  });

  comprobar('recursos · ningun archivo roto queda a la vista del cliente',
    rotos.length === 0,
    rotos.join('  ·  ') + ' (sin onerror: se ve el icono roto)');

  if (huecos.length)
    aviso('recursos · ' + huecos.length + ' archivo(s) que faltan pero degradan solos: '
      + huecos.join(', ') + ' — la seccion no se dibuja');
  else
    aviso('recursos · todos los archivos que la web pide existen');
}

/* --- Los precios fechados: 2026 hasta el 31-dic, 2027 desde el 1-ene -----
   El 1-ene-2027 a las 00:00 DE CHILE los planes pasan de 15/25/35 mil a
   20/25/30 mil (clientes nuevos y los que vuelven; lo publico no distingue
   a los antiguos). El HTML estatico trae los vigentes hoy y el script
   `us19-precios` cambia de tramo con la fecha de Chile.

   Lo que se rompe callado:
     · que el script mire UTC o la hora del equipo: entre las 21:00 del
       31-dic (UTC) y la medianoche de Chile mostraria el precio nuevo, o al
       reves, segun donde este el visitante;
     · que el HTML estatico, el JSON-LD (lo que lee Google) y el boton de
       compartir digan precios distintos de las tarjetas.
   Por eso aqui se ejecuta el script DE VERDAD (vm) contra un documento de
   mentira armado con el propio HTML, con instantes a ambos lados del cambio. */
{
  const vm = require('vm');
  const bloque = /<script id="us19-precios">([\s\S]*?)<\/script>/.exec(src);
  comprobar('precios fechados · la página trae el script us19-precios', !!bloque);

  const fmt = n => '$' + String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  const estaticos = {};
  [...src.matchAll(/<span data-precio-plan="(\d)">\$(\d{1,3})\.(\d{3})<\/span>/g)]
    .forEach(m => { estaticos[m[1]] = parseInt(m[2] + m[3], 10); });
  igual('precios fechados · las 3 tarjetas llevan su precio marcado (2x, 3x, 4x)',
    Object.keys(estaticos).sort().join(','), '2,3,4');

  /* El JSON-LD estatico: makesOffer tiene que decir lo mismo que las tarjetas. */
  if (gym) {
    const ofertas = {};
    (gym.makesOffer || []).forEach(o => {
      const m = /^Plan (\d) veces/.exec(o.name || '');
      if (m) ofertas[m[1]] = parseInt(o.price, 10);
    });
    igual('precios · las ofertas del JSON-LD (makesOffer) son las de las tarjetas',
      JSON.stringify(ofertas), JSON.stringify(estaticos));
  }

  /* El boton de compartir: su texto y su enlace dicen el plan mas barato. */
  const share = /<a class="share reveal" id="share" data-texto="([^"]*)" href="([^"]*)"/.exec(src);
  comprobar('precios · el botón de compartir lleva data-texto y href', !!share);
  if (share && Object.keys(estaticos).length) {
    const min = Math.min.apply(null, Object.values(estaticos));
    comprobar('precios · el texto de compartir dice «desde» el plan más barato',
      share[1].indexOf('desde ' + fmt(min) + '.') >= 0, share[1]);
    igual('precios · el enlace de compartir es ese mismo texto',
      share[2], 'https://wa.me/?text=' + encodeURIComponent(share[1] + ' https://ultrasport19.com/'));
  }

  if (bloque) {
    /* Documento de mentira: solo lo que el script toca, sacado del HTML. */
    function documento() {
      const precios = [...src.matchAll(/<span data-precio-plan="(\d)">([^<]*)<\/span>/g)]
        .map(m => ({ attrs: { 'data-precio-plan': m[1] }, textContent: m[2],
          getAttribute(k) { return this.attrs[k]; } }));
      const lds = bloques.map(b => ({ textContent: b[1] }));
      const sh = share ? { attrs: { 'data-texto': share[1], href: share[2] },
        getAttribute(k) { return this.attrs[k]; }, setAttribute(k, v) { this.attrs[k] = v; } } : null;
      return {
        precios, lds, sh,
        querySelectorAll(sel) {
          if (sel === '[data-precio-plan]') return precios;
          if (sel === 'script[type="application/ld+json"]') return lds;
          throw new Error('selector no previsto en la prueba: ' + sel);
        },
        getElementById(id) { return id === 'share' ? sh : null; },
      };
    }
    const docCarga = documento();
    const ventana = {};
    let error = null;
    try { vm.runInNewContext(bloque[1], { window: ventana, document: docCarga }); }
    catch (e) { error = e.message; }
    comprobar('precios fechados · el script corre sin errores', !error, error);
    const P = ventana.US19_PRECIOS;
    comprobar('precios fechados · el script publica window.US19_PRECIOS', !!P);

    if (P) {
      const V26 = { 2: 15000, 3: 25000, 4: 35000 };
      const V27 = { 2: 20000, 3: 25000, 4: 30000 };
      const plano = o => [o[2], o[3], o[4]].join('/');
      /* [instante UTC, que dia es en Chile, precios esperados]
         Chile en enero esta en UTC-3: la medianoche del 1-ene son las 03:00Z.
         El 02:30Z ya es 2027 en UTC y sigue siendo 31-dic en Chile: es el
         caso que caza a un script que mire UTC en vez de America/Santiago. */
      const CASOS = [
        ['2026-11-11T15:00:00Z', '2026-11-11', V26, 'hoy (noviembre 2026)'],
        ['2026-12-31T12:00:00Z', '2026-12-31', V26, '31-dic a mediodia'],
        ['2027-01-01T02:30:00Z', '2026-12-31', V26, '31-dic 23:30 en Chile (ya es 1-ene en UTC)'],
        ['2027-01-01T02:59:59Z', '2026-12-31', V26, '31-dic 23:59:59 en Chile'],
        ['2027-01-01T03:00:00Z', '2027-01-01', V27, '1-ene 00:00 en Chile'],
        ['2027-01-01T15:00:00Z', '2027-01-01', V27, '1-ene a mediodia'],
        ['2027-07-15T12:00:00Z', '2027-07-15', V27, 'invierno 2027 (UTC-4)'],
      ];
      CASOS.forEach(([iso, dia, esp, que]) => {
        const d = new Date(iso);
        igual('precios fechados · ' + que + ' es ' + dia + ' en Chile', P.hoyChile(d), dia);
        igual('precios fechados · ' + que + ' → ' + plano(esp), plano(P.vigentes(d)), plano(esp));
      });

      /* El HTML estatico tiene que ser el vigente HOY. Si esto falla despues
         del 1-ene-2027, toca pasar el HTML (tarjetas, JSON-LD, compartir) a
         los precios 2027: quien no ejecuta JS sigue viendo los viejos. */
      igual('precios fechados · el HTML estático muestra los precios vigentes hoy en Chile ('
        + P.hoyChile(new Date()) + ')', plano(estaticos), plano(P.vigentes(new Date())));

      /* Y aplicado sobre el documento: tarjetas, JSON-LD y compartir. */
      [['2027-01-01T02:59:59Z', V26, '31-dic 23:59:59'], ['2027-01-01T03:00:00Z', V27, '1-ene 00:00']]
        .forEach(([iso, esp, que]) => {
          const doc = documento();
          let err = null;
          try { P.aplicar(doc, new Date(iso)); } catch (e) { err = e.message; }
          comprobar('precios aplicados · ' + que + ' · sin errores', !err, err);
          const tarjetas = {};
          doc.precios.forEach(e => { tarjetas[e.attrs['data-precio-plan']] = e.textContent; });
          igual('precios aplicados · ' + que + ' · tarjetas',
            [tarjetas[2], tarjetas[3], tarjetas[4]].join(' '), [fmt(esp[2]), fmt(esp[3]), fmt(esp[4])].join(' '));
          const min = Math.min(esp[2], esp[3], esp[4]), max = Math.max(esp[2], esp[3], esp[4]);
          let g = null;
          doc.lds.forEach(l => { try { const j = JSON.parse(l.textContent); if (j['@type'] === 'ExerciseGym') g = j; } catch (e) { /* lo cuenta abajo */ } });
          comprobar('precios aplicados · ' + que + ' · el JSON-LD sigue siendo JSON válido', !!g);
          if (g) {
            igual('precios aplicados · ' + que + ' · priceRange', g.priceRange, fmt(min) + ' - ' + fmt(max) + ' CLP');
            const ofertas = {};
            (g.makesOffer || []).forEach(o => { const m = /^Plan (\d) veces/.exec(o.name || ''); if (m) ofertas[m[1]] = o.price; });
            igual('precios aplicados · ' + que + ' · makesOffer',
              [ofertas[2], ofertas[3], ofertas[4]].join('/'), [esp[2], esp[3], esp[4]].join('/'));
            const bio = (g.makesOffer || []).find(o => /bioimpedancia/i.test(o.name || ''));
            igual('precios aplicados · ' + que + ' · la bioimpedancia no se toca', bio && bio.price, '5000');
          }
          if (doc.sh) {
            comprobar('precios aplicados · ' + que + ' · compartir dice desde ' + fmt(min),
              doc.sh.attrs['data-texto'].indexOf('desde ' + fmt(min) + '.') >= 0, doc.sh.attrs['data-texto']);
            igual('precios aplicados · ' + que + ' · el enlace de compartir lleva ese texto',
              doc.sh.attrs.href, 'https://wa.me/?text=' + encodeURIComponent(doc.sh.attrs['data-texto'] + ' https://ultrasport19.com/'));
          }
        });
      aviso('precios fechados · hoy en Chile (' + P.hoyChile(new Date()) + '): ' + plano(P.vigentes(new Date()))
        + '  ·  desde 2027-01-01: ' + plano(P.vigentes(new Date('2027-01-01T03:00:00Z'))));
    }
  }
}

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
