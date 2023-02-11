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
