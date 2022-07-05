import os
from setuptools import setup, find_packages

try:
    import pypandoc

    long_description = pypandoc.convert("README.md", "rst")
except (IOError, ImportError):
    long_description = "Thumbor redis storage adapters"


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


TESTS_REQUIREMENTS = [
    "black==22.*,>=22.1.0",
    "preggy==1.*,>=1.4.4",
    "pyssim==0.*,>=0.4",
    "pytest==7.*,>=7.0.0",
    "pytest-cov==3.*,>=3.0.0",
    "pytest-asyncio==0.*,>=0.18.0",
]

RUNTIME_REQUIREMENTS = [
    "redis==4.*,>=4.1.3",
    "thumbor==7.*,>=7.0.6",
    "pre-commit==2.*,>=2.17.0",
]

setup(
    name="tc_redis",
    version="2.3.0",
    author="Thumbor Community",
    description=("Thumbor redis storage adapters"),
    license="MIT",
    keywords="thumbor redis",
    url="https://github.com/thumbor-community/redis",
    packages=find_packages(),
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    install_requires=RUNTIME_REQUIREMENTS,
    extras_require={
        "all": RUNTIME_REQUIREMENTS,
        "tests": RUNTIME_REQUIREMENTS + TESTS_REQUIREMENTS,
    },
)
