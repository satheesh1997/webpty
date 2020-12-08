# webpty

webpty is a simple web-based application to access shells & shell based applications in the system via a browser.


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

### Change Shell

```bash
webpty -c $SHELL
```
or
```bash
webpty --cmd=$SHELL

```

This $SHELL can be anything like bash, sh, python, vim, etc. which is present in the system.

### Change Port

```bash
webpty -p $PORT
```
or
```bash
webpty --port=$PORT

```

This creates a tornado server which will be serving your bash shell on http://localhost:$PORT/


### Change Allowed Hosts

By default, the server will accept request from all the hosts without any restriction, to
make it accept only from certain hosts

```bash
webpty -ah $ALLOWED_HOSTS
```
or
```bash
webpty --allowed-hosts=$ALLOWED_HOSTS
```
This creates a tornado server which  allows only requests from $ALLOWED_HOSTS.

This $ALLOWED_HOSTS should be list of strings seperated by a comma. 


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.


## -
![Python Powered](https://www.python.org/static/community_logos/python-powered-h-70x91.png)

