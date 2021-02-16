#!/usr/bin/env python3

from typing import Any
from unittest import mock

import pydantic
import pytest
from pathlib import Path

from pydantic_azure_secrets import AzureVaultSettings

PWD = Path(__file__).parent.absolute()


class SettingsENVs(AzureVaultSettings):
    """
    Example of settings with environment variables
    """

    field1: str = "default_value1"
    field2: str = "default_value2"

    class Config:
        env_prefix = "test_prefix_"


class SettingsDotEnv(AzureVaultSettings):
    """
    Example of settings with environment variables and dot-env files
    """

    field1: str = "default_value1"
    field2: str = "default_value2"

    class Config:
        env_prefix = "test_prefix_"
        env_file = PWD / "test_data/test.env"


class SettingsDotEnvMissingFields(AzureVaultSettings):
    """
    Example of settings with environment variables and dot-env files,
    but some fields are missing
    """

    test_prefix_field1: str
    field_missing: str

    class Config:
        env_file = PWD / "test_data/test.env"


class SettingsSecretDir(AzureVaultSettings):
    """
    Example of settings with environment variables, dot-env files
    and secret directory
    """

    field1: str = "default_value1"
    field2: str = "default_value2"

    class Config:
        env_prefix = "test_prefix_"
        env_file = "test_not_existed.env"
        secrets_dir = PWD / "test_data/secret_dir"


class SettingsAzureKV(AzureVaultSettings):
    """
    Example of settings with environment variables, dot-env files,
    secret directory and azure keyvault path
    """

    field1: Any = "default_value1"
    field2: Any = "default_value2"

    class Config:
        env_prefix = "test_prefix_"
        env_file = "test_not_existed.env"
        # if secrets_dir doesn't exist then exception is raise by pydantic
        secrets_dir = "/var/tmp"
        azure_keyvault = "https://pydenticlib-test.vault.azure.net/"


class SettingsAzureMissingFields(AzureVaultSettings):
    """
    Example of settings with environment variables, dot-env files,
    secret directory and azure keyvault path,
    but some values are missing in KeyVault
    """

    field: str = "default_value"
    # the same field was defined in SettingsAzureKV
    test_prefix_field1: str
    field_missing: str

    class Config:
        env_file = "test_not_existed.env"
        secrets_dir = "/var/tmp"
        azure_keyvault = "https://pydenticlib-test.vault.azure.net/"


@mock.patch("pydantic_azure_secrets.azure_vault_settings.SecretClient")
@mock.patch("pydantic_azure_secrets.azure_vault_settings.DefaultAzureCredential")
def test_very_simple(secret_client_mock, creds_mock):
    settings = SettingsENVs()
    assert settings.field1 == "default_value1"
    assert settings.field2 == "default_value2"
    assert secret_client_mock.call_count == 0
    assert creds_mock.call_count == 0


@mock.patch("pydantic_azure_secrets.azure_vault_settings.SecretClient")
@mock.patch("pydantic_azure_secrets.azure_vault_settings.DefaultAzureCredential")
def test_very_simple_environ(secret_client_mock, creds_mock, monkeypatch):
    monkeypatch.setenv("test_prefix_field1", "value1_from_environment", prepend=False)
    monkeypatch.setenv("test_prefix_field2", "value2_from_environment", prepend=False)
    settings = SettingsENVs()
    assert settings.field1 == "value1_from_environment"
    assert settings.field2 == "value2_from_environment"
    assert secret_client_mock.call_count == 0
    assert creds_mock.call_count == 0


@mock.patch("pydantic_azure_secrets.azure_vault_settings.SecretClient")
@mock.patch("pydantic_azure_secrets.azure_vault_settings.DefaultAzureCredential")
def test_very_simple_dotenv(secret_client_mock, creds_mock, monkeypatch):
    settings = SettingsDotEnv()
    assert settings.field1 == "value1_from_test.env-file"
    assert settings.field2 == "value2_from_test.env-file"

    monkeypatch.setenv("test_prefix_field1", "value1_from_environment", prepend=False)
    monkeypatch.setenv("test_prefix_field2", "value2_from_environment", prepend=False)
    settings = SettingsDotEnv()
    assert settings.field1 == "value1_from_environment"
    assert settings.field2 == "value2_from_environment"

    assert secret_client_mock.call_count == 0
    assert creds_mock.call_count == 0


