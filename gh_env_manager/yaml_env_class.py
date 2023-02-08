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


def remove_entities_with_malformed_names(input_dict: dict):
    """Remove of dict entries where the entity name is not valid.
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

    def get_dict(self) -> dict:
        return self.data
