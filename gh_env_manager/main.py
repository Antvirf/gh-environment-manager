"""
GitHub Environment Manager

"""
import logging
from typing import Optional

import typer

from .github_api_implementations import (EnvironmentGitHubApi,
                                         RepositoryGitHubApi)
from .yaml_env_class import YamlEnv

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(levelname)s: %(message)s')

app = typer.Typer()


@app.command(help="Read given YAML file and output the interpreted contents.")
def read(path_to_file: str = typer.Argument(...)):
    yaml_env_file = YamlEnv(path_to_file)
    yaml_dict = yaml_env_file.get_dict()
    print(
        f"\nConfig file from {path_to_file} interpreted successfully:\n", yaml_env_file, end="\n")


@app.command(help="Fetch secrets and variables from the GitHub repositories provided in your "
             "environment YAML file.")
def fetch(path_to_file: str = typer.Argument(...)):
    # read yaml into environments dictionary
    yaml_env_file = YamlEnv(path_to_file)
    yaml_dict = yaml_env_file.get_dict_containers_only()

    if "GH_SECRET_SYNC_KEY" not in yaml_dict:
        raise ValueError(
            "'GH_SECRET_SYNC_KEY' not found in the given .env file, aborting")

    for repo_name, repo_data in (yaml_dict["repositories"] if "repositories" in yaml_dict else {}).items():
        repo_api = RepositoryGitHubApi(
            yaml_dict["GH_SECRET_SYNC_KEY"], repo_name)

        yaml_dict["repositories"][repo_name]["secrets"] = repo_api.list_secrets()
        yaml_dict["repositories"][repo_name]["variables"] = repo_api.list_variables()

        for env_name, env_data in (repo_data["environments"] if "environments" in repo_data else {}).items():
            env_api = EnvironmentGitHubApi(
                yaml_dict["GH_SECRET_SYNC_KEY"],
                repository=repo_name,
                environment_name=env_name)

            yaml_dict["repositories"][repo_name]["environments"][env_name]["secrets"] = env_api.list_secrets()
            yaml_dict["repositories"][repo_name]["environments"][env_name]["variables"] = env_api.list_variables()

    print(yaml_env_file)


@ app.command(help="Update secrets and variables of the GitHub repositories using data from the "
              "provided YAML file. By default, existing secrets or variables are NOT overwritten. "
              "Try 'gh-env-manager update --help' to view the available options.")
def update(
    path_to_file: str = typer.Argument(...),  # mandatory
    overwrite: Optional[bool] = typer.Option(
        False,
        "--overwrite",
        "-o",
        show_default=True,
        help="If enabled, overwrite existing secrets and values in GitHub to match the provided YAML file.",
    ),
    delete_nonexisting: Optional[bool] = typer.Option(
        False,
        "--delete-nonexisting",
        "-d",
        show_default=True,
        help="If enabled, delete secrets and variables that are not found in the provided YAML file."),
):

    print(f"{path_to_file=}")
    print(f"{overwrite=}")
    print(f"{delete_nonexisting=}")

    # read yaml into environments dictionary
    yaml_env_file = YamlEnv(path_to_file)
    yaml_dict = yaml_env_file.get_dict()

    if "GH_SECRET_SYNC_KEY" not in yaml_dict:
        raise ValueError(
            "'GH_SECRET_SYNC_KEY' not found in the given .env file, aborting")

    # process organizations, if available in the dictionary
    # for org_name, org_data in (yaml_dict["organizations"] if "organizations" in yaml_dict else {}).items():
    #     api = OrganizationGitHubApi()
    #     repo_api.create_secrets(repo_name, repo_data)
    #     repo_api.create_variables(repo_name, repo_data)

    # process repositories, if available in the dictionary
    for repo_name, repo_data in (yaml_dict["repositories"] if "repositories" in yaml_dict else {}).items():
        repo_api = RepositoryGitHubApi(
            yaml_dict["GH_SECRET_SYNC_KEY"], repo_name)

        repo_api.create_secrets(repo_name, repo_data)
        repo_api.create_variables(repo_name, repo_data)

        for env_name, env_data in (repo_data["environments"] if "environments" in repo_data else {}).items():
            env_api = EnvironmentGitHubApi(
                yaml_dict["GH_SECRET_SYNC_KEY"],
                repository=repo_name,
                environment_name=env_name)

            env_api.create_secrets(env_name, env_data)
            env_api.create_variables(env_name, env_data)


if __name__ == "__main__":
    app()
