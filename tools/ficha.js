/* =====================================================================
 * US19 · la ficha de ingreso, ejecutada de verdad
 *
 *   node tools/ficha.js [ruta/ficha/index.html]
 *
 * Esta pagina no guarda nada: arma un mensaje de WhatsApp y lo manda el
 * propio socio desde su numero. Eso la hace segura y la hace fragil de
 * una manera concreta: **su unico producto es un texto**, y al otro lado
 * hay un bot que lo lee por etiquetas. Si aqui se renombra «Emergencia»
 * o se pierde un salto de linea, la ficha se sigue enviando, el socio
 * sigue leyendo «gracias» — y el dato no llega a Notion. Nadie se entera.
 *
 * Por eso la comprobacion central de este archivo no es de esta pagina:
 * es del CONTRATO. Se saca el parser de verdad del asistente
 * (US19_FICHA_esFormulario_ y US19_FICHA_campo_) y se le da el mensaje
 * que esta pagina produce. Si el bot no encuentra un campo, aqui falla.
 *
 * Y lo que se firma aqui son declaraciones de salud y un consentimiento
 * de imagen: que el formulario no deje enviar sin ellos no es un detalle
 * de interfaz, es lo que hace que el papel sirva.
 *
 * Regla de oro: si algo no se encuentra, esto FALLA. Nunca pasa en verde
 * por no haber mirado.
 * ===================================================================== */

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ruta = process.argv[2] || path.join(__dirname, '..', 'ficha', 'index.html');
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
const aviso = t => avisos.push(t);
function abortar(motivo) {
  console.log('\nUS19 · ficha de ingreso\narchivo: ' + ruta + '\n\n  ✗ ' + motivo + '\n');
  process.exit(1);
}

/* --- 1 · El script y los ids, sacados de la pagina ------------------- */

const m = src.match(/<script>([\s\S]*?)<\/script>/);
if (!m) abortar('no encuentro el bloque <script> en la pagina');
const codigo = m[1];

['function marcadas(', 'function imagen(', 'function limpio(', 'function armar('].forEach(f => {
  if (codigo.indexOf(f) < 0) abortar('el script no contiene ' + f + ')  ¿se renombro?');
});

/* Los ids salen del marcado, nunca de una lista escrita a mano: asi
   renombrar uno en el HTML rompe aqui y no en el movil de alguien.
   (Es el agujero que tenia tools/tienda.js hasta el 8-sep-2026.) */
