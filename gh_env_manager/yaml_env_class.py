import logging
import os
from typing import Optional

import yaml

from .secret_variable_entity_class import (Secret, SecretVariableEntity,
                                           Variable)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def remove_null_keys(input_dict: dict):
    """Recursive removal of dict entries where value is None.
    Adapted from https://stackoverflow.com/a/67893341"""

    if isinstance(input_dict, list):
        for entry in input_dict:
            remove_null_keys(entry)
    elif isinstance(input_dict, dict):
        for key, value in input_dict.copy().items():
            if value is None or value in [[], {}, [{}]]:
                input_dict.pop(key)
            else:
                remove_null_keys(value)


class YamlEnv:
    def validate(self, output=True):
        # validate entity names
        if output:
            for entity in self.data_content:
                if not entity.name_valid:
                    logging.warning(
                        "%s has an invalid name and will be ignored.", entity)

            if any(not x.name_valid for x in self.data_content):
                logger.warning("Please review the syntax of your environment YAML file. "
                               "As per GitHub spec, secret and variable names can only contain "
                               "alphanumeric characters ([A-Z], [0-9]) or underscores (_), "
                               "and must start with either a letter or an underscore. "
                               "This script enforces UPPER_CASE for all secret and variable names."
                               )

    def __init__(self, path_to_yaml_env_file: Optional[str] = None, output: bool = True):
        self.data = {}
        self.key = ""
        self.data_content = []

        if path_to_yaml_env_file is None:
            return

        if not os.path.isfile(path_to_yaml_env_file):
            raise FileNotFoundError(
                f"File '{path_to_yaml_env_file}' not found, aborting..")

        try:
            with open(path_to_yaml_env_file, 'r') as file_stream:
                self.data = yaml.safe_load(file_stream)
        except yaml.YAMLError as error_msg:
            raise yaml.YAMLError(
                f"Could not process '{path_to_yaml_env_file}', please check syntax. Error: {error_msg}")

        self.key = self.data.get('GH_SECRET_SYNC_KEY', None)
        remove_null_keys(self.data)

        # load data structure
        for repo_name, repo_data in (self.data["repositories"] if "repositories" in self.data else {}).items():
            self.append_entities(
                repo_data,
                repo=repo_name)
            for env_name in repo_data.get("environments", []):
                self.append_entities(
                    repo_data["environments"][env_name],
                    repo=repo_name,
                    env=env_name)

        self.validate(output)

    def __str__(self) -> str:
        string = """"""

        # process repos
        all_repositories = self.get_repositories()

        for repo_name in all_repositories:
            string += f"REPOSITORY: {repo_name}\n"
            for env_name in self.get_environments(repo_name):
                string += "\n".join([(f"\t{entity}")
                                     for entity in self.get_entities_from_environment(repo_name, env_name)]) + "\n"
        return string

    def __contains__(self, item: SecretVariableEntity):
        for entity in self.data_content:
            if entity == item:
                return True
        return False

    def get_active_data(self) -> list:
        return [x for x in self.data_content if x.is_active]

    def get_repositories(self) -> list:
        return list({x.parent_repo for x in self.get_active_data()})

    def get_environments(self, repository) -> list:
        # also returns a single None here, for when you have stuff in 'no' environment
        return list({x.parent_env for x in self.get_active_data() if x.parent_repo == repository})

    def get_entities_from_environment(self, repository, environment) -> list:
        return [x for x in self.get_active_data() if (x.parent_repo == repository and x.parent_env == environment)]

    def append_entities(self,
                        input_data: dict,
                        repo: str,
                        env: Optional[str] = None,
                        org: Optional[str] = None
                        ):
        found_entities = []
        for entity in input_data.get("secrets", []):
            found_entities.append(
                Secret(name=next(iter(entity.keys())),
                       value=next(iter(entity.values())),
                       repo=repo,
                       env=env,
                       org=org
                       ))
        for entity in input_data.get("variables", []):
            found_entities.append(
                Variable(name=next(iter(entity.keys())),
                         value=next(iter(entity.values())),
                         repo=repo,
                         env=env,
                         org=org
                         ))
        self.data_content += found_entities

    def get_existing_entities(self, other_env) -> list:
        """'Left minus join' style operation. Take the entities available in self, and check if
        any of them exist in the 'other'. If they do, delete them from the self.
        Results in a set containing entities ONLY set in the self."""

        indices_overlapping_self_entity = []
        for i, self_entity in enumerate(self.get_active_data()):
            if self_entity in other_env:
                indices_overlapping_self_entity.append(i)

        non_overlapping_self_entities = []
        for i, self_entity in enumerate(self.get_active_data()):
            if i not in indices_overlapping_self_entity:
                non_overlapping_self_entities.append(
                    self_entity
                )

        return non_overlapping_self_entities

    def get_missing_entities(self, other_env) -> list:
        """'right minus join' style operation. Take the entities available in other, and check if
        any of them exist in the 'self'. If they do, delete them from the other.
        Results in a set containing entities ONLY set in the other."""

        indices_entries_only_in_other = []
        for i, other_entity in enumerate(other_env.get_active_data()):
            if other_entity not in self:
                indices_entries_only_in_other.append(i)

        entities_only_in_other = []
        for i, other_entity in enumerate(other_env.get_active_data()):
            if i in indices_entries_only_in_other:
                entities_only_in_other.append(
                    other_entity
                )

        return entities_only_in_other


class YamlEnvFromList(YamlEnv):
    def __init__(self, data_list: list, output: bool = True):
        self.data = {}
        self.key = ""
        self.data_content = []

        self.data_content = list(data_list)

        self.validate(output)
