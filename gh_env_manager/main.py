"""
GitHub Environment Manager

"""
import logging
from typing import Optional

import typer

from .github_api_class import GitHubApi
from .yaml_env_class import YamlEnv

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(levelname)s: %(message)s')

app = typer.Typer()


class RepositoryGitHubApi(GitHubApi):
    def __init__(self, private_key: str, repository: str) -> None:
        super().__init__(private_key)
        self.get_public_key_endpoint = f"repos/{repository}/actions/secrets/public-key"
        self.get_public_key()
        self.current_parent_type = "REPOSITORY"

        # secrets
        self.get_secret_endpoint = f"repos/{repository}/actions/secrets"
        self.list_secret_endpoint = f"repos/{repository}/actions/secrets"
        self.create_secret_endpoint = f"repos/{repository}/actions/secrets"

        # variables
        self.get_variable_endpoint = f"repos/{repository}/actions/variables"
        self.list_variable_endpoint = f"repos/{repository}/actions/variables"
        self.create_variable_endpoint = f"repos/{repository}/actions/variables"


class EnvironmentGitHubApi(GitHubApi):
    def __init__(self, private_key: str, repository: str, environment_name) -> None:
        super().__init__(private_key)
        self.current_parent_type = f"Repo {repository}: ENVIRONMENT"

        self.get_repository_id(repository)  # update repository id

        self.get_public_key_endpoint = f"repositories/{self.repository_id}/environments/{environment_name}/secrets/public-key"
        self.get_public_key()

        # secrets
        self.get_secret_endpoint = f"repositories/{self.repository_id}/environments/{environment_name}/secrets"
        self.list_secret_endpoint = f"repositories/{self.repository_id}/environments/{environment_name}/secrets"
        self.create_secret_endpoint = f"repositories/{self.repository_id}/environments/{environment_name}/secrets"

        # variables
        self.get_variable_endpoint = f"repositories/{self.repository_id}/environments/{environment_name}/variables"
        self.list_variable_endpoint = f"repositories/{self.repository_id}/environments/{environment_name}/variables"
        self.create_variable_endpoint = f"repositories/{self.repository_id}/environments/{environment_name}/variables"


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

    # read yaml into environments dictionary
    env_dict = YamlEnv(".env.yaml").get_dict()

    if "GH_SECRET_SYNC_KEY" not in env_dict:
        raise ValueError(
            "'GH_SECRET_SYNC_KEY' not found in the given .env file, aborting")

    # process organizations
    if "organizations" in env_dict:
        for org in env_dict["organizations"]:
            current_org_data = env_dict["organizations"][org]
            #api = OrganizationGitHubApi()
            if "secrets" in current_org_data:
                pass
            if "variables" in current_org_data:
                pass

    # process repositories
    if "repositories" in env_dict:
        for repo in env_dict["repositories"]:
            current_repo_data = env_dict["repositories"][repo]
            api = RepositoryGitHubApi(env_dict["GH_SECRET_SYNC_KEY"], repo)

            if "secrets" in current_repo_data:
                api.create_secrets(repo, current_repo_data["secrets"])

            if "variables" in current_repo_data:
                api.create_variables(repo, current_repo_data["variables"])

            if "environments" in current_repo_data:
                for env in current_repo_data["environments"]:
                    current_env_data = current_repo_data["environments"][env]
                    envApi = EnvironmentGitHubApi(
                        env_dict["GH_SECRET_SYNC_KEY"],
                        repository=repo,
                        environment_name=env)
                    if "secrets" in current_env_data:
                        envApi.create_secrets(env, current_env_data["secrets"])
                    if "variables" in current_env_data:
                        envApi.create_variables(
                            env, current_env_data["variables"])

    # # TODO - Make this into a Command Line Tool, take path into env file as argument
    # # TODO - Delete non-existing secrets
    # # TODO - Default behaviour - ADD only, do not overwrite
    # # TODO - CLI: -u flag to update secrets where we provide a value
    # # TODO - CLI: --delete-repo-secrets-missing-from-new-list


if __name__ == "__main__":
    app()
