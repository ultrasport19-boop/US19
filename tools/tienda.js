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
  let nPeticiones = 0;
  const irA = [];

  const document = {
    getElementById(id) { return els[id] || null; },
    addEventListener(ev, fn) { if (ev === 'click') handlerClick = fn; if (ev === 'visibilitychange') handlerVis = fn; },
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
