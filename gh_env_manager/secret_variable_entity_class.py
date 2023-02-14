# pylint: disable=too-few-public-methods
import re


class SecretVariableEntity:
    def __init__(self, name, value, repo, env=None, org=None) -> None:
        self.name = name
        self.value = value
        self.parent_repo = repo
        self.parent_env = env
        self.parent_org = org

        self.name_valid = bool(re.match('^[A-Z_][A-Z0-9_]*$', str(name)))
        self.is_active = self.name_valid

    def __eq__(self, other):
        """Overrides the default implementation"""
        if any(
            [
                not isinstance(self, type(other)),
                self.name != other.name,
                # self.value != other.value, # values are NOT compared
                self.parent_env != other.parent_env,
                self.parent_org != other.parent_org,
                self.parent_repo != other.parent_repo,
            ]
        ):
            return False
        return True


class Secret(SecretVariableEntity):
    def __repr__(self) -> str:
        return str(
            f"SECRET: {self.name}={self.value} @ {self.parent_repo}"
            + (f" ({self.parent_env})" if self.parent_env else "")
        )


class Variable(SecretVariableEntity):
    def __repr__(self) -> str:
        return str(f"VARIABLE: {self.name}={self.value} @ {self.parent_repo}"
                   + (f" ({self.parent_env})" if self.parent_env else "")
                   )
