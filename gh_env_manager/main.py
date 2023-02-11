"""
GitHub Environment Manager

"""
import logging
from typing import Optional

import typer

from .github_api_implementations import (EnvironmentGitHubApi,
                                         RepositoryGitHubApi)
from .yaml_env_class import YamlEnv, YamlEnvFromList

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(levelname)s: %(message)s')

app = typer.Typer()


@app.command(help="Read given YAML file and output the interpreted contents.")
def read(path_to_file: str = typer.Argument(...)):
    yaml_env_file = YamlEnv(path_to_file)
    print(
        f"Config file from {path_to_file} interpreted successfully:\n", yaml_env_file)


@app.command(help="Fetch all secrets and all variables from the specific GitHub repositories "
             "provided in your environment YAML file.")
def fetch(path_to_file: str = typer.Argument(...),
          output: bool = typer.Option(True, help="Option that enables/disables output.")):
    # read yaml into environments dictionary
    yaml_env = YamlEnv(path_to_file, output=output)
    gh_env = YamlEnv()
    if not yaml_env.key:
        raise ValueError(
            "'GH_SECRET_SYNC_KEY' not found in the given .env file, aborting")

    logging.info(
        "Fetching current state of your repositories from GitHub...")
    all_repositories = yaml_env.get_repositories()
    for repo_name in all_repositories:
        for env_name in yaml_env.get_environments(repo_name):
            if env_name is None:
                repo_api = RepositoryGitHubApi(
                    private_key=yaml_env.key,
                    repository=repo_name
                )

                gh_env.append_entities(
                    {
                        "secrets": repo_api.list_secrets(),
                        "variables": repo_api.list_variables()
                    },
                    repo=repo_name,
                    env=env_name
                )
            else:
                env_api = EnvironmentGitHubApi(
                    private_key=yaml_env.key,
                    repository=repo_name,
                    environment_name=env_name
                )
                gh_env.append_entities(
                    {
                        "secrets": env_api.list_secrets(),
                        "variables": env_api.list_variables()
                    },
                    repo=repo_name,
                    env=env_name
                )

    if output:
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
    delete_nonexisting_without_prompt: Optional[bool] = typer.Option(
        False,
        "--delete-nonexisting-without-prompt",
        show_default=True,
        help="Applies the same commands as delete_nonexisting, but without prompting the user "
        "for confirmation."),

):
    if delete_nonexisting_without_prompt:
        delete_nonexisting = True
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

    number_of_items_to_update = len(yaml_env.get_active_data())
    if number_of_items_to_update == 0:
        logging.info("Nothing to update or add.")
    else:
        logging.info(f"{number_of_items_to_update} entities will be updated.")

    all_repositories = yaml_env.get_repositories()
    for repo_name in all_repositories:
        for env_name in yaml_env.get_environments(repo_name):
            if env_name is None:
                RepositoryGitHubApi(
                    private_key=yaml_env.key,
                    repository=repo_name
                )\
                    .create_entities(
                        entities_list=yaml_env.get_entities_from_environment(
                            repo_name, env_name)
                )
            else:
                EnvironmentGitHubApi(
                    private_key=yaml_env.key,
                    repository=repo_name,
                    environment_name=env_name
                )\
                    .create_entities(
                        entities_list=yaml_env.get_entities_from_environment(
                            repo_name, env_name)
                )

    if number_of_items_to_update != 0:
        logging.info(
            f"Updates complete, {len(yaml_env.get_active_data())} entities changed.")

    if not delete_nonexisting:
        return

    for_deletion_env = YamlEnvFromList(existing_in_gh_only, output=False)
    for_deletion_env.key = yaml_env.key
    number_of_items_to_delete = len(for_deletion_env.get_active_data())

    if number_of_items_to_delete == 0:
        logging.info("Nothing to delete.")
        return

    logging.info(
        f"{number_of_items_to_delete} entities will be deleted.")
    logging.info("The following Secrets and Variables will be DELETED without replacement.\n"
                 + str(for_deletion_env))

    if not delete_nonexisting_without_prompt:
        user_input = input("Continue? (Only 'yes' is accepted) :  ")
        if user_input != 'yes':
            logging.warning(
                "Invalid input, aborting. No deletions have been made.")
            return

    all_repositories = for_deletion_env.get_repositories()
    for repo_name in all_repositories:
        for env_name in for_deletion_env.get_environments(repo_name):
            if env_name is None:
                RepositoryGitHubApi(
                    private_key=for_deletion_env.key,
                    repository=repo_name
                ) \
                    .delete_entities(
                    entities_list=for_deletion_env.get_entities_from_environment(
                        repo_name, env_name)
                )
            else:
                EnvironmentGitHubApi(
                    private_key=for_deletion_env.key,
                    repository=repo_name,
                    environment_name=env_name
                ) \
                    .delete_entities(
                    entities_list=for_deletion_env.get_entities_from_environment(
                        repo_name, env_name)
                )
    logging.info("Deletions complete.")


if __name__ == "__main__":
    app()
