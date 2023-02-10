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
    print(
        f"\nConfig file from {path_to_file} interpreted successfully:\n", yaml_env_file)


@app.command(help="Fetch all secrets and all variables from the specific GitHub repositories"
             "provided in your environment YAML file.")
def fetch(path_to_file: str = typer.Argument(...),
          output: bool = typer.Option(True, help="Option that enables/disables output.")):
    # read yaml into environments dictionary
    yaml_env = YamlEnv(path_to_file, output=output)

    if not yaml_env.key:
        raise ValueError(
            "'GH_SECRET_SYNC_KEY' not found in the given .env file, aborting")

    gh_env = YamlEnv()
    if output:
        print(gh_env)

    all_repositories = yaml_env.get_repositories()
    for repo_name in all_repositories:
        for env_name in yaml_env.get_environments(repo_name):
            if env_name is None:
                repo_api = RepositoryGitHubApi(
                    private_key=yaml_env.key,
                    repository=repo_name
                )
                entities = {
                    "secrets": repo_api.list_secrets(),
                    "variables": repo_api.list_variables()
                }
                gh_env.append_entities(
                    entities, repo=repo_name, env=env_name)
            else:
                env_api = EnvironmentGitHubApi(
                    private_key=yaml_env.key,
                    repository=repo_name,
                    environment_name=env_name
                )
                entities = {
                    "secrets": env_api.list_secrets(),
                    "variables": env_api.list_variables()
                }
                gh_env.append_entities(
                    entities, repo=repo_name, env=env_name)

    if output:
        print("Current environment:")
        print(gh_env)
    return gh_env


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
        help="If enabled, delete secrets and variables from your GitHub repositories "
        "that are not found in the provided YAML file."),
):

    logging.debug(f"{path_to_file=}")
    logging.debug(f"{overwrite=}")
    logging.debug(f"{delete_nonexisting=}")

    # read yaml into environments dictionary
    yaml_env = YamlEnv(path_to_file)

    if not yaml_env.key:
        raise ValueError(
            "'GH_SECRET_SYNC_KEY' not found in the given .env file, aborting")

    # If we're not allowed to overwrite, or need to delete later, we need to now fetch from GH
    if (not overwrite) or (delete_nonexisting):
        gh_env = fetch(path_to_file=path_to_file, output=False)
        logging.debug("----------------GH contents:\n %s", str(gh_env))
        logging.debug("----------------YAML contents:\n %s", str(yaml_env))

        existing_in_env_only = yaml_env.get_existing_entities(gh_env)
        existing_in_gh_only = yaml_env.get_missing_entities(
            gh_env)  # to be used for deletions later

        # Drop any entries that exist in GH already. Also drops inactive/invalid entries.
        if not overwrite:
            yaml_env.data_content = existing_in_env_only
            logging.debug(
                "----------------YAML after drop:\n %s", str(yaml_env))

    all_repositories = yaml_env.get_repositories()
    for repo_name in all_repositories:
        for env_name in yaml_env.get_environments(repo_name):
            if env_name is None:
                repo_api = RepositoryGitHubApi(
                    private_key=yaml_env.key,
                    repository=repo_name
                )
                repo_api.create_secrets(
                    entity_name=repo_name,
                    secrets_list=yaml_env.get_secrets_from_environment(
                        repo_name, env_name)
                )
                repo_api.create_variables(
                    entity_name=repo_name,
                    variables_list=yaml_env.get_variables_from_environment(
                        repo_name, env_name)
                )
            else:
                env_api = EnvironmentGitHubApi(
                    private_key=yaml_env.key,
                    repository=repo_name,
                    environment_name=env_name
                )
                env_api.create_secrets(
                    entity_name=repo_name,
                    secrets_list=yaml_env.get_secrets_from_environment(
                        repo_name, env_name)
                )
                env_api.create_variables(
                    entity_name=repo_name,
                    variables_list=yaml_env.get_variables_from_environment(
                        repo_name, env_name)
                )
    print("Updates complete.")

    if delete_nonexisting:
        print(existing_in_gh_only)
        # Adapt the YAML ENV class so I can INIT it from a list of entries, without a file
        # Then init that here
        # Then do the standard loop and make sure delete works
        # And finally, move all of this standard to the YAML ENV class so we can keep this main file very clean


if __name__ == "__main__":
    app()
