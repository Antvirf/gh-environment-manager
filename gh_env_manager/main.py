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


@app.command()
def main(
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
    yaml_dict = YamlEnv(".env.yaml").get_dict()

    if "GH_SECRET_SYNC_KEY" not in yaml_dict:
        raise ValueError(
            "'GH_SECRET_SYNC_KEY' not found in the given .env file, aborting")

    # process organizations, if available in the dictionary
    # for org_name, org_data in (yaml_dict["organizations"] if "organizations" in yaml_dict else {}).items():
    #     api = OrganizationGitHubApi()
    #     repo_api.create_secrets(repo_name, repo_data)
    #     repo_api.create_variables(repo_name, repo_data)

    # here - somehow split the dict into 'new' vs. 'existing to update' vs. 'for deletion'

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
