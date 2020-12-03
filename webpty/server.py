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


define("process_id", 0) # process id given by pty.fork()
define("file_descriptor", 0) # file descriptor given by pty.fork()


@gen.coroutine
def read_and_update_web_terminal(instance):
    while True:
        yield gen.sleep(0.01)
        if options.file_descriptor:
            (output_generated, _, _) = select.select(
                [options.file_descriptor],
                [],
                [],
                0
            )
            if output_generated:
                output = os.read(options.file_descriptor, 1024 * 20).decode()
                instance.write_message(output)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class PtyHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        if options.process_id:
            return

        (process_id, file_descriptor) = pty.fork()
        if process_id == 0:
            subprocess.run(options.cmd)
        else:
            options.process_id = process_id
            options.file_descriptor = file_descriptor
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
            fcntl.ioctl(options.file_descriptor, termios.TIOCSWINSZ, terminalsize)
        elif action == "input":
            os.write(options.file_descriptor, data["key"].encode())

    def on_close(self):
        options.process_id = 0
        options.file_descriptor = 0


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

    print(f"Server listening on http://0.0.0.0:{options.port}")
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
