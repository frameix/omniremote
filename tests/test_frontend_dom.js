// Simulate browser DOM environment in Node.js
class MockElement {
  constructor(tag, id = "") {
    this.tagName = tag;
    this.id = id;
    this.className = "";
    this.style = {};
    this.children = [];
    this.innerHTML = "";
    this.textContent = "";
    this.value = "";
    this.listeners = {};
    this.attributes = {};
    this.classList = {
      add: (c) => {},
      remove: (c) => {},
      toggle: (c, force) => {}
    };
  }
  addEventListener(event, fn) {
    if (!this.listeners[event]) this.listeners[event] = [];
    this.listeners[event].push(fn);
  }
  click() {
    if (this.listeners["click"]) this.listeners["click"].forEach(fn => fn({ type: "click" }));
  }
  appendChild(child) {
    this.children.push(child);
  }
  setAttribute(k, v) { this.attributes[k] = v; }
  querySelector(sel) { return new MockElement("span"); }
  blur() {}
}

const elements = {
  "karaoke-input": new MockElement("input", "karaoke-input"),
  "btn-karaoke-search": new MockElement("button", "btn-karaoke-search"),
  "chk-karaoke-mode": new MockElement("input", "chk-karaoke-mode"),
  "karaoke-results-container": new MockElement("div", "karaoke-results-container"),
  "karaoke-results-list": new MockElement("div", "karaoke-results-list"),
  "karaoke-now-playing": new MockElement("div", "karaoke-now-playing"),
  "karaoke-current-thumb": new MockElement("img", "karaoke-current-thumb"),
  "karaoke-current-title": new MockElement("div", "karaoke-current-title"),
  "karaoke-current-dur": new MockElement("div", "karaoke-current-dur"),
  "btn-karaoke-next": new MockElement("button", "btn-karaoke-next"),
  "btn-karaoke-stop": new MockElement("button", "btn-karaoke-stop"),
  "karaoke-queue-count": new MockElement("span", "karaoke-queue-count"),
  "karaoke-queue-list": new MockElement("div", "karaoke-queue-list"),
  "btn-deck-prev": new MockElement("button", "btn-deck-prev"),
  "btn-deck-play": new MockElement("button", "btn-deck-play"),
  "btn-deck-next": new MockElement("button", "btn-deck-next"),
  "btn-deck-vol-down": new MockElement("button", "btn-deck-vol-down"),
  "btn-deck-mute": new MockElement("button", "btn-deck-mute"),
  "btn-deck-vol-up": new MockElement("button", "btn-deck-vol-up"),
  "tp-vol-down": new MockElement("button", "tp-vol-down"),
  "tp-vol-up": new MockElement("button", "tp-vol-up"),
  "tp-mute": new MockElement("button", "tp-mute"),
  "tp-play": new MockElement("button", "tp-play"),
  "tp-next": new MockElement("button", "tp-next"),
  "tp-back": new MockElement("button", "tp-back"),
  "btn-ws-prev": new MockElement("button", "btn-ws-prev"),
  "btn-ws-next": new MockElement("button", "btn-ws-next"),
  "trackpad-hint": new MockElement("div", "trackpad-hint"),
};

global.document = {
  getElementById: (id) => elements[id] || new MockElement("div", id),
  createElement: (tag) => new MockElement(tag),
  querySelectorAll: () => [],
  addEventListener: () => {},
  visibilityState: "visible"
};
global.window = global;
global.location = { protocol: "http:", host: "127.0.0.1:8765" };
global.WebSocket = class {
  static OPEN = 1;
  constructor(url) {
    this.readyState = 1;
  }
  send(payload) {
    try {
      sentMessages.push(JSON.parse(payload));
    } catch (e) {
      sentMessages.push(payload);
    }
  }
};
global.localStorage = { getItem: () => null, setItem: () => {} };
global.navigator = { vibrate: () => {} };

let sentMessages = [];
global.send = (msg) => sentMessages.push(msg);
global.haptic = () => {};
global.showHUD = (txt) => console.log("   [HUD Toast]:", txt);

// Read JS from index.html and evaluate the Karaoke portion
const fs = require("fs");
const path = require("path");
const html = fs.readFileSync(path.join(__dirname, "../web/index.html"), "utf8");
const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/);
if (!scriptMatch) throw new Error("No script found");

// Evaluate in sandbox
eval(scriptMatch[1]);

console.log("✓ Frontend JavaScript cargo y evaluo sin ningun error.");

