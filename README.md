# webpty

Web based application to access shell & shell based applications via a browser.

[![PyPI version](https://badge.fury.io/py/webpty.svg)](https://badge.fury.io/py/webpty)

#

## Installation

Use [pip](https://pip.pypa.io/en/stable/) and install webpty.

```bash
pip install webpty
```

## Usage

```bash
webpty
```

Creates a tornado server which will be serving bash shell on http://localhost:8000/

### Change Shell

```bash
webpty -c $SHELL
```

or

```bash
webpty --cmd=$SHELL

```

This $SHELL can be bash, sh, python, vim, wtfutil, etc. that is available in the system.

### Change Port

```bash
webpty -p $PORT
```

or

```bash
webpty --port=$PORT

```

Creates a tornado server that server on the specified port http://localhost:$PORT/

### Change Allowed Hosts

By default, server will accept request from all the hosts without any restriction, to make it accept only from certain hosts,

```bash
webpty -ah $ALLOWED_HOSTS
```

or

```bash
webpty --allowed-hosts=$ALLOWED_HOSTS
```

Server accepts only requests from $ALLOWED_HOSTS. This $ALLOWED_HOSTS should be list of strings seperated by a comma.

#

## Screenshots

#### Bash

![Online Bash Shell](https://imgur.com/iNoW3jL.png)

#### Python

![Online Python Shell](https://imgur.com/YYK4YXs.png)

#### Vim

![Online Vim](https://imgur.com/vfei1Ri.png)

#

## Contributing

Pull requests are welcome. Raise a issue and start a discussion before submitting a pr.

#

![Python Powered](https://www.python.org/static/community_logos/python-powered-h-70x91.png)
