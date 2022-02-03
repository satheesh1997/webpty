Terminal.applyAddon(fullscreen);
Terminal.applyAddon(fit);
Terminal.applyAddon(webLinks);

function startApp() {
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
  const webSocketProtocol = window.location.protocol.indexOf("https")
    ? "ws"
    : "wss";
  const ws = new WebSocket(`${webSocketProtocol}://${host}${pathname}pty`);

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

  function sendPing(){
    ws.send(JSON.stringify({ action: "ping"}))
  }
  if(KEEP_ALIVE){
    setInterval(sendPing,KEEP_ALIVE*1000)
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
startApp();
