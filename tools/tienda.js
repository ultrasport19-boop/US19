/* =====================================================================
 * US19 · la tienda, ejecutada de verdad
 *
 *   node tools/tienda.js [ruta/tienda/index.html]
 *
 * Saca el <script> de la pagina, le monta un navegador de mentira
 * alrededor (document, localStorage, fetch, AbortController) y hace el
 * viaje del comprador: catalogo normal, catalogo vacio, Notion caido, la
 * red que no contesta, el carro que sobrevive, el tope por pedido y el
 * mensaje que acaba en WhatsApp.
 *
 * Existe porque esta pagina es lo UNICO que ve alguien que llega desde
 * Instagram, y porque sus fallos no se ven mirando el codigo: se ven el
 * dia que Apps Script tarda cinco segundos o que Notion devuelve un 500.
 *
 * Regla de oro: si algo no se encuentra, esto FALLA. Nunca pasa en verde
 * por no haber mirado.
 * ===================================================================== */

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ruta = process.argv[2] || path.join(__dirname, '..', 'tienda', 'index.html');
const src = fs.readFileSync(ruta, 'utf8');

let ok = 0;
const fallos = [], avisos = [];
const pasa = () => ok++;
const falla = (n, d) => fallos.push(n + (d ? '  →  ' + d : ''));
const comprobar = (n, c, d) => { if (c) pasa(); else falla(n, d); };
const igual = (n, a, b) => {
  if (a === b) pasa();
  else falla(n, 'esperaba ' + JSON.stringify(b) + ', obtuvo ' + JSON.stringify(a));
};
function abortar(motivo) {
  console.log('\nUS19 · tienda\narchivo: ' + ruta + '\n\n  ✗ ' + motivo + '\n');
  process.exit(1);
}

/* --- 1 · Sacar el script de la pagina ------------------------------- */

const m = src.match(/<script>([\s\S]*?)<\/script>/);
if (!m) abortar('no encuentro el bloque <script> en la pagina');
const codigo = m[1];

['function cargar(', 'function aplicar(', 'function pintar(', 'function reconciliar(',
 'function pedirCatalogo(', 'function esc(', 'function mensaje('].forEach(function (f) {
  if (codigo.indexOf(f) < 0) abortar('el script no contiene ' + f + ')  ¿se renombro?');
});

/* --- 1 bis · Los ids, sacados de la pagina ---------------------------
   Esta suite tenia un agujero que encontro la auditoria del 8-sep: la
   lista de ids del DOM de mentira estaba escrita A MANO, asi que
   renombrar `id="pronto"` en la pagina pasaba en VERDE — el navegador
   falso devolvia un elemento para un id que ya no existia.
   Ahora los ids salen del marcado, y el DOM falso devuelve null para
   cualquier otro, igual que un navegador de verdad. */

