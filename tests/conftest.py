import pytest
import yaml

import gh_env_manager.github_api_class
import gh_env_manager.github_api_implementations
import gh_env_manager.secret_variable_entity_class
import gh_env_manager.yaml_env_class

TARGET_TEST_REPOSITORY = "Antvirf/gh-environment-manager"


@pytest.fixture(scope='session')
def path_to_test_yaml():
    return "./tests/test.yml"


@pytest.fixture(scope='session')
def test_yaml(path_to_test_yaml):
    with open(path_to_test_yaml, 'r') as file_stream:
        data = yaml.safe_load(file_stream)
    return data


@pytest.fixture(scope='session')
def gh_repo_api(test_yaml):
    api = gh_env_manager.github_api_implementations.RepositoryGitHubApi(
        private_key=test_yaml["GH_SECRET_SYNC_KEY"],
        repository="Antvirf/gh-environment-manager"
    )
    return api


@pytest.fixture(scope='session')
def gh_env_api(test_yaml):
    api = gh_env_manager.github_api_implementations.EnvironmentGitHubApi(
        private_key=test_yaml["GH_SECRET_SYNC_KEY"],
        repository="Antvirf/gh-environment-manager",
        environment_name="dev"
    )
    return api


@pytest.fixture(scope='session')
def yaml_env_list_object():
    return gh_env_manager.yaml_env_class.YamlEnvFromList(
        [
            gh_env_manager.secret_variable_entity_class.Secret(
                name="SECRET", value="value", repo="repo_name"),
            gh_env_manager.secret_variable_entity_class.Variable(
                name="Invalidly named variable", value="value", repo="repo_name"),
        ]
    )


@pytest.fixture(scope='session')
def yaml_env_object():
    return gh_env_manager.yaml_env_class.YamlEnv("./tests/test.yml")


@pytest.fixture(scope='session')
def repo_additional_secrets_to_create():
    return [
        gh_env_manager.secret_variable_entity_class.Secret(
            name="FIRST_SECRET",
            value="value of first secret",
            repo=TARGET_TEST_REPOSITORY
        ),
        gh_env_manager.secret_variable_entity_class.Secret(
            name="SECOND_SECRET",
            value="value of second secret",
            repo=TARGET_TEST_REPOSITORY
        )
    ]


@pytest.fixture(scope='session')
def repo_additional_secrets_to_create_dicts():
    return [
        {"FIRST_SECRET": None},
        {"SECOND_SECRET": None}
    ]


@pytest.fixture(scope='session')
def repo_additional_variables_to_create():
    return [
        gh_env_manager.secret_variable_entity_class.Variable(
            name="FIRST_VARIABLE",
            value="value of first variable",
            repo=TARGET_TEST_REPOSITORY
        ),
        gh_env_manager.secret_variable_entity_class.Variable(
            name="SECOND_VARIABLE",
            value="value of second variable",
            repo=TARGET_TEST_REPOSITORY
        )
    ]


@pytest.fixture(scope='session')
def repo_additional_variables_to_create_dicts():
    return [
        {"FIRST_VARIABLE": "value of first variable"},
        {"SECOND_VARIABLE": "value of second variable"}
    ]
