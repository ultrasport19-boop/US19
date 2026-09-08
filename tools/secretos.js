/* =====================================================================
 * US19 · las páginas públicas · que no se escape una credencial
 *
 *   node tools/secretos.js
 *
 * POR QUE EXISTE
 * Este es el repositorio MAS publico de los tres: no es que se pueda
 * leer, es que se sirve. Lo que hay aqui es la web del gimnasio, y GitHub
 * Pages lo publica tal cual. Aun asi era el unico de los tres sin ninguna
 * comprobacion de secretos: la app tenia la suya y el asistente acaba de
 * estrenar la propia.
 *
 * El barrido de hoy sobre los 43 commits del historial no encontro nada.
 * Esto existe para que siga siendo verdad.
 *
 * QUE MIRA
 * Los 24 archivos de texto que git tiene registrados —de 207, el resto son
 * fotos—, contra nueve formas de credencial. Y se prueba a si mismo: ver
 * abajo por que hace falta.
 * ===================================================================== */

const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const RAIZ = path.join(__dirname, '..');

let ok = 0;
const fallos = [], avisos = [];
const pasa = () => ok++;
const falla = (n, d) => fallos.push(n + (d ? '  →  ' + d : ''));
const comprobar = (n, c, d) => { if (c) pasa(); else falla(n, d); };
const aviso = t => avisos.push(t);

/* Cada patron es la forma de UNA credencial concreta, no una heuristica de
   «cadena larga». El `\b` del principio no es adorno: ver la prueba de la
   prueba, al final. */
const PATRONES = [
  ['token de Meta/WhatsApp',         /\bEAA[A-Za-z0-9]{60,}/],
  ['token de Notion',                /\bntn_[A-Za-z0-9]{20,}/],
  ['token de Notion (antiguo)',      /\bsecret_[A-Za-z0-9]{30,}/],
  ['clave de Anthropic',             /\bsk-ant-[A-Za-z0-9_-]{20,}/],
  ['token de GitHub',                /\bgh[pousr]_[A-Za-z0-9]{30,}/],
  ['token de GitHub (fine-grained)', /\bgithub_pat_[A-Za-z0-9_]{30,}/],
  ['token de Calendly (JWT)',        /\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}/],
  ['clave de API de Google',         /\bAIza[A-Za-z0-9_-]{33}\b/],
  ['clave privada en formato PEM',   /-----BEGIN [A-Z ]*PRIVATE KEY-----/],
];

/* De los 207 archivos registrados, 182 son fotos. Leerlas como utf-8 no
   encuentra nada y cuesta segundos. */
const BINARIOS = /\.(gif|mp4|jpg|jpeg|png|webp|ico|woff2?|ttf|otf|pdf|zip)$/i;

let archivos = [];
try {
  archivos = execFileSync('git', ['ls-files', '-z'], { cwd: RAIZ })
    .toString('utf8').split('\0').filter(Boolean).filter(f => !BINARIOS.test(f));
} catch (e) {
  console.log('\n  ✗ no puedo preguntarle a git que archivos hay: ' + e.message + '\n');
  process.exit(1);
}
comprobar('git me dice que archivos de texto hay', archivos.length > 0,
  'ls-files no devolvio nada — ¿esto es un repositorio?');

const sucios = [];
archivos.forEach(function (rel) {
  let texto;
  try { texto = fs.readFileSync(path.join(RAIZ, rel), 'utf8'); } catch (e) { return; }
  PATRONES.forEach(function (p) {
    const m = p[1].exec(texto);
    /* Se dice QUE y DONDE. Nunca el valor: esto se ejecuta en una terminal
       que a veces acaba pegada en un chat. */
    if (m) sucios.push(rel + ':' + texto.slice(0, m.index).split('\n').length + ' — ' + p[0]);
  });
});
comprobar('ni una credencial en las páginas ni en las herramientas',
  sucios.length === 0, sucios.join(' · '));
aviso(archivos.length + ' archivos de texto revisados, ' + PATRONES.length +
      ' formas de credencial buscadas');

/* --- La prueba de la prueba ------------------------------------------
   Barriendo el historial del repositorio de la app con el patron de Meta
   SIN el `\b`, salto una coincidencia dentro de index.html. Susto de dos
   minutos: un token de Meta en un repositorio publico no se arregla
   borrando el archivo.

   No era un token. Era el logo, que va embebido como data URI, y cuyo
   base64 tiene en mitad `...JTEUAAQ` seguido de `EAAAHI` y seiscientos
   caracteres mas. Con `\b` no coincide, porque la letra de antes es una
   `Q` y ahi no hay frontera de palabra.

   O sea que ese `\b` es lo unico que separa esto de dar la alarma en cada
   commit que lleve una imagen embebida. Y una alarma que salta sin motivo
   se acaba ignorando, que es peor que no tenerla. Asi que se comprueba en
   los dos sentidos.

   Las cadenas se construyen aqui, no se escriben enteras: si estuvieran,
   el barrido de arriba las encontraria en este mismo archivo y la prueba
   se denunciaria a si misma. */
const patronMeta = PATRONES[0];
const dentroDeUnBase64 = 'SUNDX1BST0ZJTEUAAQ' + 'EAAAHI' + 'QzZmVi'.repeat(12);
comprobar('el logo en base64 NO se confunde con un token (el \\b importa)',
  !patronMeta[1].test(dentroDeUnBase64),
  'el patron volvio a coincidir dentro de una imagen: cada commit con un data URI daria la alarma');

const unTokenDeVerdad = 'WSP_TOKEN=' + 'EAA' + 'G7kQz2mVb'.repeat(9);
comprobar('y un token de verdad sigue saltando',
  patronMeta[1].test(unTokenDeVerdad),
  'de tanto afinar el patron ya no reconoce lo que existe para reconocer');

/* --- salida ---------------------------------------------------------- */
console.log('');
avisos.forEach(a => console.log('  · ' + a));
console.log('');
if (fallos.length) {
  fallos.forEach(f => console.log('  ✗ ' + f));
  console.log('\n  comprobaciones OK: ' + ok + '  ·  FALLOS: ' + fallos.length + '\n');
  process.exit(1);
}
console.log('  comprobaciones OK: ' + ok + '  ·  sin fallos\n');