const idsPagina = new Set();
(src.match(/\bid="[A-Za-z0-9_-]+"/g) || []).forEach(function (t) {
  idsPagina.add(t.slice(4, -1));
});
const idsPedidos = new Set();
(codigo.match(/\$\(\s*['"][A-Za-z0-9_-]+['"]\s*\)/g) || []).forEach(function (t) {
  idsPedidos.add(t.replace(/^\$\(\s*['"]/, '').replace(/['"]\s*\)$/, ''));
});
if (!idsPedidos.size) abortar('el script no pide ningun elemento por id: ¿cambio el ayudante $()?');

const huerfanos = [...idsPedidos].filter(id => !idsPagina.has(id));
/* Aborta en vez de anotar el fallo y seguir. Sin ese elemento, todo lo que
   viene despues revienta con un TypeError que no explica nada; asi se dice
   cual es el id y donde mirar. */
if (huerfanos.length) {
  abortar('el script pide elementos que ya no estan en el marcado: ' + huerfanos.join(', ')
    + '\n    ¿se renombro un id en la pagina y no en el <script>?');
}
pasa();
const sinUsar = [...idsPagina].filter(id => !idsPedidos.has(id));
if (sinUsar.length) aviso('ids en la pagina que el script no usa: ' + sinUsar.join(', '));

/* La pagina y el bot tienen que hablar del mismo tope. Antes estaba
   escrito a mano en los dos sitios. */
comprobar('contrato · el tope por pedido lo manda el catalogo',
  /d\.maxPedido/.test(codigo),
  'si vuelve a estar fijo en la pagina, cambiar el del bot no sirve de nada');

/* --- 1 ter · EL CONTRATO ENTERO, CONTRA EL CÓDIGO DEL BOT -----------
   Arriba solo se ataba el tope. Los otros nueve campos no los miraba
   nadie, y es el mismo fallo silencioso que ya tiene su prueba en
   `ficha.js`: el bot renombra `precio` -> `precioCLP` en
   `US19_TIENDA_leer_`, la pagina sigue leyendo `p.precio`, y la tienda se
   ve entera con toda la ropa a $0. No hay error en ninguna consola, ni en
   el registro del bot, ni en Notion. Se descubre cuando alguien pregunta
   por WhatsApp por que la ropa sale gratis.

   Los dos lados viven en repositorios distintos y nada los ataba.

   La pagina tiene una convencion firme: `p` es siempre una prenda y `d` es
   siempre el payload del catalogo. Si esto falla, es que se renombro un
   campo en el bot... o que alguien uso `p`/`d` para otra cosa. Las dos
   merecen mirarse. */

const RUTA_BOT = process.env.US19_BOT
  || path.join('C:', 'Users', 'diego', 'OneDrive', 'Documentos',
               'RESPALDO_ASISTENTE_APPSSCRIPT', 'proyecto_clasp', 'Código.js');

if (!fs.existsSync(RUTA_BOT)) {
  avisos.push('CONTRATO SIN COMPROBAR: no encuentro el Código.js del asistente en ' + RUTA_BOT
    + '. Es el repositorio del bot, que no viaja con este. Con la variable US19_BOT se le puede dar otra ruta.');
} else {
  const bot = fs.readFileSync(RUTA_BOT, 'utf8');

  /* Se corta desde la funcion que interesa: `out.push({` aparece en varios
     sitios del Código.js y el primero no tiene por que ser este. */
  const iLeer = bot.indexOf('function US19_TIENDA_leer_');
  comprobar('contrato · el bot sigue teniendo US19_TIENDA_leer_', iLeer >= 0,
    'es la funcion que arma cada prenda del catalogo');
  const trozoLeer = iLeer >= 0 ? bot.slice(iLeer) : '';

  /* Lo que el bot manda por prenda: el objeto del `out.push({...})`. */
  const mPrenda = /out\.push\(\{([\s\S]*?)\n\s*\}\);/.exec(trozoLeer);
  comprobar('contrato · encuentro el objeto que el bot manda por prenda',
    !!mPrenda, 'busco el out.push({...}) de US19_TIENDA_leer_ — ¿se reescribio?');

  /* Y lo que manda envolviendo: el JSON.stringify del catalogo, mas los
     dos campos que solo aparecen cuando algo va mal. */
  const mSobre = /var payload = JSON\.stringify\(\{([\s\S]*?)\n\s*\}\);/.exec(bot);
  comprobar('contrato · encuentro el sobre del catalogo',
    !!mSobre, 'busco el var payload = JSON.stringify({...}) de US19_TIENDA_catalogo_');

  if (mPrenda && mSobre) {
    const claves = txt => {
      const out = new Set(), re = /(?:^|\n)\s*([a-zA-Z_$][\w$]*)\s*:/g;
      let c; while ((c = re.exec(txt)) !== null) out.add(c[1]);
      return out;
    };
    const dePrenda = claves(mPrenda[1]);
    const deSobre  = claves(mSobre[1]);
    /* `error` y `respaldo` no estan en el sobre normal: los pone el bot
       solo cuando Notion falla, y la pagina los lee para decirlo. */
    /* Los dos se ponen de formas distintas: `error` es una clave del objeto
       de emergencia y `respaldo` una asignacion sobre el sobre ya parseado
       (`o.respaldo = true`). Se aceptan las dos formas a proposito. */
    ['error', 'respaldo'].forEach(k => {
      comprobar('contrato · el bot sigue marcando «' + k + '» cuando Notion falla',
        new RegExp('[.\\s{]' + k + '\\s*[:=]\\s*true').test(bot),
        'la pagina lo lee para avisar de que el catalogo puede estar viejo');
      deSobre.add(k);
    });

    /* `p` no es SIEMPRE una prenda: en algun sitio es un array y se le
       llama `p.push`, `p.length`, `p.join`. Se descartan los miembros
       propios del lenguaje. El precio de esta lista es que un campo del
       catalogo que se llamara `length` pasaria sin mirar — no va a pasar,
       y es mejor que una prueba que grita por un `.push`. */
    const DEL_LENGUAJE = new Set(['push', 'pop', 'shift', 'unshift', 'length', 'join',
      'map', 'filter', 'forEach', 'indexOf', 'lastIndexOf', 'slice', 'splice', 'concat',
      'sort', 'reverse', 'includes', 'some', 'every', 'find', 'findIndex', 'reduce',
      'trim', 'toLowerCase', 'toUpperCase', 'replace', 'split', 'charAt', 'substring',
      'substr', 'startsWith', 'endsWith', 'padStart', 'padEnd', 'repeat', 'match',
      'toString', 'valueOf', 'hasOwnProperty', 'toFixed', 'toLocaleString']);
    const leidos = campo => {
      const out = new Set(), re = new RegExp('\\b' + campo + '\\.([a-zA-Z_$][\\w$]*)', 'g');
      let c; while ((c = re.exec(codigo)) !== null) if (!DEL_LENGUAJE.has(c[1])) out.add(c[1]);
      return out;
    };
    const huerfanos = [];
    leidos('p').forEach(k => { if (!dePrenda.has(k)) huerfanos.push('p.' + k); });
    leidos('d').forEach(k => { if (!deSobre.has(k))  huerfanos.push('d.' + k); });

    comprobar('contrato · todo lo que la pagina lee, el bot lo manda',
      huerfanos.length === 0,
      'la pagina lee ' + huerfanos.join(', ') + ' y el bot no lo manda. ' +
      'Campos del bot: prenda {' + [...dePrenda].join(', ') + '}  sobre {' + [...deSobre].join(', ') + '}');

    avisos.push('contrato comprobado contra el Código.js del asistente (' +
      dePrenda.size + ' campos por prenda, ' + deSobre.size + ' en el sobre)');
  }
}

/* --- 2 · Un navegador de mentira ------------------------------------ */

function nuevoElemento(id) {
  return {
    id, innerHTML: '', textContent: '', hidden: false, className: '', href: '',
    _attrs: {},
    setAttribute(k, v) { this._attrs[k] = String(v); },
    getAttribute(k) { return Object.prototype.hasOwnProperty.call(this._attrs, k) ? this._attrs[k] : null; },
    hasAttribute(k) { return Object.prototype.hasOwnProperty.call(this._attrs, k); },
    addEventListener(ev, fn) { (this._ev = this._ev || {})[ev] = fn; },
    querySelector() { return null; },
    querySelectorAll() { return []; },
    insertAdjacentHTML() {},
    remove() {},
  };
}

function nuevoEntorno(respuestas, opciones) {
  opciones = opciones || {};
  const els = {};
  const store = {};
  /* Solo existen los ids que estan de verdad en la pagina. Si uno se
     renombra en el marcado, aqui devuelve null y la prueba que lo usaba
     se cae — que es justo lo que antes no pasaba. */
  idsPagina.forEach(function (id) { els[id] = nuevoElemento(id); });

  let handlerClick = null;
  let handlerVis = null;
  let handlerChange = null;
  let nPeticiones = 0;
  const irA = [];

  const document = {
    getElementById(id) { return els[id] || null; },
    addEventListener(ev, fn) {
      if (ev === 'click') handlerClick = fn;
      if (ev === 'visibilitychange') handlerVis = fn;
      if (ev === 'change') handlerChange = fn;
    },
    visibilityState: 'visible',
  };

  const localStorage = {
    getItem(k) { return Object.prototype.hasOwnProperty.call(store, k) ? store[k] : null; },
    setItem(k, v) { store[k] = String(v); },
    removeItem(k) { delete store[k]; },
  };
  if (opciones.store) Object.keys(opciones.store).forEach(k => { store[k] = opciones.store[k]; });

  /* fetch de mentira: `respuestas` es una lista; cada llamada consume una.
     Un elemento Error significa «la red fallo»; un numero, «tardo tanto». */
  function fetchFalso() {
    const r = respuestas[Math.min(nPeticiones, respuestas.length - 1)];
    nPeticiones++;
    if (r instanceof Error) return Promise.reject(r);
    return Promise.resolve({ json: () => Promise.resolve(r) });
  }

  const location = { hash: opciones.hash || '', pathname: '/US19/tienda/', search: '', href: '' };
  Object.defineProperty(location, 'href', {
    get() { return irA[irA.length - 1] || ''; },
    set(v) { irA.push(v); },
  });

  const ctx = {
    document, localStorage, fetch: fetchFalso, location,
    history: { replaceState() {} },
    window: { location },
    AbortController: function () { this.signal = {}; this.abort = function () {}; },
    setTimeout, clearTimeout, Promise, JSON, Math, Date, Number, String, Object, Array, Error,
    encodeURIComponent, decodeURIComponent, console,
  };
  ctx.window.document = document;
  vm.createContext(ctx);
  vm.runInContext(codigo, ctx);

  return {
    els, store, ctx, irA,
    peticiones: () => nPeticiones,
    click(target) { if (handlerClick) handlerClick({ target }); },
    cambiar(target) { if (handlerChange) handlerChange({ target }); },
    volverAlaPestana() { if (handlerVis) handlerVis(); },
  };
}

/* Un boton de tarjeta de mentira, para simular el toque en «Lo quiero». */
function botonDe(id) {
  const card = { className: '', querySelectorAll: () => [], querySelector: () => null };
  const btn = {
    textContent: 'Lo quiero',
    getAttribute: k => (k === 'data-id' ? id : null),
    hasAttribute: () => false,
    closest: sel => (sel === '.card button' ? btn : (sel === '.card' ? card : null)),
  };
  btn.closest = sel => (sel === '.card button' ? btn : (sel === '.card' ? card : null));
  return { target: { closest: sel => btn.closest(sel) }, btn, card };
}

const PRENDA = (i, extra) => Object.assign({
  id: 'id-' + i, nombre: 'Polera ' + i, categoria: 'Polera', talla: 'M',
  estado: 'Como nuevo', precio: 9990, notas: '', foto: 'https://x/f' + i + '.jpg',
}, extra || {});

const CATALOGO = (n, extra) => Object.assign({
  actualizado: '2026-09-08T14:00:00-03:00',
  wsp: '56900000000',
  maxPedido: 3,
  prendas: Array.from({ length: n }, (_, i) => PRENDA(i)),
}, extra || {});

const esperar = () => new Promise(r => setTimeout(r, 60));
/* El reintento de la pagina espera 2 s a proposito (arranque en frio de
   Apps Script). Las pruebas que lo ejercitan tienen que esperar mas que
   eso o miden el estado de antes: los tres primeros fallos de esta suite
   fueron justo eso, y no un fallo de la pagina. */
const esperarReintento = () => new Promise(r => setTimeout(r, 2600));

/* --- 3 · El viaje ---------------------------------------------------- */

async function principal() {

  /* a) Lo normal ---------------------------------------------------- */

  const A = nuevoEntorno([CATALOGO(5)]);
  await esperar();
  comprobar('normal · pinta las cinco prendas', (A.els.grid.innerHTML.match(/<li class="card/g) || []).length === 5,
    A.els.grid.innerHTML.slice(0, 120));
  igual('normal · el recuento lo dice', A.els.conteo.textContent, '5 prendas disponibles');
  igual('normal · esconde el aviso de «próximamente»', A.els.pronto.hidden, true);
  igual('normal · no muestra el estado vacio', A.els.vacio.hidden, true);
  comprobar('normal · pinta los filtros de categoria', A.els.filtros.innerHTML.indexOf('Todo') >= 0);
  comprobar('normal · guarda copia del catalogo para la proxima visita', !!A.store['us19_tienda_catalogo_v1']);
  comprobar('normal · dice cuando se actualizo', A.els.actualizado.textContent.indexOf('08/09') >= 0,
    A.els.actualizado.textContent);

  /* b) Sin ropa ------------------------------------------------------ */

  const B = nuevoEntorno([CATALOGO(0)]);
  await esperar();
  igual('sin ropa · muestra el estado vacio', B.els.vacio.hidden, false);
  igual('sin ropa · MANTIENE el aviso de «próximamente»', B.els.pronto.hidden, false,
    'con la tienda sin cargar, ese aviso es justo lo que hay que decir');
  igual('sin ropa · no deja filtros colgando', B.els.filtros.innerHTML, '');

  /* Y al reves: el aviso se apaga solo. Este es el fallo que estaba vivo
     en produccion — la pagina decia «el primer fardo viene en camino»
     encima de dos prendas que ya se podian comprar. */
  igual('el aviso se decide solo, no a mano', A.els.pronto.hidden !== B.els.pronto.hidden, true);

  /* c) Notion caido -------------------------------------------------- */

  const C = nuevoEntorno([{ error: true, prendas: [] }]);
  await esperar();
  igual('Notion caido · lo dice, no deja la pagina en blanco', C.els.vacio.hidden, false);
  comprobar('Notion caido · el texto invita a escribir por WhatsApp',
    C.els.vacio.innerHTML.indexOf('WhatsApp') >= 0);

  /* d) La red no contesta -------------------------------------------- */

  const D = nuevoEntorno([new Error('sin red'), new Error('sin red')]);
  await esperarReintento();
  igual('sin red · reintenta una vez', D.peticiones(), 2,
    'el arranque en frio de Apps Script falla la primera y responde la segunda');
  igual('sin red · si no hay nada que mostrar, lo dice', D.els.vacio.hidden, false);

  const E = nuevoEntorno([new Error('sin red'), CATALOGO(4)]);
  await esperarReintento();
  comprobar('sin red · el reintento salva la visita', (E.els.grid.innerHTML.match(/<li class="card/g) || []).length === 4,
    'peticiones: ' + E.peticiones());

  /* e) La copia local: la tienda aparece antes de que conteste nadie -- */

  const copia = JSON.stringify({ t: Date.now(), d: CATALOGO(3) });
  const F = nuevoEntorno([new Error('sin red'), new Error('sin red')],
                         { store: { us19_tienda_catalogo_v1: copia } });
  comprobar('copia local · pinta al instante, sin esperar a la red',
    (F.els.grid.innerHTML.match(/<li class="card/g) || []).length === 3,
    'lo primero que ve alguien no puede ser una pantalla vacia');
  await esperarReintento();
  comprobar('copia local · si la red falla del todo, la deja puesta',
    (F.els.grid.innerHTML.match(/<li class="card/g) || []).length === 3);
  comprobar('copia local · pero avisa de que puede haber cambiado',
    F.els.nota.innerHTML.indexOf('cambiado') >= 0 && F.els.nota.hidden === false,
    F.els.nota.innerHTML);

  const vieja = JSON.stringify({ t: Date.now() - 3600000, d: CATALOGO(3) });
  const G = nuevoEntorno([CATALOGO(1)], { store: { us19_tienda_catalogo_v1: vieja } });
  comprobar('copia local · una copia de hace una hora NO se usa',
    G.els.grid.innerHTML.indexOf('<li class="card') < 0 || G.els.grid.innerHTML.indexOf('esq') >= 0,
    'las fotos que firma Notion caducan a la hora: se verian rotas');

  /* f) Nada de lo que viene de Notion puede ejecutarse --------------- */

  const malicia = '<img src=x onerror=alert(1)>';
  const H = nuevoEntorno([CATALOGO(1, { prendas: [PRENDA(0, { nombre: malicia, notas: malicia })] })]);
  await esperar();
  comprobar('inyeccion · el nombre de la prenda sale escapado',
    H.els.grid.innerHTML.indexOf('<img src=x') < 0 && H.els.grid.innerHTML.indexOf('&lt;img') >= 0,
    'un nombre con etiquetas no puede acabar ejecutandose en el navegador del comprador');

  /* Y en el aviso de «ya no está disponible», que se pinta con innerHTML
     y antes no pasaba por esc(). */
  const carroMalo = JSON.stringify({ t: Date.now(), c: { 'id-99': { id: 'id-99', nombre: malicia, precio: 1000 } } });
  const I = nuevoEntorno([CATALOGO(2)], { store: { us19_tienda_carro_v1: carroMalo } });
  await esperar();
  comprobar('inyeccion · tambien en el aviso de prendas caidas',
    I.els.nota.innerHTML.indexOf('<img src=x') < 0,
    I.els.nota.innerHTML.slice(0, 120));
  comprobar('carro · la prenda que ya no esta se cae y se avisa',
    I.els.nota.hidden === false && I.els.nota.innerHTML.indexOf('ya no est') >= 0);

  /* g) El carro sobrevive -------------------------------------------- */

  const carroBueno = JSON.stringify({ t: Date.now(), c: { 'id-1': PRENDA(1) } });
  const J = nuevoEntorno([CATALOGO(3)], { store: { us19_tienda_carro_v1: carroBueno } });
  await esperar();
  igual('carro · sobrevive a la recarga', J.els.resumen.textContent, '1 prenda');
  igual('carro · la barra se ve', J.els.barra.className, 'barra visible');
  igual('carro · suma bien', J.els.total.textContent, '$9.990');

  const carroCaducado = JSON.stringify({ t: Date.now() - 90000000, c: { 'id-1': PRENDA(1) } });
  const K = nuevoEntorno([CATALOGO(3)], { store: { us19_tienda_carro_v1: carroCaducado } });
  await esperar();
  igual('carro · a las 24 h se olvida', K.els.resumen.textContent, '0 prendas');

  /* h) El tope por pedido lo manda el bot ---------------------------- */

  const L = nuevoEntorno([CATALOGO(6)]);   // maxPedido: 3
  await esperar();
  const b0 = botonDe('id-0'), b1 = botonDe('id-1'), b2 = botonDe('id-2'), b3 = botonDe('id-3');
  L.click(b0.target); L.click(b1.target); L.click(b2.target);
  igual('tope · tres prendas entran', L.els.resumen.textContent, '3 prendas');
  L.click(b3.target);
  igual('tope · la cuarta no', L.els.resumen.textContent, '3 prendas');
  comprobar('tope · y se explica, con el numero que dijo el bot',
    L.els.nota.innerHTML.indexOf('3 prendas por pedido') >= 0,
    L.els.nota.innerHTML);

  /* i) El mensaje que llega al bot ----------------------------------- */

  L.els.pedir._ev.click();
  const url = L.irA[L.irA.length - 1] || '';
  comprobar('pedido · abre WhatsApp con el numero del catalogo', url.indexOf('wa.me/56900000000') >= 0, url.slice(0, 80));
  const texto = decodeURIComponent(url.split('text=')[1] || '');
  comprobar('pedido · empieza por la palabra que el bot reconoce', /^PEDIDO US19/.test(texto), texto.slice(0, 40));
  igual('pedido · lleva un #id por prenda', (texto.match(/#id-\d/g) || []).length, 3);
  comprobar('pedido · lleva el total', texto.indexOf('Total: $29.970') >= 0, texto);
  comprobar('pedido · la URL cabe de sobra (WhatsApp corta las largas)', url.length < 2000,
    'mide ' + url.length + ' caracteres');

  /* j) Filtros que viajan en el enlace ------------------------------- */

  const M = nuevoEntorno([CATALOGO(4, {
    prendas: [PRENDA(0), PRENDA(1, { categoria: 'Short' }), PRENDA(2, { talla: 'L' }), PRENDA(3)],
  })], { hash: '#cat=Polera&talla=M' });
  await esperar();
  igual('enlace filtrado · aplica categoria y talla al abrir', M.els.conteo.textContent, '2 prendas disponibles de 4');

  /* k) Ordenar por precio -------------------------------------------- */

  const precios = [5000, 20000, 12000, 8000, 30000, 1000, 7000, 15000, 9000];
  const N = nuevoEntorno([CATALOGO(9, {
    prendas: precios.map((p, i) => PRENDA(i, { precio: p })),
  })]);
  await esperar();
  comprobar('orden · con nueve prendas aparece el control', N.els.orden.innerHTML.indexOf('Más barato') >= 0);
  N.click({ closest: sel => (sel === '.chip' ? { hasAttribute: k => k === 'data-orden', getAttribute: () => 'barato' } : null) });
  const orden = (N.els.grid.innerHTML.match(/\$[\d.]+/g) || []).slice(0, 3);
  igual('orden · «más barato» ordena de verdad', orden.join(' '), '$1.000 $5.000 $7.000');

  const O = nuevoEntorno([CATALOGO(5)]);
  await esperar();
  igual('orden · con pocas prendas el control estorba y no sale', O.els.orden.innerHTML, '');

  /* l) POR ENCARGO (14-sep-2026) ----------------------------------------
     Las camisetas del proveedor: no se apartan, se piden con talla, y
     conviven con la ropa de fardo en otra seccion. */

  const ENC = (i, extra) => Object.assign({
    id: 'enc-' + i, nombre: 'Camiseta ' + i, categoria: 'Camiseta de fútbol', estado: 'Nuevo',
    precio: 23000, foto: 'https://ultrasport19-boop.github.io/US19-FOTOS/fotos/' + i + '-v2.webp',
    encargo: true, equipo: 'Equipo ' + i, temporada: '25/26', modelo: 'Local',
  }, extra || {});
  const CAT_ENC = (lista, extra) => Object.assign(CATALOGO(0), {
    precioRef: 23000, plazoEncargo: '2 a 3 semanas', tallasEncargo: ['S', 'M', 'L', 'XL', 'XXL'], prendas: lista,
  }, extra || {});

  /* Un <select> de talla de mentira dentro de su tarjeta, con su boton. */
  function tarjetaEnc(id) {
    const btn = { textContent: 'Elige talla', disabled: true,
      getAttribute: k => (k === 'data-id' ? id : (k === 'data-enc' ? '1' : null)), hasAttribute: () => false };
    const card = { className: 'card enc', querySelectorAll: () => [], querySelector: s => (s === 'button[data-id]' ? btn : null) };
    btn.closest = sel => (sel === '.card button' ? btn : (sel === '.card' ? card : null));
    const select = { value: '', getAttribute: k => (k === 'data-para' ? id : null), closest: sel => (sel === '.card' ? card : null) };
    return { btn, card, select, toque: { closest: sel => btn.closest(sel) } };
  }

  // Mezclado: abre en entrega inmediata, con los dos contadores
  const P1 = nuevoEntorno([CAT_ENC([PRENDA(0), PRENDA(1), ENC(0), ENC(1), ENC(2)])]);
  await esperar();
  igual('secciones · con ropa de fardo abre en «Entrega inmediata»', P1.els['tab-inmediata'].getAttribute('aria-selected'), 'true');
  igual('secciones · cuenta las dos', P1.els['n-inmediata'].textContent + P1.els['n-encargo'].textContent, '(2)(3)');
  igual('secciones · entrega inmediata solo muestra fardo', (P1.els.grid.innerHTML.match(/<li class="card/g) || []).length, 2);
  igual('secciones · el plazo no se ve en entrega inmediata', P1.els.plazo.hidden, true);
  P1.click({ closest: sel => (sel === '[data-sec]' ? { getAttribute: () => 'encargo' } : null) });
  igual('secciones · la pestaña «Por encargo» muestra las tres', (P1.els.grid.innerHTML.match(/<li class="card enc/g) || []).length, 3);
  igual('secciones · y el plazo se ve', P1.els.plazo.hidden, false);
  igual('secciones · el plazo lo manda el catalogo', P1.els['plazo-txt'].textContent, '2 a 3 semanas');
  comprobar('secciones · cada tarjeta dice que es por encargo',
    (P1.els.grid.innerHTML.match(/Por encargo · llega en 2 a 3 semanas/g) || []).length === 3);
  igual('secciones · en encargo no hay chips de categoria', P1.els.filtros.innerHTML, '');

  // Solo encargos: abre en «Por encargo» sin que nadie elija
  const P2 = nuevoEntorno([CAT_ENC([ENC(0), ENC(1, { precio: 20000 }), ENC(2, { precio: 25000 }), ENC(3, { tallas: 'S-4XL' }),
    ENC(4, { tallas: 'S / M / L' }), ENC(5, { tallas: 'talla única rara' })])]);
  await esperar();
  igual('encargo · sin fardo abre directo en «Por encargo»', P2.els['tab-encargo'].getAttribute('aria-selected'), 'true');
  igual('encargo · OFERTA solo bajo el precio de referencia', (P2.els.grid.innerHTML.match(/class="oferta"/g) || []).length, 1);
  comprobar('encargo · la foto va con medidas fijas (sin salto al cargar)', /width="1000" height="1000" loading="lazy"/.test(P2.els.grid.innerHTML));
  const tarj = P2.els.grid.innerHTML.split('<li class="card');
  const opciones = t => (t.match(/<option value="([^"]+)"/g) || []).map(x => x.slice(15, -1)).join(',');
  igual('tallas · vacía → las del catalogo', opciones(tarj[1]), 'S,M,L,XL,XXL');
  igual('tallas · «S-4XL» → el rango entero', opciones(tarj[4]), 'S,M,L,XL,XXL,3XL,4XL');
  igual('tallas · «S / M / L» → la lista', opciones(tarj[5]), 'S,M,L');
  igual('tallas · lo que no se entiende → las del catalogo', opciones(tarj[6]), 'S,M,L,XL,XXL');
  comprobar('talla · el boton nace desactivado', /data-enc="1" disabled>Elige talla/.test(tarj[1]), tarj[1].slice(-160));

  // Sin catalogo nuevo (precioRef ausente) no se inventa ninguna oferta
  const P3 = nuevoEntorno([CATALOGO(0, { prendas: [ENC(0, { precio: 1000 })] })]);
  await esperar();
  igual('encargo · sin precio de referencia no hay OFERTA (nada escrito a mano)', (P3.els.grid.innerHTML.match(/class="oferta"/g) || []).length, 0);

  // La talla es obligatoria
  const T = nuevoEntorno([CAT_ENC([ENC(0), ENC(1)])]);
  await esperar();
  const t0 = tarjetaEnc('enc-0');
  T.click(t0.toque);
  igual('talla · sin elegir, no entra al pedido', T.els.resumen.textContent, '0 prendas');
  comprobar('talla · y se le dice por qué', T.els.nota.innerHTML.indexOf('talla') >= 0 && T.els.nota.hidden === false, T.els.nota.innerHTML);
  t0.select.value = 'M'; T.cambiar(t0.select);
  igual('talla · al elegirla se activa el boton', t0.btn.disabled, false);
  T.click(t0.toque);
  igual('talla · con talla entra', T.els.resumen.textContent, '1 prenda');
  igual('talla · la tarjeta queda marcada con la talla', t0.btn.textContent, 'Quitar (M)');
  t0.select.value = 'L'; T.cambiar(t0.select); T.click(t0.toque);
  igual('talla · la misma camiseta en otra talla es otro encargo', T.els.resumen.textContent, '2 prendas');
  igual('encargo · el boton dice «Pedir», no «Reservar»', T.els.pedir.textContent, 'Pedir por WhatsApp');
  T.els.pedir._ev.click();
  const txtEnc = decodeURIComponent((T.irA[T.irA.length - 1] || '').split('text=')[1] || '');
  comprobar('encargo · el mensaje empieza como pidió Diego', /^Hola! Quiero encargar:/.test(txtEnc), txtEnc.slice(0, 60));
  comprobar('encargo · lleva talla y precio de cada una', txtEnc.indexOf('Talla: M — $23.000') >= 0 && txtEnc.indexOf('Talla: L — $23.000') >= 0, txtEnc);
  comprobar('encargo · SIN #id: el #id es lo que hace que el bot aparte', txtEnc.indexOf('#') < 0, txtEnc);

  const T1 = nuevoEntorno([CAT_ENC([ENC(0)])]);
  await esperar();
  const u0 = tarjetaEnc('enc-0'); u0.select.value = 'XL'; T1.cambiar(u0.select); T1.click(u0.toque);
  T1.els.pedir._ev.click();
  igual('encargo · una sola camiseta: el mensaje exacto',
    decodeURIComponent((T1.irA[T1.irA.length - 1] || '').split('text=')[1] || ''),
    'Hola! Quiero encargar: Camiseta 0 — Equipo 0 25/26 Local\nTalla: XL — $23.000. (Por encargo, 2 a 3 semanas)');

  // Carro mixto: el fardo sigue apartandose con su #id; el encargo va aparte y sin id
  const X = nuevoEntorno([CAT_ENC([PRENDA(0), ENC(0)])]);
  await esperar();
  X.click(botonDe('id-0').target);
  X.click({ closest: sel => (sel === '[data-sec]' ? { getAttribute: () => 'encargo' } : null) });
  const x0 = tarjetaEnc('enc-0'); x0.select.value = 'S'; X.cambiar(x0.select); X.click(x0.toque);
  X.els.pedir._ev.click();
  const txtMix = decodeURIComponent((X.irA[X.irA.length - 1] || '').split('text=')[1] || '');
  comprobar('mixto · empieza por PEDIDO US19 (el bot aparta el fardo)', /^PEDIDO US19/.test(txtMix), txtMix.slice(0, 40));
  igual('mixto · un solo #id, el de la prenda de fardo', (txtMix.match(/#/g) || []).length, 1);
  comprobar('mixto · y el encargo va detrás, con su talla', txtMix.indexOf('Hola! Quiero encargar: Camiseta 0') > 0 && txtMix.indexOf('Talla: S') > 0, txtMix);
  igual('mixto · con fardo en el carro, el boton sigue diciendo «Reservar»', X.els.pedir.textContent, 'Reservar por WhatsApp');

  // Ver más y buscador sobre TODO el catalogo
  const muchas = Array.from({ length: 130 }, (_, i) => ENC(i, i === 125 ? { nombre: 'Camiseta Atlético de Madrid', equipo: 'Atlético de Madrid' } : {}));
  const V = nuevoEntorno([CAT_ENC(muchas)]);
  await esperar();
  igual('ver más · pinta 60 de entrada', (V.els.grid.innerHTML.match(/<li class="card/g) || []).length, 60);
  igual('ver más · el boton dice cuántas quedan', V.els.mas.textContent, 'Ver más (70)');
  igual('ver más · el recuento habla del total', V.els.conteo.textContent, '130 camisetas por encargo');
  V.els.mas._ev.click();
  igual('ver más · suma otras 60', (V.els.grid.innerHTML.match(/<li class="card/g) || []).length, 120);
  V.els.mas._ev.click();
  igual('ver más · al final desaparece', V.els.mas.hidden, true);
  V.els.buscar._ev.input({ target: { value: 'ATLETICO' } });
  igual('buscador · espera a que se deje de escribir', (V.els.grid.innerHTML.match(/<li class="card/g) || []).length, 130);
  await new Promise(r => setTimeout(r, 260));
  igual('buscador · sin acentos ni mayúsculas, y busca más allá de las 60 pintadas',
    (V.els.grid.innerHTML.match(/<li class="card/g) || []).length, 1);
  comprobar('buscador · encuentra la del puesto 126', V.els.grid.innerHTML.indexOf('Atlético de Madrid') >= 0);
  const W = nuevoEntorno([CAT_ENC([ENC(0, { nombre: 'Camiseta Colo Colo 24/25 local', equipo: 'Colo Colo' }), ENC(1)])]);
  await esperar();
  W.els.buscar._ev.input({ target: { value: 'Colo-Colo' } });
  await new Promise(r => setTimeout(r, 260));
  igual('buscador · «Colo-Colo» con guion encuentra «Colo Colo»', (W.els.grid.innerHTML.match(/<li class="card/g) || []).length, 1);
  V.els.buscar._ev.input({ target: { value: 'zzz' } });
  await new Promise(r => setTimeout(r, 260));
  comprobar('buscador · sin resultados lo dice', V.els.conteo.textContent.indexOf('Nada con esa búsqueda') === 0, V.els.conteo.textContent);

  // El carro recuerda la talla aunque se recargue el catalogo
  const carroEnc = JSON.stringify({ t: Date.now(), c: { 'enc-0|M': Object.assign(ENC(0), { tallaElegida: 'M', precio: 1 }) } });
  const R = nuevoEntorno([CAT_ENC([ENC(0)])], { store: { us19_tienda_carro_v1: carroEnc } });
  await esperar();
  igual('carro · el encargo sobrevive a la recarga con precio al día', R.els.total.textContent, '$23.000');
  R.els.pedir._ev.click();
  comprobar('carro · y conserva la talla elegida',
    decodeURIComponent((R.irA[R.irA.length - 1] || '').split('text=')[1] || '').indexOf('Talla: M') >= 0);

  avisos.push('el catalogo de prueba usa maxPedido=3 para no montar 13 clics');
}

principal().then(function () {
  console.log('\nUS19 · tienda');
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
}).catch(function (e) {
  console.log('\n  ✗ la suite reventó: ' + (e && e.stack || e));
  process.exit(1);
});
