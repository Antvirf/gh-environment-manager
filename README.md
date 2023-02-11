# GitHub Environment Manager - `gh_env_manager`

![Python](https://img.shields.io/badge/python-3.9%20-blue)
![Pytest coverage](./.github/badges/coverage.svg)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=Antvirf_gh-environment-manager&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=Antvirf_gh-environment-manager)[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=Antvirf_gh-environment-manager&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=Antvirf_gh-environment-manager)


## Installation (coming soon!)

<!-- 
```bash
pip install gh-env-manager
``` -->

---

## Usage

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
