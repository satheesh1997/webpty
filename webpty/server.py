"""
Copyright 2019 by Satheesh Kumar D.

Maintainer:
    -> Satheesh Kumar D <mail@satheesh.dev>
"""

import fcntl
import json
import logging
import os
import pty
import select
import struct
import subprocess
import termios

from argparse import ArgumentParser

from tornado import gen
from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornado.web import RequestHandler, Application
from tornado.websocket import WebSocketHandler, WebSocketClosedError

from webpty import __version__


define("process_id", 0)  # process id given by pty.fork()
define("file_descriptor", 0)  # file descriptor given by pty.fork()


@gen.coroutine
def read_and_update_web_terminal(instance):
    while True:
        yield gen.sleep(0.01)
        if options.file_descriptor:
            (output_generated, _, _) = select.select(
                [options.file_descriptor], [], [], 0
            )
            if output_generated:
                output = os.read(options.file_descriptor, 1024 * 20).decode(
                    "utf-8", "ignore"
                )
                try:
                    instance.write_message(output)
                except WebSocketClosedError:
                    logging.error(
                        "WebSocketClosedError: socket connection with the client is not open"
                    )
                    break

        else:
            break


class IndexHandler(RequestHandler):
    def get(self):
        self.render(
            "index.html",
            app_version=__version__,
            is_secured=True if options.password else False,
            keepalive=options.keepalive,
        )


class AuthHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")

    def post(self):
        if options.password:
            data = json.loads(self.request.body) if self.request.body else {}
            webpty_pass = data.get("webptyPass", None)
            if webpty_pass and webpty_pass == options.password:
                self.set_cookie("webptyPass", options.password)
                self.write(json.dumps({"status": "OK"}))
            else:
                self.write(
                    json.dumps({"status": "NOK", "message": "Invalid password!!"})
                )
        else:
            self.write(
                json.dumps(
                    {"status": "OK", "message": "This is not an secured application"}
                )
            )


class PtyHandler(WebSocketHandler):
    def check_origin(self, *args, **kwargs):
        if options.allowed_hosts:
            return self.request.host in options.allowed_hosts
        return True

    def open(self):
        if options.password:
            client_password = self.get_cookie("webptyPass")
            if not client_password or not client_password == options.password:
                logging.info("Closing user connection due to invalid password!!")
                self.close()

        if options.process_id:
            return

        (process_id, file_descriptor) = pty.fork()

        if process_id == 0:
            subprocess.run(options.cmd, check=False)
        else:
            options.process_id = process_id
            options.file_descriptor = file_descriptor
            read_and_update_web_terminal(self)

    def on_message(self, message):
        message = json.loads(message)
        logging.debug("Message: %s", message)

        action = message.get("action")
        data = message.get("data")

        if action == "resize":
            terminalsize = struct.pack(
                "HHHH", data.get("rows", 50), data.get("cols", 50), 0, 0
            )
            fcntl.ioctl(options.file_descriptor, termios.TIOCSWINSZ, terminalsize)
        elif action == "input":
            os.write(options.file_descriptor, data["key"].encode())

    def on_close(self):
        options.process_id = 0
        options.file_descriptor = 0


def start_server():
    handlers = [(r"/", IndexHandler), (r"/pty", PtyHandler), (r"/auth", AuthHandler)]
    settings = dict(static_path=os.path.join(os.path.dirname(__file__), "static"))
    app = Application(handlers, **settings)
    app.listen(options.port, "0.0.0.0")

    try:
        logging.info("Application listening on http://0.0.0.0:%s/", options.port)

        if options.password:
            logging.info("Application secured with the password!!")

        IOLoop.instance().start()
    except KeyboardInterrupt:
        pass


def main():
    parser = ArgumentParser(
        description=(
            "A web-based application to access shell & shell based applications via a browser"
        )
    )
    parser.add_argument(
        "-p", "--port", type=int, default=8000, help="port to expose the webpty server."
    )
    parser.add_argument(
        "-c",
        "--cmd",
        type=str,
        default="bash",
        help="command to start a shell application, eg: (vim) to start vim.",
    )
    parser.add_argument(
        "-ah",
        "--allowed-hosts",
        type=str,
        default=None,
        help="allows request from the hosts specified, eg: 127.0.0.1, satheesh.dev.",
    )
    parser.add_argument(
        "-pass",
        "--password",
        type=str,
        default=None,
        help="password which will be used to secure the application",
    )
    parser.add_argument(
        "-k",
        "--keepalive",
        type=int,
        default=0,
        help="interval(in seconds) at which heartbeat check is done(bydefault 0 to disable check)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s - %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if args.allowed_hosts:
        allowed_hosts = args.allowed_hosts.split(",")
        logging.debug("Using allowed_hosts: %s", args.allowed)
    else:
        allowed_hosts = []

    define("cmd", args.cmd)
    logging.debug("Using cmd: %s", args.cmd)

    define("port", args.port)
    logging.debug("Using port: %s", args.port)

    define("allowed_hosts", allowed_hosts)
    define("password", args.password)

    define("keepalive", args.keepalive)

    start_server()


if __name__ == "__main__":
    main()