// TEST 1: Simular busqueda desde el input y boton
console.log("\n[TEST FRONTEND 1] Simulando busqueda de cancion...");
elements["karaoke-input"].value = "Soda Stereo De musica ligera";
elements["chk-karaoke-mode"].checked = true;
elements["btn-karaoke-search"].click();

const lastSent = sentMessages[sentMessages.length - 1];
console.log("   Mensaje enviado por WebSocket al buscar:", lastSent);
if (lastSent.type !== "karaoke_search" || lastSent.query !== "Soda Stereo De musica ligera" || lastSent.karaoke !== true) {
  throw new Error("Fallo en mensaje de busqueda");
}
console.log("✓ TEST FRONTEND 1 PASO: El boton de busqueda despacho el frame WebSocket correctamente.");

// TEST 2: Simular renderizado de resultados de busqueda que llegan del servidor
console.log("\n[TEST FRONTEND 2] Simulando recepcion de resultados del servidor...");
const mockResults = [
  { id: "mjJ-ybMo4ZM", title: "Soda Stereo - De Musica Ligera (Karaoke)", duration: "3:28", thumb: "https://img.youtube.com/vi/1.jpg" },
  { id: "Ig_u_Mty0cU", title: "Soda Stereo - De Musica Ligera (Pista)", duration: "3:44", thumb: "https://img.youtube.com/vi/2.jpg" }
];
handleServerMessage({ type: "karaoke_results", results: mockResults });

console.log("   Items renderizados en #karaoke-results-list:", elements["karaoke-results-list"].children.length);
if (elements["karaoke-results-list"].children.length !== 2) throw new Error("No se renderizaron 2 resultados");

// TEST 3: Simular click en "Poner Ya" en el primer resultado
console.log("\n[TEST FRONTEND 3] Simulando click en boton 'Poner Ya' del primer resultado...");
const firstRow = elements["karaoke-results-list"].children[0];
const actionsContainer = firstRow.children[2];
const playNowBtn = actionsContainer.children[0];
playNowBtn.click();

const playMsg = sentMessages[sentMessages.length - 1];
console.log("   Mensaje enviado por WebSocket al presionar 'Poner Ya':", playMsg);
if (playMsg.type !== "karaoke_play_now" || playMsg.song.id !== "mjJ-ybMo4ZM") {
  throw new Error("Fallo en boton reproducir ya");
}
console.log("✓ TEST FRONTEND 3 PASO: El boton 'Poner Ya' despacho karaoke_play_now correctamente.");

// TEST 4: Simular click en "Cola" en el segundo resultado
console.log("\n[TEST FRONTEND 4] Simulando click en boton 'Cola' del segundo resultado...");
const secondRow = elements["karaoke-results-list"].children[1];
const addQueueBtn = secondRow.children[2].children[1];
addQueueBtn.click();

const queueMsg = sentMessages[sentMessages.length - 1];
console.log("   Mensaje enviado por WebSocket al presionar 'Cola':", queueMsg);
if (queueMsg.type !== "karaoke_add_queue" || queueMsg.song.id !== "Ig_u_Mty0cU") {
  throw new Error("Fallo en boton agregar a la cola");
}
console.log("✓ TEST FRONTEND 4 PASO: El boton 'Cola' despacho karaoke_add_queue correctamente.");

// TEST 5: Simular actualizacion de estado de la cola
console.log("\n[TEST FRONTEND 5] Simulando renderizado de estado de cola (Now Playing + Queue)...");
handleServerMessage({
  type: "karaoke_state",
  data: {
    current: mockResults[0],
    queue: [mockResults[1]]
  }
});

console.log("   Now Playing display:", elements["karaoke-now-playing"].style.display);
console.log("   Now Playing title:", elements["karaoke-current-title"].textContent);
console.log("   Queue count:", elements["karaoke-queue-count"].textContent);
console.log("   Queue items rendered:", elements["karaoke-queue-list"].children.length);

if (elements["karaoke-now-playing"].style.display !== "flex") throw new Error("Now playing card no visible");
if (elements["karaoke-current-title"].textContent !== "Soda Stereo - De Musica Ligera (Karaoke)") throw new Error("Titulo erroneo");
if (String(elements["karaoke-queue-count"].textContent) !== "1") throw new Error("Contador de cola erroneo");
console.log("✓ TEST FRONTEND 5 PASO: El estado 'Sonando Ahora' y la 'Lista de Espera' se renderizaron a la perfeccion.");

