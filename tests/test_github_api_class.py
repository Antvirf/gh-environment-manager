import pytest
import yaml

import gh_env_manager.github_api_class
import gh_env_manager.github_api_implementations


@pytest.fixture(scope='session')
def test_yaml():
    with open("./tests/test.yml", 'r') as file_stream:
        data = yaml.safe_load(file_stream)
    return data


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

# secrets


def test_github_api_create_secret():
    pass


def test_github_api_get_secret():
    pass


def test_github_api_list_secret():
    pass


def test_github_api_delete_secret():
    pass


# variables
def test_github_api_create_variable():
    pass


def test_github_api_patch_variable():
    pass


def test_github_api_get_variable():
    pass


def test_github_api_list_variable():
    pass


def test_github_api_delete_variable():
    pass


def test_github_api_create_entities():
    pass


def test_github_api_delete_entities():
    pass


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
