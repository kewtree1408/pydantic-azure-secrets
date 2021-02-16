# pydantic-azure-secrets
A class to use pydantic settings together with [Azure KeyVault](https://docs.microsoft.com/en-us/azure/key-vault/)

![tests](https://github.com/kewtree1408/pydantic-azure-secrets/workflows/Linters%20and%20Tests/badge.svg?branch=main)

The [behaviour](https://pydantic-docs.helpmanual.io/usage/settings/#field-value-priority) of the class is exactly like in `pydantic.BaseSettings`, except the step which checks azure key vault: 

> settings_args > envs > dotenv > secret_directory > azure_keyvault > defaults

# Install:

```shell
pip install pydantic-azure-secrets
```

# Example:

```python

# Example for GitHub REST API

from pydantic import HttpUrl, SecretStr
from pydantic_azure_secrets import AzureVaultSettings


class GitHubBasic(AzureVaultSettings):
    url: HttpUrl = "https://api.github.com/user"
    username: str
    token: SecretStr

    class Config:
        env_prefix = "github_" 
        azure_keyvault = <your_keyvault_URI> # e.g. "https://pydantic-test-kv.vault.azure.net/"

github_settings = GitHubBasic()
# GitHubBasic(url=HttpUrl('https://github.com', scheme='https', host='github.com', tld='com', host_type='domain'), username='kewtree1408', token=SecretStr('**********'))
```

See more examples in the [example.py](./example.py)

# Authentification
Authentification for azure keyvault is the same as for [SDK](https://docs.microsoft.com/en-us/azure/key-vault/general/secure-your-key-vault)

Before using the library, please log in to your Azure subscription with one of the following methods
- [x] az login
- [x] environment variables: `AZURE_CLIENT_ID`, `AZURE_CLIENT_PASSWORD`, `AZURE_TENANT_ID` [see more](https://pypi.org/project/azure-keyvault-secrets/)

# Run tests

``` sh
tox
```

# TODO:
- [ ] support custom chain authentification for Azure: [example1](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-identity/1.4.0/azure.identity.html#azure.identity.ChainedTokenCredential), [example2](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity#defining-a-custom-authentication-flow-with-chainedtokencredential)
