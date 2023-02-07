# GitHub Environment Manager - `gh_env_manager`

![Pytest coverage](./badges/coverage.svg)
![Python](https://img.shields.io/badge/python-3.9%20-blue)

## Installation

```bash
pip install gh-env-manager
```

## Quick start guide

```bash
gh-env-manager path_to_your_env_file.yml
```

---

### Usage

```console
$ gh_env_manager [OPTIONS] PATH_TO_FILE
```

### Arguments

* `PATH_TO_FILE`: [required]

### Options

* `-o, --overwrite`: If enabled, overwrite existing secrets and values in GitHub to match the provided YAML file.  [default: False]
* `-d, --delete-nonexisting`: If enabled, delete secrets and variables that are not found in the provided YAML file.  [default: False]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.
