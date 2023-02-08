import copy
import logging
import os
import re

import yaml

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


def remove_entities_with_malformed_names(input_dict: dict) -> None:
    """Removal of dict entries where the entity name is not valid.
    Adapted from remove_null_keys() above."""

    if isinstance(input_dict, list):
        for entry in input_dict:
            remove_entities_with_malformed_names(entry)
    elif isinstance(input_dict, dict):
        for key, value in input_dict.copy().items():
            if not entity_name_is_valid(value) and key in ["secretName", "variableName"]:
                # we need to pop the name as well value
                input_dict.pop(key)
                input_dict.pop(key.replace("Name", "Value"))
            else:
                remove_entities_with_malformed_names(value)


def remove_specific_keys(input_dict: dict, keys_to_drop: list) -> None:
    """Removal of dict entries where the key is in the given list.
    Adapted from remove_null_keys() above."""

    if isinstance(input_dict, list):
        for entry in input_dict:
            remove_specific_keys(entry, keys_to_drop)
    elif isinstance(input_dict, dict):
        for key, value in input_dict.copy().items():
            if key in keys_to_drop:
                input_dict.pop(key)
            else:
                remove_specific_keys(value, keys_to_drop)


def gen_dict_extract(key, var):
    """Extract all instances of a given key from a dictionary.
    Adapted from https://stackoverflow.com/a/29652561"""
    if hasattr(var, 'items'):
        for k, v in var.items():
            if k == key:
                yield v
            if isinstance(v, dict):
                for result in gen_dict_extract(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in gen_dict_extract(key, d):
                        yield result


def entity_name_is_valid(input_string: str) -> bool:
    """Validates that the name for a secret or variable is valid according to the GitHub spec.
    'Secret names can only contain alphanumeric characters ([a-z], [A-Z], [0-9]) or underscores (_).
    Spaces are not allowed. Must start with a letter ([a-z], [A-Z]) or underscores (_).'
    """
    return bool(re.match('^[A-Z_][A-Z0-9_]*$', str(input_string)))


class YamlEnv:
    def validate(self):
        # validate entity names
        invalid_names_were_found = False
        for entity in ["secretName", "variableName"]:
            # for entity_name in [x for x in gen_dict_extract(entity, self.data)]:
            for entity_name in list(gen_dict_extract(entity, self.data)):
                if not entity_name_is_valid(entity_name):
                    logging.warning(
                        "%s '%s' is invalid and will be ignored.", entity, entity_name)
                    invalid_names_were_found = True
        if invalid_names_were_found:
            logger.warning("Please review the syntax of your environment YAML file. "
                           "As per GitHub spec, secret and variable names can only contain "
                           "alphanumeric characters ([A-Z], [0-9]) or underscores (_), "
                           "and must start with either a letter or an underscore. "
                           "This script enforces UPPER_CASE for all secret and variable names."
                           )

        # remove invalid names
        remove_entities_with_malformed_names(self.data)

        # validate structure - remove any empty keys
        remove_null_keys(self.data)

    def __init__(self, path_to_yaml_env_file: str):
        self.data = {}
        if not os.path.isfile(path_to_yaml_env_file):
            raise FileNotFoundError(path_to_yaml_env_file)

        try:
            # read plain yaml
            with open(path_to_yaml_env_file, 'r') as file_stream:
                self.data = yaml.safe_load(file_stream)

        except yaml.YAMLError as error_msg:
            logging.error("Could not process %s, please check syntax. Error: %s",
                          path_to_yaml_env_file,
                          error_msg
                          )

        self.validate()

    def get_dict(self) -> dict:
        return self.data

    def get_dict_containers_only(self) -> dict:
        keys_to_drop = ["secretName", "secretValue", "secrets",
                        "variableName", "variableValue", "variables"]
        remove_specific_keys(self.data, keys_to_drop)
        return self.data

    # def __repr__(self) -> str:
    #     return str(self.data)

    def __str__(self) -> str:
        data_dict = copy.deepcopy(self.data)
        remove_null_keys(data_dict)

        string = """"""

        # process repos
        for repo_name, repo_data in (data_dict["repositories"] if "repositories" in data_dict else {}).items():
            string += f"REPOSITORY: {repo_name}\n"

            if "secrets" in repo_data:
                for entry in repo_data["secrets"]:
                    string += f"\tSECRET: {entry['secretName']}={entry['secretValue'] if 'secretValue' in entry else '???'}\n"
            if "variables" in repo_data:
                for entry in repo_data["variables"]:
                    string += f"\tVARIABLE: {entry['variableName']}={entry['variableValue']}\n"

            # process envs within repositories
            for env_name, env_data in (repo_data["environments"] if "environments" in repo_data else {}).items():
                if "secrets" in env_data:
                    for entry in env_data["secrets"]:
                        string += f"\tENVIRONMENT {env_name}: SECRET: {entry['secretName']}={entry['secretValue'] if 'secretValue' in entry else '???'}\n"
                if "variables" in env_data:
                    for entry in env_data["variables"]:
                        string += f"\tENVIRONMENT {env_name}: VARIABLE: {entry['variableName']}={entry['variableValue']}\n"

        return string
