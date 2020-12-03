import fcntl
import json
import os
import pty
import select
import struct
import subprocess
import termios

from argparse import ArgumentParser

import tornado.ioloop
import tornado.web
import tornado.websocket

from tornado import gen
from tornado.options import define, options


define("child_pid", 0)
define("fd", 0)


@gen.coroutine
def read_and_update_tty_terminal(instance):
    max_read_bytes = 1024 * 20

    while True:
        yield gen.sleep(0.01)
        if options.fd:
            timeout = 0
            (output_generated, _, _) = select.select([options.fd], [], [], timeout)
            if output_generated:
                output = os.read(options.fd, max_read_bytes).decode()
                instance.write_message(output)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class PtyHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        if options.child_pid:
            return

        (child_pid, fd) = pty.fork()
        if child_pid == 0:
            subprocess.run("bash")
        else:
            options.fd = fd
            options.child_pid = child_pid
            read_and_update_tty_terminal(self)

    def on_message(self, message):
        message = json.loads(message)
        action = message.get("action")
        data = message.get("data")

        if action == "resize":
            terminalsize = struct.pack(
                "HHHH",
                data.get("rows", 50),
                data.get("cols", 50),
                0,
                0
            )
            fcntl.ioctl(options.fd, termios.TIOCSWINSZ, terminalsize)
        elif action == "input":
            os.write(options.fd, data["key"].encode())

    def on_close(self):
        options.fd = 0
        options.child_pid = 0


def start_server(port=8000):
    appHandlers = [
        (r'/', IndexHandler),
        (r'/pty', PtyHandler)
    ]
    appSettings = dict(
        static_path=os.path.join(os.path.dirname(__file__), "static")
    )
    app = tornado.web.Application(
        appHandlers,
        **appSettings
    )

    app.listen(port)
    tornado.ioloop.IOLoop.instance().start()


def main():
    parser = ArgumentParser(
        description=(
            'Start the webpty application and control your system from '
            ' terminal via browser.'))
    parser.add_argument(
        '-p', '--port', type=int, default=8000,
        help='Port on which to run server.')

    args = parser.parse_args()
    start_server(port=args.port)


if __name__ == "__main__":
    main()
