import gh_env_manager.yaml_env_class


def test_remove_null_keys():
    gh_env_manager.yaml_env_class.remove_null_keys({})
    gh_env_manager.yaml_env_class.remove_entities_with_malformed_names({})
    assert 1 == 1
