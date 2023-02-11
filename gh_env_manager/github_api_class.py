import logging
from base64 import b64encode

import requests
from nacl import encoding, public

from .secret_variable_entity_class import Secret, Variable

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def encrypt_secret(public_key_input: str, secret_value: str) -> str:  # pragma: no cover
    """Encrypt a Unicode string using the public key. This code is directly from the GitHub docs"""
    public_key = public.PublicKey(
        public_key_input.encode("utf-8"), encoding.Base64Encoder())  # type: ignore
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")


class GitHubApi:
    """Class providing easy access to GitHub REST API"""

    def __init__(self, key: str, api_url: str = "https://api.github.com") -> None:
        self.key = key
        self.api_url = api_url
        self.current_parent_type = "Undefined for base class"
        self.repository_id = ""

        # public key
        self.get_public_key_endpoint = ""
        self.public_key = ""
        self.public_key_id = ""

        self.secrets_endpoint = ""
        self.variables_endpoint = ""

    def _make_request(self,
                      endpoint: str,
                      extra_headers: dict = {},
                      payload: dict = {},
                      method: str = "get"):
        """Internal function to make a request with the proper URL, headers, and payload."""
        url_for_request = "/".join([self.api_url, endpoint])
        headers_for_request = {**{
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.key}",
            "X-GitHub-Api-Version": "2022-11-28"
        }, **extra_headers}

        if method == "get":  # pragma: no cover - basic requests method
            _response = requests.get(
                url=url_for_request,
                headers=headers_for_request,
                data=payload
            )
        elif method == "put":  # pragma: no cover - basic requests method
            _response = requests.put(
                url=url_for_request,
                headers=headers_for_request,
                json=payload
            )
        elif method == "post":  # pragma: no cover - basic requests method
            _response = requests.post(
                url=url_for_request,
                headers=headers_for_request,
                json=payload
            )
        elif method == "delete":  # pragma: no cover - basic requests method
            _response = requests.delete(
                url=url_for_request,
                headers=headers_for_request,
                json=payload
            )
        elif method == "patch":  # pragma: no cover - basic requests method
            _response = requests.patch(
                url=url_for_request,
                headers=headers_for_request,
                json=payload
            )
        else:
            raise NotImplementedError(
                "Given method '%s' has not been implemented." % method)

        logging.debug(str(_response.content))
        if _response.status_code != 409:  # deal with 409 conflict separately
            _response.raise_for_status()

        try:
            return_json = _response.json()
        except requests.exceptions.JSONDecodeError:
            return_json = {}

        return return_json, _response.status_code

    # repo-level operations
    def get_public_key(self):
        """Fetches a public key used to encrypt secrets before creation."""
        # use _make_request to get the public key
        _response_data, _ = self._make_request(
            endpoint=self.get_public_key_endpoint
        )

        self.public_key = _response_data["key"]
        self.public_key_id = _response_data["key_id"]

    def get_repository_id(self, repository: str):
        """Fetches the unique ID of a given repository."""
        # use _make_request to get the public key
        _response_data, _ = self._make_request(
            endpoint=f"repos/{repository}"
        )

        self.repository_id = _response_data["id"]

    # secrets
    def _create_secret(self, secret_name: str, secret_value: str):
        """Creates a given secret"""

        _, status_code = self._make_request(
            endpoint=f"{self.secrets_endpoint}/{secret_name}",
            payload={
                "encrypted_value": encrypt_secret(self.public_key, str(secret_value)),
                "key_id": self.public_key_id
            },
            method="put"
        )
        if status_code == 201:
            logging.debug("Secret %s created.", secret_name)
        elif status_code == 204:
            logging.debug("Secret %s updated.", secret_name)
        else:
            logging.error("Secret %s: status %d", secret_name, status_code)

    def get_secret_info(self, secret_name: str):
        """Get info about a secret"""
        _response_data, _ = self._make_request(
            endpoint=f"{self.secrets_endpoint}/{secret_name}"
        )
        return _response_data

    def list_secrets(self):
        """Get full list of existing entity secrets"""
        _response_data, _ = self._make_request(
            endpoint=self.secrets_endpoint
        )
        list_of_secrets = []
        for secret in _response_data["secrets"]:
            list_of_secrets.append({
                secret["name"]: None
            })
        return list_of_secrets

    def _delete_secret(self, secret_name: str):
        """Delete a secret"""
        _response_data, _ = self._make_request(
            endpoint=f"{self.secrets_endpoint}/{secret_name}",
            method="delete"
        )
        return _response_data

    # variables
    def _create_variable(self, variable_name: str, variable_value: str):
        """Creates a given variable, or patches it in case of a conflict."""

        _, status_code = self._make_request(
            endpoint=f"{self.variables_endpoint}",
            payload={
                "name": variable_name,
                "value": str(variable_value)
            },
            method="post"
        )
        if status_code == 201:
            logging.debug("Variable %s created.", variable_name)
        elif status_code == 409:
            self._patch_variable(variable_name=variable_name,
                                 variable_value=variable_value)
        else:
            logging.error("Variable %s: status %d", variable_name, status_code)

    def _patch_variable(self, variable_name: str, variable_value: str):
        """Patches a given variable"""

        _, status_code = self._make_request(
            endpoint=f"{self.variables_endpoint}/{variable_name}",
            payload={
                "name": variable_name,
                "value": str(variable_value)
            },
            method="patch"
        )
        if status_code == 204:
            logging.debug("Variable %s updated.", variable_name)
        else:
            logging.error("Variable %s: status %d", variable_name, status_code)

    def get_variable_info(self, variable_name: str):
        """Get info about a variable"""
        _response_data, _ = self._make_request(
            endpoint=f"{self.variables_endpoint}/{variable_name}"
        )
        return _response_data

    def _delete_variable(self, variable_name: str):
        """Delete a variable"""
        _response_data, _ = self._make_request(
            endpoint=f"{self.variables_endpoint}/{variable_name}",
            method="delete"
        )
        return _response_data

    def list_variables(self):
        """Get full list of existing entity variables"""
        _response_data, _ = self._make_request(
            endpoint=self.variables_endpoint
        )
        list_of_variables = []
        for variable in _response_data["variables"]:
            list_of_variables.append({
                variable["name"]: variable["value"]
            })
        return list_of_variables

    # batch operation
    def create_entities(self, entities_list: list):
        if not entities_list:
            return

        logging.info("Syncing %s entities to PUSH: %s",
                     self.current_parent_type,
                     str([
                         x.name for x in entities_list
                     ]))

        for entity in entities_list:
            if isinstance(entity, Secret):
                self._create_secret(
                    secret_name=entity.name,
                    secret_value=entity.value
                )
            elif isinstance(entity, Variable):
                self._create_variable(
                    variable_name=entity.name,
                    variable_value=entity.value
                )

    def delete_entities(self, entities_list: list):
        if not entities_list:
            return

        logging.info("Syncing %s entities to DELETE: %s",
                     self.current_parent_type,
                     str([
                         x.name for x in entities_list
                     ]))

        for entity in entities_list:
            if isinstance(entity, Secret):
                self._delete_secret(
                    secret_name=entity.name
                )
            elif isinstance(entity, Variable):
                self._delete_variable(
                    variable_name=entity.name
                )
