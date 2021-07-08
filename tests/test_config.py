#! python3

"""
Unit tests for config.
"""

import pytest
from jira2confluencegantt.config import (
    Config,
    JsonConfig,
    YamlConfig,
    load_config,
)


@pytest.fixture(scope="module")
def script_loc(request):
    """
    Return the directory of the currently running test script.
    """

    # uses .join instead of .dirname so we get a LocalPath object instead of
    # a string. LocalPath.join calls normpath for us when joining the path
    return request.fspath.join("..")


def test_load_config_with_invalid_file_extension() -> None:
    """
    Loads config with unsupported file extension must raise an exception.
    """
    with pytest.raises(Exception):
        load_config("config.test")


def test_yaml_config_with_invalid_file() -> None:
    """
    Read YAML config without file name must raise an exception.
    """
    with pytest.raises(Exception):
        YamlConfig("")


def test_json_config_with_invalid_file() -> None:
    """
    Read JSON config without file name must raise an exception.
    """
    with pytest.raises(Exception):
        JsonConfig("")


def test_yaml_basic_config(script_loc) -> None:
    """
    YAML basic config must be loaded without errors.
    """
    config = script_loc.join("../examples/basic_config.yaml")
    load_config(config)


def test_json_basic_config(script_loc) -> None:
    """
    JSON basic config must be loaded without errors.
    """
    config = script_loc.join("../examples/basic_config.json")
    load_config(config)


def test_yaml_basic_with_dependency_links_config(script_loc) -> None:
    """
    YAML basic config with dependency links must be loaded without errors.
    """
    config = script_loc.join(
        "../examples/basic_with_dependency_link_config.yaml"
    )
    load_config(config)


def test_json_basic_with_dependency_links_config(script_loc) -> None:
    """
    JSON basic config with dependency links must be loaded without errors.
    """
    config = script_loc.join(
        "../examples/basic_with_dependency_link_config.json"
    )
    load_config(config)


def test_yaml_full_config(script_loc) -> None:
    """
    YAML full config must be loaded without errors.
    """
    config = script_loc.join("../examples/full_config.yaml")
    load_config(config)


def test_json_full_config(script_loc) -> None:
    """
    JSON full config must be loaded without errors.
    """
    config = script_loc.join("../examples/full_config.json")
    load_config(config)


def test_yaml_multi_projects_config(script_loc) -> None:
    """
    YAML multi projects config must be loaded without errors.
    """
    config = script_loc.join("../examples/multi_projects_config.yaml")
    load_config(config)


def test_json_multi_projects_config(script_loc) -> None:
    """
    JSON multi projects config must be loaded without errors.
    """
    config = script_loc.join("../examples/multi_projects_config.json")
    load_config(config)


def test_yaml_multi_projects_with_anchor_config(script_loc) -> None:
    """
    YAML multi projects config with_anchor must be loaded without errors.
    """
    config = script_loc.join(
        "../examples/multi_projects_with_anchor_config.yaml"
    )
    load_config(config)


def test_config_with_missing_mandatory_nodes() -> None:
    """
    A config without all mandatory nodes must raise an exception.
    """
    with pytest.raises(Exception):
        Config({})
    with pytest.raises(Exception):
        Config({"Server": {}})
    with pytest.raises(Exception):
        Config({"Server": {"Jira": ""}})
