"""Test-Setup: die Integration aus diesem Repo für den HA-Loader sichtbar machen."""

import pathlib

import custom_components

_REPO_CC = str(pathlib.Path(__file__).resolve().parent.parent / "custom_components")
if _REPO_CC not in custom_components.__path__:
    custom_components.__path__.append(_REPO_CC)
