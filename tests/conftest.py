"""Shared helpers: load a hook file (its name has dashes, so it is not importable by name)."""
import importlib.util
import pathlib

import pytest

HOOKS = pathlib.Path(__file__).resolve().parent.parent / "hooks"


def load_hook(filename):
    path = HOOKS / filename
    name = "hook_" + filename.replace("-", "_").removesuffix(".py")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def hooks_dir():
    return HOOKS
