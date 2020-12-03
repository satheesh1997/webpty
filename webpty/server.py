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


define("cpid", 0)
define("ppid", 0)


@gen.coroutine
def read_and_update_web_terminal(instance):
    while True:
        yield gen.sleep(0.01)
        if options.ppid:
            (output_generated, _, _) = select.select(
                [options.ppid],
                [],
                [],
                0
            )
            if output_generated:
                output = os.read(options.ppid, 1024 * 20).decode()
                instance.write_message(output)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class PtyHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        if options.cpid:
            return

        (cpid, ppid) = pty.fork()
        if cpid == 0:
            subprocess.run(options.cmd)
        else:
            options.ppid = ppid
            options.cpid = cpid
            read_and_update_web_terminal(self)

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
            fcntl.ioctl(options.ppid, termios.TIOCSWINSZ, terminalsize)
        elif action == "input":
            os.write(options.ppid, data["key"].encode())

    def on_close(self):
        options.ppid = 0
        options.cpid = 0


def start_server():
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

    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


def main():
    parser = ArgumentParser(
        description=(
            'Start the webpty application and control your system from '
            ' terminal via browser.'))
    parser.add_argument(
        '-p', '--port', type=int, default=8000,
        help='Port on which to run server.')
    parser.add_argument(
        '-c', '--cmd', type=str, default="bash",
        help='Initial command to run in the shell')
    args = parser.parse_args()
    define("cmd", args.cmd)
    define("port", args.port)

    start_server()


if __name__ == "__main__":
    main()
