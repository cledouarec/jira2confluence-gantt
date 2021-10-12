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


def test_config_with_empty_config() -> None:
    """
    An empty config must raise an exception.
    """
    with pytest.raises(Exception):
        Config({})


@pytest.fixture
def full_config():
    return {
        "Server": {"Jira": "My jira url", "Confluence": "My confluence url"},
        "Projects": {
            "Project": {
                "JQL": "My JQL",
                "Report": {
                    "Engine": "My engine",
                    "Legend": True,
                    "Model": "My model",
                    "Space": "My confluence space",
                    "Parent page": "My parent page",
                },
                "Fields": {
                    "Start date": "My start date",
                    "End date": "My end date",
                    "Progress": "My progress",
                    "Link": "My link",
                },
            },
        },
    }


def test_config_without_server_config(full_config) -> None:
    """
    A config without Server node must raise an exception.
    """
    del full_config["Server"]
    with pytest.raises(Exception):
        Config(full_config)


def test_config_without_server_jira_config(full_config) -> None:
    """
    A config without Server/Jira node must raise an exception.
    """
    del full_config["Server"]["Jira"]
    with pytest.raises(Exception):
        Config(full_config)


def test_config_with_server_jira_config(full_config) -> None:
    """
    A config with Server/Jira node must return the right value.
    """
    config = Config(full_config)
    assert config.jira == "My jira url"


def test_config_without_server_confluence_config(full_config) -> None:
    """
    A config without Server/Confluence node must be created to None value.
    """
    del full_config["Server"]["Confluence"]
    config = Config(full_config)
    assert config.confluence is None


def test_config_with_server_confluence_config(full_config) -> None:
    """
    A config with Server/Confluence node must return the right value.
    """
    config = Config(full_config)
    assert config.confluence == "My confluence url"


def test_config_without_projects_config(full_config) -> None:
    """
    A config without Projects node must raise an exception.
    """
    del full_config["Projects"]
    with pytest.raises(Exception):
        Config(full_config)


def test_config_without_project_jql_config(full_config) -> None:
    """
    A config without Projects/Project/JQL node must raise an exception.
    """
    del full_config["Projects"]["Project"]["JQL"]
    with pytest.raises(Exception):
        Config(full_config)


def test_config_without_project_report_config(full_config) -> None:
    """
    A config without Projects/Project/Report node must raise an exception.
    """
    del full_config["Projects"]["Project"]["Report"]
    with pytest.raises(Exception):
        Config(full_config)


def test_config_without_project_report_engine_config(full_config) -> None:
    """
    A config without Projects/Project/Report/Engine node must be created to
    default value.
    """
    del full_config["Projects"]["Project"]["Report"]["Engine"]
    config = Config(full_config)
    assert config.projects["Project"]["Report"]["Engine"] == "Confluence"


def test_config_without_project_report_legend_config(full_config) -> None:
    """
    A config without Projects/Project/Report/Legend node must be created to
    False value.
    """
    del full_config["Projects"]["Project"]["Report"]["Legend"]
    config = Config(full_config)
    assert not config.projects["Project"]["Report"]["Legend"]


def test_config_without_project_report_model_config(full_config) -> None:
    """
    A config without Projects/Project/Report/Model node must be created to
    None value.
    """
    del full_config["Projects"]["Project"]["Report"]["Model"]
    config = Config(full_config)
    assert config.projects["Project"]["Report"]["Model"] is None


def test_config_without_project_fields_config(full_config) -> None:
    """
    A config without Projects/Project/Fields node must raise an exception.
    """
    del full_config["Projects"]["Project"]["Fields"]
    with pytest.raises(Exception):
        Config(full_config)


def test_config_without_project_fields_start_date_config(full_config) -> None:
    """
    A config without Projects/Project/Fields/Start date node must raise an
    exception.
    """
    del full_config["Projects"]["Project"]["Fields"]["Start date"]
    with pytest.raises(Exception):
        Config(full_config)


def test_config_without_project_fields_end_date_config(full_config) -> None:
    """
    A config without Projects/Project/Fields/End date node must raise an
    exception.
    """
    del full_config["Projects"]["Project"]["Fields"]["End date"]
    with pytest.raises(Exception):
        Config(full_config)


def test_config_without_project_fields_progress_config(full_config) -> None:
    """
    A config without Projects/Project/Fields/Progress node must be created to
    None value.
    """
    del full_config["Projects"]["Project"]["Fields"]["Progress"]
    config = Config(full_config)
    assert config.projects["Project"]["Fields"]["Progress"] is None


def test_config_without_project_fields_link_config(full_config) -> None:
    """
    A config without Projects/Project/Fields/Link node must be created to
    default value.
    """
    del full_config["Projects"]["Project"]["Fields"]["Link"]
    config = Config(full_config)
    assert config.projects["Project"]["Fields"]["Link"] == "is blocked by"