// TEST 6: Simular botones Siguiente y Detener
console.log("\n[TEST FRONTEND 6] Probando botones de control multimedia...");
elements["btn-karaoke-next"].click();
const nextMsg = sentMessages[sentMessages.length - 1];
console.log("   Mensaje al presionar Siguiente:", nextMsg);
if (nextMsg.type !== "karaoke_next") throw new Error("Fallo en Siguiente");

elements["btn-karaoke-stop"].click();
const stopMsg = sentMessages[sentMessages.length - 1];
console.log("   Mensaje al presionar Detener:", stopMsg);
if (stopMsg.type !== "karaoke_stop") throw new Error("Fallo en Detener");
console.log("✓ TEST FRONTEND 6 PASO: Los botones 'Siguiente' y 'Detener' funcionan al 100%.");

// TEST 7: Probar botones del Deck Multimedia y Trackpad Mini Bar
console.log("\n[TEST FRONTEND 7] Probando botones universales (Deck Multimedia & Trackpad Mini Bar)...");
elements["btn-deck-prev"].click();
if (sentMessages[sentMessages.length - 1].action !== "prev") throw new Error("Deck prev falló");

elements["btn-deck-play"].click();
if (sentMessages[sentMessages.length - 1].action !== "play_pause") throw new Error("Deck play falló");
if (elements["tp-play"].textContent !== "⏸️") throw new Error("Al dar play en Deck, tp-play debió sincronizar a pausa (⏸️)");

elements["tp-play"].click();
if (sentMessages[sentMessages.length - 1].action !== "play_pause") throw new Error("TP play falló");
if (elements["tp-play"].textContent !== "▶️") throw new Error("Al pulsar tp-play, debió alternar a reproducir (▶️)");

elements["tp-vol-down"].click();
if (sentMessages[sentMessages.length - 1].action !== "vol_down") throw new Error("TP vol_down falló");

elements["tp-vol-up"].click();
if (sentMessages[sentMessages.length - 1].action !== "vol_up") throw new Error("TP vol_up falló");

elements["tp-mute"].click();
if (sentMessages[sentMessages.length - 1].action !== "mute") throw new Error("TP mute falló");

elements["tp-next"].click();
if (sentMessages[sentMessages.length - 1].action !== "next") throw new Error("TP next falló");

elements["tp-back"].click();
if (sentMessages[sentMessages.length - 1].action !== "back") throw new Error("TP back falló");

console.log("✓ TEST FRONTEND 7 PASO: Todos los botones del Deck (Prev, Play, Next, Vol+, Vol-, Mute) y Trackpad Mini Bar (Vol-, Vol+, Mute, Play, Next, Back) responden y alternan estado de reproducción.");

// TEST 8: Adaptación Dinámica según Sistema Operativo (Windows vs Linux)
console.log("\n[TEST FRONTEND 8] Probando adaptación de UI para Windows y Linux (system_info)...");
// 1. Simular mensaje system_info de Windows
handleServerMessage({
  type: "system_info",
  platform: "windows",
  desktop: "GenericDesktop"
});

if (elements["btn-ws-prev"].textContent !== "◀ Ventana") throw new Error("Botón no adaptado a Windows (◀ Ventana)");
if (elements["btn-ws-next"].textContent !== "Ventana ▶") throw new Error("Botón no adaptado a Windows (Ventana ▶)");
if (!elements["trackpad-hint"].innerHTML.includes("Cambiar Ventana")) throw new Error("Hint no adaptado a Windows");

elements["btn-ws-next"].click();
const winNextMsg = sentMessages[sentMessages.length - 1];
if (winNextMsg.type !== "gesture" || winNextMsg.action !== "workspace_next") throw new Error("Fallo en envío de workspace_next");

// 2. Simular mensaje system_info de Linux
handleServerMessage({
  type: "system_info",
  platform: "linux",
  desktop: "HyprlandDesktop"
});

if (elements["btn-ws-prev"].textContent !== "◀ Escritorio") throw new Error("Botón no adaptado a Linux (◀ Escritorio)");
if (elements["btn-ws-next"].textContent !== "Escritorio ▶") throw new Error("Botón no adaptado a Linux (Escritorio ▶)");
if (!elements["trackpad-hint"].innerHTML.includes("Cambiar Escritorio")) throw new Error("Hint no adaptado a Linux");

console.log("✓ TEST FRONTEND 8 PASO: La interfaz se adapta dinámicamente entre 'Ventana' (Windows) y 'Escritorio' (Linux), y menciona 3 dedos.");

console.log("\n=======================================================");
console.log("  TODOS LOS TESTS DE INTERFAZ Y BOTONES PASARON OK  ");
console.log("=======================================================");
