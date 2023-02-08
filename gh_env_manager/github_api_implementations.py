"""Module containing the implementations for each of the GitHub API classes along with their respective configurations"""
from .github_api_class import GitHubApi


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
    def __init__(self, private_key: str, repository: str, environment_name: str) -> None:
        super().__init__(private_key)
        self.current_parent_type = f"REPOSITORY ENVIRONMENT '{repository}':"

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


class OrganizationGitHubApi(GitHubApi):
    def __init__(self, private_key: str, organization_name: str) -> None:
        super().__init__(private_key)
        self.current_parent_type = f"ORGANIZATION"

        self.get_public_key_endpoint = f"orgs/{organization_name}/actions/secrets/public-key"
        self.get_public_key()

        # secrets
        self.get_secret_endpoint = f"orgs/{organization_name}/actions/secrets"
        self.list_secret_endpoint = f"orgs/{organization_name}/actions/secrets"
        self.create_secret_endpoint = f"orgs/{organization_name}/actions/secrets"

        # variables
        self.get_variable_endpoint = f"orgs/{organization_name}/actions/variables"
        self.list_variable_endpoint = f"orgs/{organization_name}/actions/variables"
        self.create_variable_endpoint = f"orgs/{organization_name}/actions/variables"
