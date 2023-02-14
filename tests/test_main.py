import gh_env_manager.main


def test_read(path_to_test_yaml):
    gh_env_manager.main.read(path_to_test_yaml)


def test_fetch_output_true(path_to_test_yaml):
    gh_env_manager.main.fetch(
        path_to_file=path_to_test_yaml,
        output=True  # default
    )


def test_fetch_output_false(path_to_test_yaml):
    gh_env_manager.main.fetch(
        path_to_file=path_to_test_yaml,
        output=False
    )
