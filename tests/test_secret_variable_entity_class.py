import gh_env_manager.secret_variable_entity_class

VALID_SECRET = {
    "name": "MY_VALID_SECRET",
    "value": "MY_SECRET_VALUE",
    "repo": "repo_name",
    "env": "env_name",
    "org": "org_name"
}


def test_entity_name_validity():
    valid_object = gh_env_manager.secret_variable_entity_class.SecretVariableEntity(
        name=VALID_SECRET["name"],
        value=VALID_SECRET["value"],
        repo=VALID_SECRET["repo"]
    )
    assert valid_object.name_valid is True


def test_entity_name_invalid():
    for test_name in [
        "NAME-INVALID",  # contains a dash - common error
        "name",  # is lowercase - common error
        "Name",  # is partially lowercase
        " NAME",  # starts with a space
        "NAME INVALID",  # contains a space
        "!", "@", "#", "$", "%",  # invalid characters
        "^", "&", "*", "(", ")",  "-", "+",  # invalid characters
    ]:
        invalid_object = gh_env_manager.secret_variable_entity_class.SecretVariableEntity(
            name=test_name,
            value=VALID_SECRET["value"],
            repo=VALID_SECRET["repo"]
        )
        assert invalid_object.name_valid is False


def test_secret__repr__():
    secret = gh_env_manager.secret_variable_entity_class.Secret(
        name=VALID_SECRET["name"],
        value=VALID_SECRET["value"],
        repo=VALID_SECRET["repo"]
    )
    assert str(
        secret) == "SECRET: MY_VALID_SECRET=MY_SECRET_VALUE @ repo_name"


def test_variable__repr__():
    variable = gh_env_manager.secret_variable_entity_class.Variable(
        name=VALID_SECRET["name"],
        value=VALID_SECRET["value"],
        repo=VALID_SECRET["repo"]
    )
    assert str(
        variable) == "VARIABLE: MY_VALID_SECRET=MY_SECRET_VALUE @ repo_name"


def test_equality():
    first = gh_env_manager.secret_variable_entity_class.SecretVariableEntity(
        name=VALID_SECRET["name"],
        value=VALID_SECRET["value"],
        repo=VALID_SECRET["repo"]
    )
    second = gh_env_manager.secret_variable_entity_class.SecretVariableEntity(
        name=VALID_SECRET["name"],
        value=VALID_SECRET["value"],
        repo=VALID_SECRET["repo"]
    )
    assert first == second


def test_equality_env_filled():
    first = gh_env_manager.secret_variable_entity_class.SecretVariableEntity(
        name=VALID_SECRET["name"],
        value=VALID_SECRET["value"],
        repo=VALID_SECRET["repo"]
    )
    second = gh_env_manager.secret_variable_entity_class.SecretVariableEntity(
        name=VALID_SECRET["name"],
        value=VALID_SECRET["value"],
        repo=VALID_SECRET["repo"],
        env="environment"
    )
    assert first != second


def test_equality_diff_value():
    first = gh_env_manager.secret_variable_entity_class.SecretVariableEntity(
        name=VALID_SECRET["name"],
        value=VALID_SECRET["value"],
        repo=VALID_SECRET["repo"]
    )
    second = gh_env_manager.secret_variable_entity_class.SecretVariableEntity(
        name=VALID_SECRET["name"],
        value="something else",
        repo=VALID_SECRET["repo"]
    )
    assert first == second


def test_equality_diff_name():
    first = gh_env_manager.secret_variable_entity_class.SecretVariableEntity(
        name=VALID_SECRET["name"],
        value=VALID_SECRET["value"],
        repo=VALID_SECRET["repo"]
    )
    second = gh_env_manager.secret_variable_entity_class.SecretVariableEntity(
        name="something else",
        value=VALID_SECRET["value"],
        repo=VALID_SECRET["repo"]
    )
    assert first != second


def test_equality_different_types():
    first = gh_env_manager.secret_variable_entity_class.Variable(
        name=VALID_SECRET["name"],
        value=VALID_SECRET["value"],
        repo=VALID_SECRET["repo"]
    )
    second = gh_env_manager.secret_variable_entity_class.Secret(
        name=VALID_SECRET["name"],
        value=VALID_SECRET["value"],
        repo=VALID_SECRET["repo"]
    )
    assert first != second
