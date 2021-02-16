#!/usr/bin/env python3

import os
import subprocess

from pydantic import HttpUrl, SecretStr

from pydantic_azure_secrets import AzureVaultSettings


class GitHubBasic(AzureVaultSettings):
    # Example for GitHub REST API
    url: HttpUrl = "https://api.github.com/user"
    username: str
    token: SecretStr

    class Config:
        env_prefix = "github_"  # defaults to no prefix, i.e. ""
        env_file = ".env"
        secret_dir = "/var/tmp"
        azure_keyvault = "https://pydantic-test-kv.vault.azure.net/"


def use_case_keyvault_only():
    # This example shows how to use library
    # if you want to use azure keyvault only
    github_settings = GitHubBasic()
    print_settings(github_settings, __name__)


def use_case_keyvault_mixed_with_environments():
    # This example shows how to use library
    # if you want to use azure keyvault together with some other settings
    # from environment variables, for example

    os.environ["GITHUB_USERNAME"] = "env_var_username"
    os.environ["GITHUB_TOKEN"] = "atoken"

    github_settings = GitHubBasic()
    print_settings(github_settings, __name__)

    del os.environ["GITHUB_USERNAME"]
    del os.environ["GITHUB_TOKEN"]


def use_case_keyvault_mixed_with_environments_and_dotenv():
    # This example shows how to use library
    # if you want to use azure keyvault together with some other settings
    # from environment variables and dotenv files, for example
    with open(".env", "w") as dotenv:
        dotenv.write("GITHUB_url=https://github-test.com")
        dotenv.write("GITHUB_username=octocat")

    os.environ["GITHUB_TOKEN"] = "randomstring"
    github_settings = GitHubBasic()
    print_settings(github_settings, __name__)

    del os.environ["GITHUB_TOKEN"]
    os.remove(".env")


def print_settings(settings, func_name):
    print(f"Settings after the function: {func_name}")
    print(settings.dict())
    print(f"Show github token: {settings.token.get_secret_value()}")


def login_to_azure():
    subprocess.run("az login", check=True, shell=True)


def main():
    login_to_azure()
    use_case_keyvault_only()
    use_case_keyvault_mixed_with_environments()
    use_case_keyvault_mixed_with_environments_and_dotenv()


if __name__ == "__main__":
    main()
