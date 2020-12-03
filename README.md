# webpty

webpty a simple web-based application to access shells & shell based applications in the system via a browser.


[![PyPI version](https://badge.fury.io/py/webpty.svg)](https://badge.fury.io/py/webpty)

## Screenshots

#### Bash Shell
![Online Bash Shell](https://imgur.com/iNoW3jL.png)

#### Python Shell
![Online Python Shell](https://imgur.com/YYK4YXs.png)

#### VIM
![Online Vim](https://imgur.com/vfei1Ri.png)


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install webpty.

```bash
pip install webpty
```

## Usage

```bash
webpty
```

This creates a tornado server which will be serving your bash shell on http://localhost:8000/

### Change shell

```bash
webpty -c $SHELL
```
or
```bash
webpty --cmd=$SHELL

```

This $SHELL can be anything like bash, sh, python, vim, etc. which is present in the system.

### Change port

```bash
webpty -p $PORT
```
or
```bash
webpty --port=$PORT

```

This creates a tornado server which will be serving your bash shell on http://localhost:$PORT/

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.


## -
![Python Powered](https://www.python.org/static/community_logos/python-powered-h-70x91.png)

