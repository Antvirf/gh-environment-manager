import pytest
import yaml

import gh_env_manager.secret_variable_entity_class
import gh_env_manager.yaml_env_class


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


def test_remove_null_keys():
    test_dict = {
        'secrets': [  # keep as-is
            {'name1': 'value1'},
            {'name2': 'value2'},
        ],
        'drop_me': [{}],
        'drop_me_too': [],
        'header': {  # header won't be dropped..
            # ... but the key that links to something entry will be dropped.
            "drop_me_three": []
        }

    }
    gh_env_manager.yaml_env_class.remove_null_keys(test_dict)

    assert test_dict.get('secrets', None) is not None
    assert test_dict.get('drop_me', None) is None
    assert test_dict.get('drop_me_too', None) is None
    assert test_dict.get('header', None) is not None
    assert test_dict['header'].get('drop_me_three', None) is None


def test_yaml_env_inits():
    # no path - works fine
    gh_env_manager.yaml_env_class.YamlEnv(
        path_to_yaml_env_file=None)

    # wrong path
    with pytest.raises(FileNotFoundError):
        gh_env_manager.yaml_env_class.YamlEnv(
            path_to_yaml_env_file="asdasdasd")

    # invalid file / YAML read fails - try to read this test file
    with pytest.raises(yaml.YAMLError):
        gh_env_manager.yaml_env_class.YamlEnv(
            path_to_yaml_env_file=__file__)


def test_yaml_env_from_list_entity_counts(yaml_env_list_object):
    assert len(yaml_env_list_object.data_content) == 2
    assert len(yaml_env_list_object.get_active_data()) == 1


def test_yaml_env_entity_counts(yaml_env_object):
    assert len(yaml_env_object.data_content) == 6
    assert len(yaml_env_object.get_active_data()) == 5


def test_yaml_env_str(yaml_env_list_object):
    assert str(yaml_env_list_object) == """REPOSITORY: repo_name
	SECRET: SECRET=value @ repo_name
"""


def test_yaml_env_contains(yaml_env_object):
    assert (gh_env_manager.secret_variable_entity_class.Secret(
        name="REPO_SECRET", value="something", repo="Antvirf/gh-env-manager") in yaml_env_object) is True
    assert (gh_env_manager.secret_variable_entity_class.Variable(
        name="REPO_ENV_VARIABLE", value="something", repo="Antvirf/gh-env-manager", env="dev") in yaml_env_object) is True
    assert (gh_env_manager.secret_variable_entity_class.Variable(
        name="THIS_IS_NOT_THERE", value="something", repo="Antvirf/gh-env-manager", env="dev") in yaml_env_object) is False


def test_yaml_env_get_repositories(yaml_env_object):
    assert yaml_env_object.get_repositories() == ["Antvirf/gh-env-manager"]


def test_yaml_env_get_environments(yaml_env_object):
    result = yaml_env_object.get_environments(
        repository="Antvirf/gh-env-manager"
    )
    assert len(result) == 2
    assert None in result
    assert "dev" in result


def test_yaml_env_get_entities_from_environments(yaml_env_object):
    entities_from_environment = yaml_env_object.get_entities_from_environment(
        repository="Antvirf/gh-env-manager",
        environment="dev"
    )
    assert entities_from_environment[0] == gh_env_manager.secret_variable_entity_class.Secret(
        name="REPO_ENV_SECRET", value="something", repo="Antvirf/gh-env-manager", env="dev")


def test_yaml_env_append_entities(yaml_env_list_object):
    assert len(yaml_env_list_object.get_active_data()) == 1
    yaml_env_list_object.append_entities(
        input_data={
            "secrets": [
                {"ADDED_ONE_SECRET": "1234"},
                {"ADDED_TWO_SECRET": "5678"}
            ]
        },
        repo="Antvirf/gh-env-manager"
    )
    assert len(yaml_env_list_object.get_active_data()) == 3


def test_yaml_env_get_existing_entities(yaml_env_object):
    assert len(yaml_env_object.get_active_data()) == 5

    entities_list = [
        gh_env_manager.secret_variable_entity_class.Secret(
            name="REPO_SECRET", value="something", repo="Antvirf/gh-env-manager"),
        gh_env_manager.secret_variable_entity_class.Variable(
            name="REPO_ENV_VARIABLE", value="something", repo="Antvirf/gh-env-manager", env="dev"),
    ]
    other_test_env = gh_env_manager.yaml_env_class.YamlEnvFromList(
        entities_list)

    existing_entities = yaml_env_object.get_existing_entities(other_test_env)
    new_yaml_env = gh_env_manager.yaml_env_class.YamlEnvFromList(
        existing_entities)
    assert len(new_yaml_env.get_active_data()) == 5 - len(entities_list)


def test_yaml_env_get_missing_entities(yaml_env_object, yaml_env_list_object):
    assert len(yaml_env_object.get_active_data()) == 5

    entities_list = [
        gh_env_manager.secret_variable_entity_class.Secret(
            name="RANDOM_SECRET", value="something", repo="Antvirf/gh-env-manager"),
        gh_env_manager.secret_variable_entity_class.Variable(
            name="RANDOM_VARIABLE", value="something", repo="Antvirf/gh-env-manager", env="dev"),
    ]
    other_test_env = gh_env_manager.yaml_env_class.YamlEnvFromList(
        entities_list)

    missing_entities = yaml_env_object.get_missing_entities(other_test_env)

    new_yaml_env = gh_env_manager.yaml_env_class.YamlEnvFromList(
        missing_entities)

    # as there is no overlap, the length of the new set is the length of 'entities_list'
    assert len(new_yaml_env.get_active_data()) == len(entities_list)
