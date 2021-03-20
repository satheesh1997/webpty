import os
import pathlib
import requests

from argparse import ArgumentParser


BASE_PATH = os.path.join(pathlib.Path().absolute(), 'webpty')


class StaticBuilder:
    """
    Build the static files.
    """

    CSS_FILE = os.path.join(BASE_PATH, 'static', 'webpty.css')
    JS_FILE = os.path.join(BASE_PATH, 'static', 'webpty.js')

    @classmethod
    def minify_css(cls):
        """
        Minify css file.
        """

        with open(cls.CSS_FILE, "r") as css_file:
            css = css_file.read()

        response = requests.post('https://cssminifier.com/raw', {'input': css})

        if response.status_code != 200:
            raise ConnectionError("Failed to minify css file")

        with open(cls.CSS_FILE.rstrip('.css') + '.min.css', 'w') as minify_css:
            minify_css.write(response.text)

    @classmethod
    def minify_js(cls):
        """
        Minify js file.
        """

        with open(cls.JS_FILE, "r") as js_file:
            js = js_file.read()

        response = requests.post(
            'https://javascript-minifier.com/raw', {'input': js})

        if response.status_code != 200:
            raise ConnectionError("Failed to minify js file")

        with open(cls.JS_FILE.rstrip('.js') + '.min.js', 'w') as minify_js:
            minify_js.write(response.text)

    @classmethod
    def build(cls):
        """
        Build the static files.
        """
        cls.minify_css()
        cls.minify_js()


if __name__ == "__main__":
    parser = ArgumentParser(
        description=(
            "Trigger a builder."
        )
    )
    parser.add_argument(
        "-b", "--builder", type=str, default="static-files", help="builder class to run"
    )
    args = parser.parse_args()
    available_builders = {
        "static-files": StaticBuilder
    }
    builder = available_builders.get(args.builder, None)
    if not builder:
        raise NotImplementedError(
            f"Builder {args.builder} is not implemented.")
    builder.build()
