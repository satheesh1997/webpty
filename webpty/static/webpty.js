// terminal addons are to be added here
Terminal.applyAddon(fullscreen);
Terminal.applyAddon(fit);
Terminal.applyAddon(webLinks);

// all the constants are to be added here
const delay = 50;
const host = window.location.host;
const pathname = window.location.pathname;
const scrollBackLimit = 5000; // current limit is 5000, change it in future if required
const terminal = new Terminal({
  cursorBlink: true,
  macOptionIsMeta: true,
  scrollback: true,
});
const terminalDivId = "webpty";
const webSocketProtocol = window.location.protocol.indexOf("https") ? "ws" : "wss";
const ws = new WebSocket(`${webSocketProtocol}://${host}${pathname}pty`);

// utility functions are to be added here
function fitToScreen() {
  terminal.fit();
  ws.send(
    JSON.stringify({
      action: "resize",
      data: { cols: terminal.cols, rows: terminal.rows },
    })
  );
}

function resizeDelay(func, delay) {
  let timeout;
  return function (...args) {
    const context = this;
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(context, args), delay);
  };
}

// all on event handlers & listeners are to be added here
window.onresize = resizeDelay(fitToScreen, delay);

ws.onopen = function () {
  terminal.open(document.getElementById(terminalDivId));
  terminal.toggleFullScreen(true);
  terminal.setOption("scrollback", scrollBackLimit);
  fitToScreen();
};

ws.onmessage = function (event) {
  terminal.write(event.data);
};

terminal.on("key", (key) => {
  ws.send(JSON.stringify({ action: "input", data: { key: key } }));
});

terminal.on("paste", (text) => {
  ws.send(JSON.stringify({ action: "input", data: { key: text } }));
});
