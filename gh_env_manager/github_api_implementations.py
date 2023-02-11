"""Module containing the implementations for each of the GitHub API classes along with their respective configurations"""
from .github_api_class import GitHubApi


class RepositoryGitHubApi(GitHubApi):
    def __init__(self, private_key: str, repository: str) -> None:
        super().__init__(private_key)
        self.get_public_key_endpoint = f"repos/{repository}/actions/secrets/public-key"
        self.get_public_key()
        self.current_parent_type = f"REPOSITORY {repository} ENVIRONMENT '{str(None)}':"

        self.secrets_endpoint = f"repos/{repository}/actions/secrets"
        self.variables_endpoint = f"repos/{repository}/actions/variables"


class EnvironmentGitHubApi(GitHubApi):
    def __init__(self, private_key: str, repository: str, environment_name: str) -> None:
        super().__init__(private_key)
        self.current_parent_type = f"REPOSITORY {repository} ENVIRONMENT '{environment_name}':"
        self.get_repository_id(repository)  # update repository id

        self.get_public_key_endpoint = f"repositories/{self.repository_id}/environments/{environment_name}/secrets/public-key"
        self.get_public_key()

        self.secrets_endpoint = f"repositories/{self.repository_id}/environments/{environment_name}/secrets"
        self.variables_endpoint = f"repositories/{self.repository_id}/environments/{environment_name}/variables"
