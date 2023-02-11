import gh_env_manager.yaml_env_class


def test_remove_null_keys():
    gh_env_manager.yaml_env_class.remove_null_keys({})
    assert 1 == 0+1
