function callWithDelay(func, delay) {
  let timeout;
  return function (...args) {
    const context = this;
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(context, args), delay);
  };
}

function startApp() {
  const delay = 50;
  const host = window.location.host;
  const pathname = window.location.pathname;
  const scrollBackLimit = 5000; // current limit is 5000, change it in future if required
  const fitAddon = new FitAddon.FitAddon();
  const terminal = new Terminal({
    screenKeys: true,
    cursorBlink: true,
    macOptionIsMeta: true,
    scrollback: true,
    fontFamily: "Source Code Pro",
  });
  const terminalDivId = "webpty";
  const webSocketProtocol = window.location.protocol.indexOf("https")
    ? "ws"
    : "wss";
  const ws = new WebSocket(`${webSocketProtocol}://${host}${pathname}pty`);

  terminal.loadAddon(fitAddon);

  function fitToScreen() {
    fitAddon.fit();
    console.log(terminal.cols, terminal.rows);
    ws.send(
      JSON.stringify({
        action: "resize",
        data: { cols: terminal.cols, rows: terminal.rows },
      })
    );
  }

  window.onresize = callWithDelay(fitToScreen, delay);

  ws.onopen = function () {
    terminal.open(document.getElementById(terminalDivId));
    terminal.options.scrollback = scrollBackLimit;
    fitToScreen();
  };

  ws.onmessage = function (event) {
    terminal.write(event.data);
  };

  terminal.onKey((event) => {
    ws.send(JSON.stringify({ action: "input", data: { key: event.key } }));
  });

  terminal.attachCustomKeyEventHandler((event) => {
    if (
      (event.ctrlKey || event.metaKey) &&
      event.code === "KeyV" &&
      event.type === "keydown"
    ) {
      navigator.clipboard.readText().then((clipText) => {
        ws.send(JSON.stringify({ action: "input", data: { key: clipText } }));
      });
      event.preventDefault();
    }
  });

  function sendPing() {
    ws.send(JSON.stringify({ action: "ping" }));
  }

  if (KEEP_ALIVE) {
    setInterval(sendPing, KEEP_ALIVE * 1000);
  }
}

function getPasswordFromCookie() {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; webptyPass=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}

if (APP_SECURED) {
  var userPassword = getPasswordFromCookie();
  while (
    userPassword === null ||
    userPassword === "" ||
    userPassword === undefined
  ) {
    userPassword = prompt(
      "This is a password protected shell. Please enter your password."
    );
    if (userPassword) {
      var xhr = new XMLHttpRequest();
      xhr.open("POST", "/auth", true);
      xhr.setRequestHeader("Content-Type", "application/json");
      xhr.send(
        JSON.stringify({
          webptyPass: userPassword,
        })
      );

      xhr.onreadystatechange = function () {
        if (this.readyState != 4) return;
        if (this.status !== 200) {
          userPassword = null;
        }
        if (this.status === 200) {
          location.reload();
        }
      };
    }
  }
}

window.onload = startApp;
