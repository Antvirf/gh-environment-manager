import logging
from base64 import b64encode

import requests
from nacl import encoding, public

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def encrypt_secret(public_key_input: str, secret_value: str) -> str:
    """Encrypt a Unicode string using the public key. This code is directly from the GitHub docs"""
    public_key = public.PublicKey(
        public_key_input.encode("utf-8"), encoding.Base64Encoder())
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

        # secrets
        self.get_secret_endpoint = ""
        self.list_secret_endpoint = ""
        self.create_secret_endpoint = ""

        # variables
        self.get_variable_endpoint = ""
        self.list_variable_endpoint = ""
        self.create_variable_endpoint = ""

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

        if method == "get":
            _response = requests.get(
                url=url_for_request,
                headers=headers_for_request,
                data=payload
            )
        elif method == "put":
            _response = requests.put(
                url=url_for_request,
                headers=headers_for_request,
                json=payload
            )
        elif method == "post":
            _response = requests.post(
                url=url_for_request,
                headers=headers_for_request,
                json=payload
            )
        elif method == "delete":
            _response = requests.delete(
                url=url_for_request,
                headers=headers_for_request,
                json=payload
            )
        elif method == "patch":
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

    def _create_secret(self, secret_name: str, secret_value: str):
        """Creates a given secret"""

        _, status_code = self._make_request(
            endpoint=f"{self.create_secret_endpoint}/{secret_name}",
            payload={
                "encrypted_value": encrypt_secret(self.public_key, str(secret_value)),
                "key_id": self.public_key_id
            },
            method="put"
        )
        if status_code == 201:
            logging.info("Secret %s created.", secret_name)
        elif status_code == 204:
            logging.info("Secret %s updated.", secret_name)
        else:
            logging.info("Secret %s: status %d", secret_name, status_code)

    def get_secret_info(self, secret_name: str):
        """Get info about a secret"""
        _response_data, _ = self._make_request(
            endpoint=f"{self.get_secret_endpoint}/{secret_name}"
        )
        return _response_data

    def list_secrets(self):
        """Get full list of existing entity secrets"""
        _response_data, _ = self._make_request(
            endpoint=self.list_secret_endpoint
        )
        list_of_secrets = []
        for secret in _response_data["secrets"]:
            list_of_secrets.append({
                secret["name"]: None
            })
        return list_of_secrets

    def _create_variable(self, variable_name: str, variable_value: str):
        """Creates a given variable, or patches it in case of a conflict."""

        _, status_code = self._make_request(
            endpoint=f"{self.create_variable_endpoint}",
            payload={
                "name": variable_name,
                "value": str(variable_value)
            },
            method="post"
        )
        if status_code == 201:
            logging.info("Variable %s created.", variable_name)
        elif status_code == 409:
            self._patch_variable(variable_name=variable_name,
                                 variable_value=variable_value)
        else:
            logging.info("Variable %s: status %d", variable_name, status_code)

    def _patch_variable(self, variable_name: str, variable_value: str):
        """Patches a given variable"""

        _, status_code = self._make_request(
            endpoint=f"{self.create_variable_endpoint}/{variable_name}",
            payload={
                "name": variable_name,
                "value": str(variable_value)
            },
            method="patch"
        )
        if status_code == 204:
            logging.info("Variable %s updated.", variable_name)
        else:
            logging.info("Variable %s: status %d", variable_name, status_code)

    def get_variable_info(self, variable_name: str):
        """Get info about a variable"""
        _response_data, _ = self._make_request(
            endpoint=f"{self.get_variable_endpoint}/{variable_name}"
        )
        return _response_data

    def list_variables(self):
        """Get full list of existing entity variables"""
        _response_data, _ = self._make_request(
            endpoint=self.list_variable_endpoint
        )
        list_of_variables = []
        for variable in _response_data["variables"]:
            list_of_variables.append({
                variable["name"]: variable["value"]
            })
        return list_of_variables

    def create_secrets(self, entity_name: str, secrets_list: list):
        if not secrets_list:
            return

        logging.info("Syncing %s '%s': Secrets to create: %s",
                     self.current_parent_type,
                     entity_name,
                     str([
                         x.name for x in secrets_list
                     ]))

        for secret in secrets_list:
            self._create_secret(
                secret_name=secret.name,
                secret_value=secret.value
            )

    def create_variables(self, entity_name: str, variables_list: list):
        if not variables_list:
            return

        logging.info("Syncing %s '%s': Variables to create: %s",
                     self.current_parent_type,
                     entity_name,
                     str([
                         x.name for x in variables_list
                     ]))
        for variable in variables_list:
            self._create_variable(
                variable_name=variable.name,
                variable_value=variable.value
            )
