# GitHub Environment Manager - `gh_env_manager`

[![PyPI version](https://badge.fury.io/py/gh-env-manager.svg)](https://badge.fury.io/py/gh-env-manager)
![Pytest coverage](./.github/badges/coverage.svg)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=Antvirf_gh-environment-manager&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=Antvirf_gh-environment-manager)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=Antvirf_gh-environment-manager&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=Antvirf_gh-environment-manager)
![Python](https://img.shields.io/badge/python-3.9%20-blue)

GitHub Environment Manager helps you maintain GitHub Actions [Secrets](https://docs.github.com/en/rest/actions/secrets?apiVersion=2022-11-28) and [Variables](https://docs.github.com/en/rest/actions/variables?apiVersion=2022-11-28) across your repositories, and [environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment) within them. You provide your target state in the form of a `YAML` file - the desired Secrets and Variables that your repositories and their environments should contain - and the tool does the rest.

## Installation

```bash
pip install gh-env-manager
```

---

## Quick start to update entities in your repositories

`gh-env-manager` requires as an input a `YAML` file that describes the target state of your GitHub repository (or repositories) and its (their) Secrets and Variables. It does **not** create any repositories or environments for you - so every repository, and every environment within your repositories, that you add to the configuration must exist already. The tool maintains the entities - Secrets and Variables - within.

1. Install this tool with `pip install gh-env-manager`
1. Create a GitHub personal access token following [this guide from GitHub](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
1. Create a `YAML` file that describes your target state, following the format below. You can also check the [example used for tests](./tests/test.yml).

    ```yaml
    GH_SECRET_SYNC_KEY: <your GitHub personal access token>
    
    repositories:
      username/repositoryname: # e.g. Antvirf/gh-environment-manager 
        secrets:
          - YOUR_SECRET: "something"
        variables:
          - YOUR_VARIABLE: "something" 
        environments:
          dev: # assuming 'dev' environment exists in your repository
            secrets:
              - YOUR_DEV_SECRET: "something"
            variables:
              - YOUR_DEV_VARIABLE: "something"
    
    ```

1. Run `gh-env-manager fetch ./path_to_your_yaml_file` to get current state of your repositories
1. Run `gh-env-manager update ./path_to_your_yaml_file` to push the contents of the `YAML` file to your repositories
    * By default, nothing is overwritten - if an entity exists already, it is **NOT** updated. Use the `--overwrite` flag to enable that behaviour.
    * By default, nothing is deleted - if your repository has an entity that is not in the `YAML` file, it is ignored. Use the `--delete-nonexisting` or `--delete-nonexisting-without-prompt` to delete any secret or variable from your repository that was missing from your input `YAML` file.

## Usage

`PATH_TO_FILE` is always required for each command.

```bash
$ gh_env_manager [COMMANDS] PATH_TO_FILE [OPTIONS]

# examples
$ gh_env_manager read .env.yaml
$ gh_env_manager fetch .env.yaml
$ gh_env_manager update .env.yaml

# to overwrite existing entries
$ gh_env_manager update .env.yaml --overwrite 

# to delete any secret/variable missing from your YAML
$ gh_env_manager update .env.yaml --delete-nonexisting

# fully sync your repository with the contents of the yaml by updating all values, and deleting any that are not present
$ gh_env_manager update .env.yaml --overwrite --delete-nonexisting-without-prompt 
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

## FAQ

1. Why do secrets sometimes state their value as `None`?
    1. GitHub Secrets API does **NOT** support fetching the *value* of a secret, and hence they are shown as `None` when data coming *from* GitHub is output.

## Known missing features & potential roadmap items

* Support for GitHub Organizations (see API ref for [org Variables](https://docs.github.com/en/rest/actions/variables?apiVersion=2022-11-28#list-organization-variables), [org Secrets](https://docs.github.com/en/rest/actions/secrets?apiVersion=2022-11-28#list-organization-secrets))
  * Potentially support for scoped secrets and variables (ability to set visibility at repo level)