const idsPagina = new Set();
(src.match(/\bid="[A-Za-z0-9_-]+"/g) || []).forEach(t => idsPagina.add(t.slice(4, -1)));
const idsPedidos = new Set();
(codigo.match(/\$\(\s*['"][A-Za-z0-9_-]+['"]\s*\)/g) || [])
  .forEach(t => idsPedidos.add(t.replace(/^\$\(\s*['"]/, '').replace(/['"]\s*\)$/, '')));
if (!idsPedidos.size) abortar('el script no pide ningun elemento por id: ¿cambio el ayudante $()?');
const huerfanos = [...idsPedidos].filter(id => !idsPagina.has(id));
if (huerfanos.length) {
  abortar('el script pide elementos que ya no estan en el marcado: ' + huerfanos.join(', ')
    + '\n    ¿se renombro un id en la pagina y no en el <script>?');
}
pasa();

/* --- 2 · La pagina no guarda nada, y eso es a proposito -------------- */

comprobar('privacidad · la pagina no habla con ningun servidor',
  !/\bfetch\s*\(|XMLHttpRequest|navigator\.sendBeacon/.test(codigo),
  'si algun dia necesita servidor, deja de ser «no hay formulario que exponer»');
comprobar('privacidad · no guarda nada en el navegador',
  !/localStorage|sessionStorage|indexedDB|document\.cookie/.test(codigo),
  'son datos de salud: no pueden quedarse en el equipo de nadie');
comprobar('privacidad · el destino es WhatsApp, con el texto codificado',
  /wa\.me\/'\s*\+\s*BOT\s*\+\s*'\?text='\s*\+\s*encodeURIComponent/.test(codigo));

/* --- 3 · Un navegador de mentira ------------------------------------ */

function nuevoEntorno(valores, opciones) {
  opciones = opciones || {};
  const els = {};
  const marcados = opciones.salud || [];
  const enfocado = [];
  let irA = '';

  idsPagina.forEach(function (id) {
    els[id] = {
      id, value: '', checked: false, hidden: false, textContent: '', className: '',
      _ev: {},
      addEventListener(ev, fn) { this._ev[ev] = fn; },
      focus() { enfocado.push(id); },
      scrollIntoView() {},
      querySelector(sel) {
        if (id !== 'salud') return null;
        return marcados.length ? { value: marcados[0] } : null;
      },
      querySelectorAll(sel) {
        if (id !== 'salud') return [];
        return marcados.map(v => ({ value: v }));
      },
    };
  });
  Object.keys(valores || {}).forEach(k => {
    if (!els[k]) throw new Error('la prueba usa un id que no esta en la pagina: ' + k);
    if (typeof valores[k] === 'boolean') els[k].checked = valores[k];
    else els[k].value = valores[k];
  });

  const document = {
    getElementById(id) { return els[id] || null; },
    querySelector(sel) {
      if (/input\[name="imagen"\]:checked/.test(sel)) {
        return opciones.imagen ? { value: opciones.imagen } : null;
      }
      if (/input\[name="imagen"\]/.test(sel)) return { focus() { enfocado.push('imagen'); }, scrollIntoView() {} };
      return null;
    },
  };
  const ctx = {
    document,
    window: { get location() { return { href: irA }; }, set location(v) { irA = v; } },
    encodeURIComponent, decodeURIComponent, console, String, Array, RegExp, Object,
  };
  /* `window.location.href = …` es como la pagina navega: se intercepta. */
  ctx.window = { location: { set href(v) { irA = v; }, get href() { return irA; } } };
  vm.createContext(ctx);
  vm.runInContext(codigo, ctx);
  return {
    els, enfocado,
    pulsar() { if (els.btn._ev.click) els.btn._ev.click(); },
    cambiarSalud() { if (els.salud._ev.change) els.salud._ev.change(); },
    destino: () => irA,
    mensaje() {
      const u = irA;
      const i = u.indexOf('?text=');
      return i < 0 ? '' : decodeURIComponent(u.slice(i + 6));
    },
  };
}

/* --- 4 · Lo que NO deja enviar -------------------------------------- */

const COMPLETA = {
  nombre: '  Juan   Pérez  ', rut: '11.111.111-1', nacimiento: '1990-05-02',
  emergencia: 'María 912345678', antecedentes: 'ninguno', medicamentos: '',
  comollegaste: 'Recomendación', quienrecomendo: 'Pedro', acepta: true,
};

let E = nuevoEntorno(Object.assign({}, COMPLETA, { nombre: '   ' }), { imagen: 'Si' });
E.pulsar();
igual('validacion · sin nombre no se envia', E.destino(), '');
comprobar('validacion · y el foco va al nombre', E.enfocado.indexOf('nombre') >= 0);
comprobar('validacion · con un aviso que dice que falta', /nombre/i.test(E.els.aviso.textContent), E.els.aviso.textContent);

E = nuevoEntorno(Object.assign({}, COMPLETA, { acepta: false }), { imagen: 'Si' });
E.pulsar();
igual('validacion · sin aceptar el consentimiento no se envia', E.destino(), '');
comprobar('validacion · y dice en que seccion esta', /4/.test(E.els.aviso.textContent), E.els.aviso.textContent);

E = nuevoEntorno(COMPLETA, {});
E.pulsar();
igual('validacion · sin responder lo de las fotos no se envia', E.destino(), '');
comprobar('validacion · y deja claro que un NO tambien vale',
  /cualquiera de las dos/i.test(E.els.aviso.textContent), E.els.aviso.textContent);

/* Que un NO a las fotos SI deje enviar: si no, el consentimiento no seria
   libre, y un consentimiento obligatorio no vale justo cuando hace falta. */
E = nuevoEntorno(COMPLETA, { imagen: 'No' });
E.pulsar();
comprobar('consentimiento · decir NO a las fotos deja enviar igual', E.destino().indexOf('wa.me') > 0);
comprobar('consentimiento · y el mensaje lo dice', /^Fotos: NO$/m.test(E.mensaje()), E.mensaje());

/* --- 5 · El mensaje, que es todo el producto ------------------------ */

E = nuevoEntorno(COMPLETA, { imagen: 'Si', salud: ['Asma', 'Hipertensión'] });
E.pulsar();
const MSG = E.mensaje();
comprobar('mensaje · va al numero del bot', E.destino().indexOf('wa.me/56965902238') > 0, E.destino().slice(0, 60));
comprobar('mensaje · empieza por FICHA US19', /^FICHA US19$/m.test(MSG.split('\n')[0]), MSG.split('\n')[0]);
comprobar('mensaje · el nombre llega limpio de espacios de mas',
  /^Nombre: Juan Pérez$/m.test(MSG), (MSG.match(/^Nombre:.*$/m) || [])[0]);
comprobar('mensaje · las marcas de salud van juntas y separadas por " / "',
  /^Salud: Asma \/ Hipertensión$/m.test(MSG), (MSG.match(/^Salud:.*$/m) || [])[0]);
comprobar('mensaje · un campo vacio va como "-", no como vacio',
  /^Medicamentos: -$/m.test(MSG), (MSG.match(/^Medicamentos:.*$/m) || [])[0]);
comprobar('mensaje · la atribucion viaja', /^Como llegaste: Recomendación$/m.test(MSG));
comprobar('mensaje · y quien recomendo tambien', /^Quien recomendo: Pedro$/m.test(MSG));

const SIN_SALUD = (() => {
  const F = nuevoEntorno(COMPLETA, { imagen: 'Si', salud: [] });
  F.pulsar();
  return F.mensaje();
})();
comprobar('mensaje · sin nada marcado dice "ninguna marcada"',
  /^Salud: ninguna marcada$/m.test(SIN_SALUD), (SIN_SALUD.match(/^Salud:.*$/m) || [])[0]);

/* El aviso de salud aparece al marcar algo, no antes. */
const G = nuevoEntorno(COMPLETA, { imagen: 'Si', salud: ['Asma'] });
G.cambiarSalud();
igual('interfaz · al marcar algo de salud se muestra el aviso', G.els['aviso-salud'].hidden, false);
const H = nuevoEntorno(COMPLETA, { imagen: 'Si', salud: [] });
H.cambiarSalud();
igual('interfaz · sin nada marcado, el aviso sigue escondido', H.els['aviso-salud'].hidden, true);

/* --- 6 · EL CONTRATO CON EL BOT ------------------------------------- */
/* Lo que de verdad puede romperse en silencio. El asistente lee este
   mensaje por etiquetas; si aqui se renombra una, la ficha se envia
   igual, el socio lee «gracias» y el dato no llega. Asi que se usa el
   parser DE VERDAD, no una imitacion. */

const RUTA_BOT = process.env.US19_BOT
  || path.join('C:', 'Users', 'diego', 'OneDrive', 'Documentos',
               'RESPALDO_ASISTENTE_APPSSCRIPT', 'proyecto_clasp', 'Código.js');

if (!fs.existsSync(RUTA_BOT)) {
  aviso('CONTRATO SIN COMPROBAR: no encuentro el Código.js del asistente en ' + RUTA_BOT
      + '. Es el repositorio del bot, que no viaja con este. Con la variable US19_BOT se le puede dar otra ruta.');
} else {
  const bot = fs.readFileSync(RUTA_BOT, 'utf8');
  function fnBot(nombre) {
    const i = bot.indexOf('function ' + nombre + '(');
    if (i < 0) return null;
    const j = bot.indexOf('\r\n}\r\n', i);
    const k = bot.indexOf('\n}\n', i);
    const fin = j >= 0 ? j + 5 : (k >= 0 ? k + 3 : -1);
    return fin < 0 ? null : bot.slice(i, fin);
  }
  const esForm = fnBot('US19_FICHA_esFormulario_');
  const campo = fnBot('US19_FICHA_campo_');
  if (!esForm || !campo) {
    falla('contrato · no pude sacar el parser del asistente',
      'US19_FICHA_esFormulario_ o US19_FICHA_campo_ cambiaron de forma');
  } else {
    const api = new Function(esForm + '\n' + campo
      + '\nreturn { esFormulario: US19_FICHA_esFormulario_, campo: US19_FICHA_campo_ };')();

    comprobar('contrato · el bot reconoce el mensaje como una ficha', api.esFormulario(MSG) === true);

    /* Las ocho etiquetas que el asistente lee de verdad, sacadas de su
       propio codigo: si añade una novena y la pagina no la manda, aqui
       se ve. */
    const pedidas = [...new Set(
      (bot.match(/US19_FICHA_campo_\(\s*\w+\s*,\s*'([^']+)'/g) || [])
        .map(t => t.replace(/.*'([^']+)'.*/, '$1'))
    )];
    comprobar('contrato · el asistente lee al menos las ocho etiquetas conocidas',
      pedidas.length >= 8, pedidas.join(', '));

    const vacias = pedidas.filter(et => {
      const v = api.campo(MSG, et);
      /* «Salud» y los opcionales pueden venir vacios a proposito; lo que
         no puede es que la ETIQUETA no exista en el mensaje. */
      return !new RegExp('^\\s*' + et + '\\s*:', 'im').test(MSG);
    });
    igual('contrato · la pagina manda TODAS las etiquetas que el bot busca',
      vacias.join(', '), '');

    igual('contrato · el bot lee el nacimiento', api.campo(MSG, 'Nacimiento'), '1990-05-02');
    igual('contrato · el bot lee el contacto de emergencia', api.campo(MSG, 'Emergencia'), 'María 912345678');
    igual('contrato · el bot lee la salud marcada', api.campo(MSG, 'Salud'), 'Asma / Hipertensión');
    igual('contrato · el bot lee como llego', api.campo(MSG, 'Como llegaste'), 'Recomendación');
    igual('contrato · el bot lee quien recomendo', api.campo(MSG, 'Quien recomendo'), 'Pedro');
    igual('contrato · el bot lee la respuesta de fotos', api.campo(MSG, 'Fotos'), 'SI');
    /* Un campo vacio viaja como «-» y el bot lo traduce a cadena vacia:
       si eso deja de coincidir, Notion se llena de guiones. */
    igual('contrato · el "-" de un campo vacio le llega al bot como vacio',
      api.campo(MSG, 'Medicamentos'), '');
    igual('contrato · «ninguna marcada» tambien le llega como vacio',
      api.campo(SIN_SALUD, 'Salud'), '');
    aviso('contrato comprobado contra el Código.js del asistente (' + pedidas.length + ' etiquetas)');
  }
}

/* --- salida ---------------------------------------------------------- */

console.log('\nUS19 · ficha de ingreso');
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
