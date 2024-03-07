"""Unit tests for config."""

import os

import pytest

from jira2confluencegantt.config import GlobalConfig, load_global_config


@pytest.fixture(autouse=True)
def _secrets():
    """Set secrets as environment variables."""
    os.environ["ATLASSIAN_USER"] = "Username"
    os.environ["ATLASSIAN_TOKEN"] = "Token"  # noqa: S105


@pytest.fixture(scope="module")
def script_loc(request):
    """Return the directory of the currently running test script."""
    # uses .join instead of .dirname so we get a LocalPath object instead of
    # a string. LocalPath.join calls normpath for us when joining the path
    return request.fspath.join("..")


def test_load_config_with_invalid_file_extension() -> None:
    """Loads config with unsupported file extension.

    It must raise an exception.
    """
    with pytest.raises(
        ValueError,
        match="Unknown file extension for configuration",
    ):
        load_global_config("config.test")


def test_yaml_basic_config(script_loc) -> None:
    """Test YAML basic config.

    It must be loaded without errors.
    """
    config = script_loc.join("../examples/basic_config.yaml")
    load_global_config(config)


def test_json_basic_config(script_loc) -> None:
    """Test JSON basic config.

    It must be loaded without errors.
    """
    config = script_loc.join("../examples/basic_config.json")
    load_global_config(config)


def test_yaml_basic_with_dependency_links_config(script_loc) -> None:
    """Test YAML basic config with dependency links.

    It must be loaded without errors.
    """
    config = script_loc.join(
        "../examples/basic_with_dependency_link_config.yaml",
    )
    load_global_config(config)


def test_json_basic_with_dependency_links_config(script_loc) -> None:
    """Test JSON basic config with dependency links.

    It must be loaded without errors.
    """
    config = script_loc.join(
        "../examples/basic_with_dependency_link_config.json",
    )
    load_global_config(config)


def test_yaml_full_config(script_loc) -> None:
    """Test YAML full config.

    It must be loaded without errors.
    """
    config = script_loc.join("../examples/full_config.yaml")
    load_global_config(config)


def test_json_full_config(script_loc) -> None:
    """Test JSON full config.

    It must be loaded without errors.
    """
    config = script_loc.join("../examples/full_config.json")
    load_global_config(config)


def test_yaml_multi_projects_config(script_loc) -> None:
    """Test YAML multi projects' config.

    It must be loaded without errors.
    """
    config = script_loc.join("../examples/multi_projects_config.yaml")
    load_global_config(config)


def test_json_multi_projects_config(script_loc) -> None:
    """Test JSON multi projects' config.

    It must be loaded without errors.
    """
    config = script_loc.join("../examples/multi_projects_config.json")
    load_global_config(config)


def test_yaml_multi_projects_with_anchor_config(script_loc) -> None:
    """Test YAML multi projects config with anchor.

    It must be loaded without errors.
    """
    config = script_loc.join(
        "../examples/multi_projects_with_anchor_config.yaml",
    )
    load_global_config(config)


def test_config_with_empty_config() -> None:
    """Test Empty config.

    It must raise an exception.
    """
    with pytest.raises(
        TypeError,
        match="missing 1 required positional argument",
    ):
        GlobalConfig({})