@mock.patch("pydantic_azure_secrets.azure_vault_settings.SecretClient")
@mock.patch("pydantic_azure_secrets.azure_vault_settings.DefaultAzureCredential")
def test_dotenv_file_init(secret_client_mock, creds_mock, monkeypatch):
    settings = SettingsDotEnv()
    assert settings.field1 == "value1_from_test.env-file"
    assert settings.field2 == "value2_from_test.env-file"

    settings = SettingsDotEnv(_env_file=PWD / "test_data/.dotenvfile")
    assert settings.field1 == "value1_from_.dotenvfile"
    assert settings.field2 == "value2_from_.dotenvfile"

    settings = SettingsDotEnv(
        _env_file=PWD / "test_data/.dotenvfile", _env_file_encoding="utf-8"
    )
    assert settings.field1 == "value1_from_.dotenvfile"
    assert settings.field2 == "value2_from_.dotenvfile"

    monkeypatch.setenv("test_prefix_field1", "value1_from_environment", prepend=False)
    monkeypatch.setenv("test_PREFIX_field2", "value2_from_environment", prepend=False)
    settings = SettingsDotEnv()
    assert settings.field1 == "value1_from_environment"
    assert settings.field2 == "value2_from_environment"

    assert secret_client_mock.call_count == 0
    assert creds_mock.call_count == 0


@mock.patch("pydantic_azure_secrets.azure_vault_settings.SecretClient")
@mock.patch("pydantic_azure_secrets.azure_vault_settings.DefaultAzureCredential")
def test_secret_dir(secret_client_mock, creds_mock, monkeypatch):
    settings = SettingsSecretDir()

    assert settings.field1 == "value1_from_file_inside_secret_directory"
    assert settings.field2 == "value2_from_file_inside_secret_directory"

    settings = SettingsSecretDir(_env_file=PWD / "test_data/.dotenvfile")
    assert settings.field1 == "value1_from_.dotenvfile"
    assert settings.field2 == "value2_from_.dotenvfile"

    settings = SettingsSecretDir(
        _env_file=PWD / "test_data/.dotenvfile", _env_file_encoding="utf-8"
    )
    assert settings.field1 == "value1_from_.dotenvfile"
    assert settings.field2 == "value2_from_.dotenvfile"

    monkeypatch.setenv("test_prefix_field1", "value1_from_environment", prepend=False)
    monkeypatch.setenv("test_PREFIX_field2", "value2_from_environment", prepend=False)
    settings = SettingsSecretDir()
    assert settings.field1 == "value1_from_environment"
    assert settings.field2 == "value2_from_environment"

    assert secret_client_mock.call_count == 0
    assert creds_mock.call_count == 0


@mock.patch("pydantic_azure_secrets.azure_vault_settings.SecretClient")
@mock.patch("pydantic_azure_secrets.azure_vault_settings.DefaultAzureCredential")
def test_secret_dir_init(secret_client_mock, creds_mock, monkeypatch):
    settings = SettingsSecretDir()
    show_the_dir = PWD / "test_data/.secret_dir_init"

    assert settings.field1 == "value1_from_file_inside_secret_directory"
    assert settings.field2 == "value2_from_file_inside_secret_directory"

    settings = SettingsSecretDir(_env_file=PWD / "test_data/.dotenvfile")
    assert settings.field1 == "value1_from_.dotenvfile"
    assert settings.field2 == "value2_from_.dotenvfile"

    settings = SettingsSecretDir(
        _env_file=PWD / "test_data/.dotenvfile", _env_file_encoding="utf-8"
    )
    assert settings.field1 == "value1_from_.dotenvfile"
    assert settings.field2 == "value2_from_.dotenvfile"

    settings = SettingsSecretDir(_secrets_dir=PWD / "test_data/.secret_dir_init")
    show_the_dir = PWD / "test_data/.secret_dir_init"
    assert show_the_dir is not None
    assert settings.field1 == "value1_from_.secret_dir_init"
    assert settings.field2 == "value2_from_.secret_dir_init"

    monkeypatch.setenv("test_prefix_field1", "value1_from_environment", prepend=False)
    monkeypatch.setenv("test_PREFIX_field2", "value2_from_environment", prepend=False)
    settings = SettingsSecretDir()
    assert settings.field1 == "value1_from_environment"
    assert settings.field2 == "value2_from_environment"

    assert secret_client_mock.call_count == 0
    assert creds_mock.call_count == 0


@mock.patch("pydantic_azure_secrets.azure_vault_settings.SecretClient")
@mock.patch("pydantic_azure_secrets.azure_vault_settings.DefaultAzureCredential")
def test_secret_dir_with_missing_fields(secret_client_mock, creds_mock, monkeypatch):
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        settings = SettingsDotEnvMissingFields()

    monkeypatch.setenv("FIELD_MISSING", "value_from_environment")
    settings = SettingsDotEnvMissingFields()
    assert settings.field_missing == "value_from_environment"


