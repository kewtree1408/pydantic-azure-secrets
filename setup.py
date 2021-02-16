import os
import re

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def get_version(package):
    """
    Returns version of a package (`__version__` in `init.py`).
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.match("(?s).*__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


setuptools.setup(
    name="pydantic-azure-secrets",
    version=get_version("pydantic_azure_secrets"),
    author="Victoria",
    author_email="me@vika.space",
    license="MIT",
    description="Pydantic extention to work with Azure Key Vaults",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kewtree1408/pydantic-azure-secrets",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pydantic==1.7.3",
        "python-dotenv==0.15.0",
        "azure-identity==1.5.0",
        "azure-keyvault-secrets==4.2.0",
    ],
    extras_require={
        "test": [
            "pytest==6.2.1",
            "pytest-cov==2.11.1",
            "black==19.10b0",
            "isort==5.7.0",
            "mypy==0.800",
            "mypy-extensions==0.4.3",
            "pylint==2.6.0",
            "flake8==3.8.4",
        ]
    },
)
