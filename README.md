# GitHub Environment Manager - `gh_env_manager`

![Python](https://img.shields.io/badge/python-3.9%20-blue)
![Pytest coverage](./.github/badges/coverage.svg)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=Antvirf_gh-environment-manager&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=Antvirf_gh-environment-manager)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=Antvirf_gh-environment-manager&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=Antvirf_gh-environment-manager)

## Installation (coming soon!)

<!-- 
```bash
pip install gh-env-manager
``` -->

---

## Usage

`PATH_TO_FILE` is always required for each command.

```bash
$ gh_env_manager [COMMANDS] PATH_TO_FILE [OPTIONS]

# examples
$ gh_env_manager read .env.yaml
$ gh_env_manager fetch .env.yaml
$ gh_env_manager update .env.yaml
```

### Commands

* `read`:    Read given YAML file and output the interpreted contents.
* `fetch`:   Fetch all secrets and all variables from the specific GitHub repositories provided in your environment YAML file.
* `update`:  Update secrets and variables of the GitHub repositories using data from the provided YAML file. By default, existing secrets or variables are NOT overwritten. Try `gh-env-manager update --help` to view the available options.

### Options for `update`

* `-o, --overwrite`: If enabled, overwrite existing secrets and values in GitHub to match the provided YAML file.  [default: False]
* `-d, --delete-nonexisting`: If enabled, delete secrets and variables that are not found in the provided YAML file.  [default: False]
* `--delete-nonexisting-without-prompt`: Applies the same commands as `delete_nonexisting`, but without prompting the user for confirmation. [default: False]
<!-- 
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit. -->