@mock.patch("pydantic_azure_secrets.azure_vault_settings.SecretClient")
@mock.patch("pydantic_azure_secrets.azure_vault_settings.DefaultAzureCredential")
def test_mocked_keyvault(secret_client_mock, creds_mock, monkeypatch):
    # This test check a mocked integration with Azure keyvault
    settings = SettingsAzureKV()
    assert secret_client_mock.call_count == 2
    assert creds_mock.call_count == 2

    settings = SettingsAzureKV(_env_file=PWD / "test_data/.dotenvfile")
    assert secret_client_mock.call_count == 4
    assert creds_mock.call_count == 4

    settings = SettingsAzureKV(
        _env_file=PWD / "test_data/.dotenvfile", _env_file_encoding="utf-8"
    )
    assert settings.field1 == "value1_from_.dotenvfile"
    assert settings.field2 == "value2_from_.dotenvfile"
    assert secret_client_mock.call_count == 6
    assert creds_mock.call_count == 6

    settings = SettingsAzureKV(
        _env_file=PWD / "test_data/.dotenvfile",
        _env_file_encoding="utf-8",
        _secrets_dir=PWD / "test_data/.secret_dir_init",
        _azure_keyvault="https://pydantictestinit.vault.azure.net/",
    )
    assert settings.field1 == "value1_from_.dotenvfile"
    assert settings.field2 == "value2_from_.dotenvfile"
    assert secret_client_mock.call_count == 8
    assert creds_mock.call_count == 8

    settings = SettingsAzureKV(_secrets_dir=PWD / "test_data/.secret_dir_init")
    assert settings.field1 == "value1_from_.secret_dir_init"
    assert settings.field2 == "value2_from_.secret_dir_init"
    assert secret_client_mock.call_count == 10
    assert creds_mock.call_count == 10

    settings = SettingsAzureKV(
        _secrets_dir=PWD / "test_data/.secret_dir_init",
        _azure_keyvault="https://pydantictestinit.vault.azure.net/",
    )
    assert settings.field1 == "value1_from_.secret_dir_init"
    assert settings.field2 == "value2_from_.secret_dir_init"
    assert secret_client_mock.call_count == 12
    assert creds_mock.call_count == 12

    settings = SettingsAzureKV(
        _azure_keyvault="https://pydantictestinit.vault.azure.net/",
    )
    assert secret_client_mock.call_count == 14
    assert creds_mock.call_count == 14

    monkeypatch.setenv("test_prefix_field1", "value1_from_environment", prepend=False)
    monkeypatch.setenv("test_PREFIX_field2", "value2_from_environment", prepend=False)
    settings = SettingsAzureKV()
    assert settings.field1 == "value1_from_environment"
    assert settings.field2 == "value2_from_environment"
    assert secret_client_mock.call_count == 16
    assert creds_mock.call_count == 16


@pytest.mark.integration
def test_keyvault(monkeypatch):
    # This test check a real integration with Azure keyvault
    settings = SettingsAzureKV()
    assert settings.field1 == "value1_inside_default_azureKV"
    assert settings.field2 == "value2_inside_default_azureKV"

    settings = SettingsAzureKV(_env_file=PWD / "test_data/.dotenvfile")
    assert settings.field1 == "value1_from_.dotenvfile"
    assert settings.field2 == "value2_from_.dotenvfile"

    settings = SettingsAzureKV(
        _env_file=PWD / "test_data/.dotenvfile", _env_file_encoding="utf-8"
    )
    assert settings.field1 == "value1_from_.dotenvfile"
    assert settings.field2 == "value2_from_.dotenvfile"

    settings = SettingsAzureKV(
        _env_file=PWD / "test_data/.dotenvfile",
        _env_file_encoding="utf-8",
        _secrets_dir=PWD / "test_data/.secret_dir_init",
        _azure_keyvault="https://pydantictestinit.vault.azure.net/",
    )
    assert settings.field1 == "value1_from_.dotenvfile"
    assert settings.field2 == "value2_from_.dotenvfile"

    settings = SettingsAzureKV(_secrets_dir=PWD / "test_data/.secret_dir_init")
    assert settings.field1 == "value1_from_.secret_dir_init"
    assert settings.field2 == "value2_from_.secret_dir_init"

    settings = SettingsAzureKV(
        _secrets_dir=PWD / "test_data/.secret_dir_init",
        _azure_keyvault="https://pydantictestinit.vault.azure.net/",
    )
    assert settings.field1 == "value1_from_.secret_dir_init"
    assert settings.field2 == "value2_from_.secret_dir_init"

    settings = SettingsAzureKV(
        _azure_keyvault="https://pydantictestinit.vault.azure.net/",
    )
    assert settings.field1 == "value1_inside_azureKV_from_init"
    assert settings.field2 == "value2_inside_azureKV_from_init"

    monkeypatch.setenv("test_prefix_field1", "value1_from_environment", prepend=False)
    monkeypatch.setenv("test_PREFIX_field2", "value2_from_environment", prepend=False)
    settings = SettingsAzureKV()
    assert settings.field1 == "value1_from_environment"
    assert settings.field2 == "value2_from_environment"


@pytest.mark.integration
def test_keyvault_if_some_fields_are_empty(monkeypatch):
    # This test check a real integration with Azure keyvault
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        settings = SettingsAzureMissingFields()

    monkeypatch.setenv("FIELD_MISSING", "missing_value_from_environments")
    settings = SettingsAzureMissingFields()
    assert settings.field == "default_value"
    assert settings.test_prefix_field1 == "value1_inside_default_azureKV"
    assert settings.field_missing == "missing_value_from_environments"
