# Contributing guide

## Usage

### New system

1. Install [pyenv](https://github.com/pyenv/pyenv) and run `pyenv install X.Y` to install Python X.Y
1. [Install pipx](https://pipx.pypa.io/stable/installation/)
1. [Install poetry](https://python-poetry.org/docs/#installing-with-pipx) with `--python pythonX.Y`
1. Install [poetry-shell-plugin](https://github.com/python-poetry/poetry-plugin-shell)

Optionally, set up [remote development using SSH](https://code.visualstudio.com/docs/remote/ssh) by using the following prompt:

```
I want to set up remote development using the Visual Studio Code Remote - SSH extension. I am connecting to my Host named {Host} with HostName {HostName}, User {User}, Port {Port}, and IdentityFile named {DeviceName}.pem. Please walk me through setting this up on my {system: Windows, M-series Mac OS, Ubuntu} device step by step, including creating an Ed25519 key pair in PEM format.
```

If on Mac OS, make sure to [give Local Network access to VS Code](https://github.com/microsoft/vscode/issues/228862#issuecomment-2358636415).

### New clone of repository

```
poetry install
poetry run pre-commit install --hook-type pre-commit --hook-type commit-msg
poetry env use pythonX.Y
```

### New terminal

```
poetry shell
```

### New dependencies

Development-only dependencies:

```
poetry add --group dev pkgname
```

Production/runtime dependencies:

```
poetry add pkgname
```

### New code

```
pytest tests

pylint **/*.py
```

### New staged changes

```
pre-commit run
```
