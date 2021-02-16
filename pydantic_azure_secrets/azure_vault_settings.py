import logging
import logging.config
from pathlib import Path
from typing import Any, Dict, Optional, Union

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from pydantic import BaseSettings
from pydantic.utils import deep_update  # pylint: disable=no-name-in-module

logger = logging.getLogger(__name__)


class AzureVaultSettings(BaseSettings):
    """
    The behaviour of this class is exactly like pydantic.BaseSettings, except
    the Field value priority:
    https://pydantic-docs.helpmanual.io/usage/settings/#field-value-priority
    The latest step is to check azure key vault, e.g.:

    In the case where a value is specified for the same Settings field in
    multiple ways, the selected value is determined as follows
    (in descending order of priority):
        1. Arguments passed to the Settings class initialiser.
        2. Environment variables, e.g. my_prefix_special_function
    as described above.
        3. Variables loaded from a dotenv (.env) file.
        4. Variables loaded from the secrets directory.
        5. Variables loaded from the keyvault.
        6. The default field values for the Settings model.

    The implementation details are the same as in this version of pydantic:
    https://github.com/samuelcolvin/pydantic/blob/00a128a3609dac82dfe0cdb4200bbf2011aa5f83/pydantic/env_settings.py
    """

    def __init__(  # pylint: disable=no-self-argument
        __pydantic_self__,
        _env_file: Union[Path, str, None] = str(object()),
        _env_file_encoding: Optional[str] = None,
        _secrets_dir: Union[Path, str, None] = None,
        _azure_keyvault: Union[str, None] = None,
        **values: Any,
    ) -> None:
        # Uses something other than `self`
        # the first arg to allow "self" as a settable attribute
        super().__init__(
            **__pydantic_self__._build_values(
                values,
                _env_file=_env_file,
                _env_file_encoding=_env_file_encoding,
                _secrets_dir=_secrets_dir,
                _azure_keyvault=_azure_keyvault,
            )
        )

    def _build_values(
        self,
        init_kwargs: Dict[str, Any],
        _env_file: Union[Path, str, None] = None,
        _env_file_encoding: Optional[str] = None,
        _secrets_dir: Union[Path, str, None] = None,
        _azure_keyvault: Union[str, None] = None,
    ) -> Dict[str, Any]:

        azure_keyvault = _azure_keyvault or self.__config__.azure_keyvault
        secret_client = self.__config__.get_azure_client(azure_keyvault)

        return deep_update(
            self._build_keyvault(secret_client),
            self._build_secrets_files(_secrets_dir),
            self._build_environ(_env_file, _env_file_encoding),
            init_kwargs,
        )

    def _build_keyvault(
        self, secret_client: Optional[SecretClient] = None
    ) -> Dict[str, Optional[str]]:
        secrets: Dict[str, Optional[str]] = {}

        if secret_client is None:
            return {}

        # Get secrets
        for field in self.__fields__.values():
            for env_name in field.field_info.extra["env_names"]:
                az_field_name = env_name.replace("_", "-")
                try:
                    secret = secret_client.get_secret(az_field_name)
                    secrets[field.name] = secret.value
                except ResourceNotFoundError:
                    logger.warning(
                        "%s was not found in: %s",
                        field.name,
                        self.__config__.azure_keyvault,
                    )

        return secrets

    class Config(BaseSettings.Config):
        azure_keyvault = None

        @classmethod
        def get_azure_client(cls, azure_keyvault: Optional[str]) -> SecretClient:
            secret_client = None
            if azure_keyvault:
                credential = DefaultAzureCredential()
                secret_client = SecretClient(
                    vault_url=azure_keyvault, credential=credential
                )
            return secret_client

    __config__: Config
