import gh_env_manager.secret_variable_entity_class

from .conftest import TARGET_TEST_REPOSITORY


def test_gh_api_full_flow_repo(
        gh_repo_api,
        repo_additional_secrets_to_create,
        repo_additional_variables_to_create,
        repo_additional_secrets_to_create_dicts,
        repo_additional_variables_to_create_dicts):
    secrets_in_test_repo_at_the_beginning_dicts = [
        {'PAT_SECRET': None},
        {'PYPI_TOKEN': None},
    ]

    # step 1: check starting stage
    assert gh_repo_api.list_secrets() == secrets_in_test_repo_at_the_beginning_dicts
    assert gh_repo_api.list_variables() == []

    try:
        # step 2: entity creation - batch and individual operations
        gh_repo_api.create_entities([
            repo_additional_secrets_to_create[0], repo_additional_variables_to_create[0]
        ])
        # individual creation - secret
        gh_repo_api._create_secret(
            secret_name=repo_additional_secrets_to_create[1].name,
            secret_value=repo_additional_secrets_to_create[1].value
        )
        # individual creation - variable
        gh_repo_api._create_variable(
            variable_name=repo_additional_variables_to_create[1].name,
            variable_value=repo_additional_variables_to_create[1].value
        )

        # step 3: fetching entries in batch
        # assert gh_repo_api.list_secrets() == secrets_in_test_repo_at_the_beginning_dicts + \
        #     repo_additional_secrets_to_create_dicts
        # assert gh_repo_api.list_variables() == repo_additional_variables_to_create_dicts

        assert [i for i in gh_repo_api.list_secrets() if i not in secrets_in_test_repo_at_the_beginning_dicts +
                repo_additional_secrets_to_create_dicts] == []
        assert [i for i in gh_repo_api.list_variables(
        ) if i not in repo_additional_variables_to_create_dicts] == []

        # step 4: updating entries
        gh_repo_api._create_secret(
            secret_name=repo_additional_secrets_to_create[1].name,
            secret_value="new value for second secret"
        )
        gh_repo_api._patch_variable(
            variable_name=repo_additional_variables_to_create[1].name,
            variable_value="new value for second variable"
        )

        # step 5: fetch updated entries
        # get_secret() - just ensuring this works, but we cannot test its value
        gh_repo_api.get_secret_info(repo_additional_secrets_to_create[1].name)
        assert gh_repo_api.get_variable_info(
            variable_name=repo_additional_variables_to_create[1].name
        )["value"] == "new value for second variable"

    finally:
        # step 6: delete entries - batch and individual operations
        gh_repo_api.delete_entities([
            repo_additional_secrets_to_create[0], repo_additional_variables_to_create[0]
        ])
        gh_repo_api._delete_secret(
            secret_name=repo_additional_secrets_to_create[1].name
        )
        gh_repo_api._delete_variable(
            variable_name=repo_additional_variables_to_create[1].name
        )

    # step 7: ensure entities were deleted by asserting start state == end state
    assert gh_repo_api.list_secrets() == secrets_in_test_repo_at_the_beginning_dicts
    assert gh_repo_api.list_variables() == []
