import pytest

import gh_env_manager.github_api_class
import gh_env_manager.github_api_implementations


def test_github_make_request():
    api = gh_env_manager.github_api_class.GitHubApi(
        key="",
        api_url="https://google.com"
    )
    api._make_request(
        endpoint="")


def test_github_unsupported_method():
    api = gh_env_manager.github_api_class.GitHubApi(
        key="",
    )
    with pytest.raises(NotImplementedError):
        api._make_request(
            endpoint="",
            method="notimplemented")


def test_github_empty_input_to_delete_entities(gh_repo_api):
    gh_repo_api.delete_entities([])


def test_github_empty_inpucreate_entities(gh_repo_api):
    gh_repo_api.create_entities([])


def test_github_implementation_repo(test_yaml):
    api = gh_env_manager.github_api_implementations.RepositoryGitHubApi(
        private_key=test_yaml["GH_SECRET_SYNC_KEY"],
        repository="Antvirf/gh-environment-manager"
    )
    api.get_public_key()
    assert f"REPOSITORY Antvirf/gh-environment-manager ENVIRONMENT '{str(None)}':" == api.current_parent_type
    assert f"repos/Antvirf/gh-environment-manager/actions/secrets/public-key" == api.get_public_key_endpoint
    assert f"repos/Antvirf/gh-environment-manager/actions/secrets" == api.secrets_endpoint
    assert f"repos/Antvirf/gh-environment-manager/actions/variables" == api.variables_endpoint


def test_github_implementation_repo_env(test_yaml):
    api = gh_env_manager.github_api_implementations.EnvironmentGitHubApi(
        private_key=test_yaml["GH_SECRET_SYNC_KEY"],
        repository="Antvirf/gh-environment-manager",
        environment_name="dev"
    )
    api.get_public_key()
    api.get_repository_id("Antvirf/gh-environment-manager")

    assert str(api.repository_id) == str(598437204)
    assert f"REPOSITORY Antvirf/gh-environment-manager ENVIRONMENT 'dev':" == api.current_parent_type
    assert f"repositories/598437204/environments/dev/secrets" == api.secrets_endpoint
    assert f"repositories/598437204/environments/dev/variables" == api.variables_endpoint
