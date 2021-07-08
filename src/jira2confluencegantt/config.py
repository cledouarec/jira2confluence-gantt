#! python3

"""
Manage configuration file.
"""

import json
import logging
import pathlib
import yaml
from .jiraclient import JiraClient
from .utils import keys_exists

#: Create logger for this file.
logger = logging.getLogger()


class Config:
    """
    This class is used to manage configuration.
    """

    def __init__(self, config: dict):
        """
        Constructs the configuration from dictionary.

        :param config: Configuration dictionary.
        """
        logger.debug("Create configuration")

        Config._check_config(config)

        #: Configuration dictionary already parsed
        self._config: dict = config

        logger.debug("Configuration created")

    @staticmethod
    def _check_server_config(config: dict) -> None:
        """
        Check server configuration, update with default values for optional
        fields or raise an error for mandatory fields.

        :param config: Configuration dictionary.
        :raises Exception: If configuration is invalid.
        """
        if not keys_exists(config, "Server"):
            raise Exception("Missing Server node in configuration")
        if not keys_exists(config, "Server", "Jira"):
            raise Exception("Missing Jira server configuration")
        if not keys_exists(config, "Server", "Confluence"):
            config["Server"]["Confluence"] = None

    @staticmethod
    def _check_project_config(project_name: str, project_config: dict) -> None:
        """
        Check project configuration, update with default values for optional
        fields or raise an error for mandatory fields.

        :param project_name: Project name.
        :param project_config: Project configuration dictionary.
        :raises Exception: If configuration is invalid.
        """
        if not keys_exists(project_config, "JQL"):
            raise Exception(
                "Missing JQL configuration for %s project" % project_name
            )

        if not keys_exists(project_config, "Report"):
            raise Exception(
                "Missing Report node configuration for %s project"
                % project_name,
            )
        if not keys_exists(project_config, "Report", "Engine"):
            project_config["Report"]["Engine"] = "Confluence"
        if not keys_exists(project_config, "Report", "Model"):
            project_config["Report"]["Model"] = None

        if not keys_exists(project_config, "Fields"):
            raise Exception(
                "Missing Fields node configuration for %s project"
                % project_name,
            )
        if not keys_exists(project_config, "Fields", "Start date"):
            raise Exception(
                "Missing Start date configuration for %s project"
                % project_name,
            )
        if not keys_exists(project_config, "Fields", "End date"):
            raise Exception(
                "Missing End date configuration for %s project" % project_name,
            )
        if not keys_exists(project_config, "Fields", "Progress"):
            project_config["Fields"]["Progress"] = None
        if not keys_exists(project_config, "Fields", "Link"):
            project_config["Fields"]["Link"] = "is blocked by"

    @staticmethod
    def _check_config(config: dict) -> None:
        """
        Check configuration, update with default values for optional fields or
        raise an error for mandatory fields.

        :param config: Configuration dictionary.
        :raises Exception: If configuration is invalid.
        """
        Config._check_server_config(config)

        if not keys_exists(config, "Projects"):
            raise Exception("Missing Projects node configuration")
        for project_name, project_config in config["Projects"].items():
            Config._check_project_config(project_name, project_config)

    def dump(self) -> None:
        """
        Dump the configuration.
        """
        print(self._config)

    @property
    def jira(self) -> str:
        """
        Get Jira server URL.

        :return: Jira server URL.
        """
        return self._config["Server"]["Jira"]

    @property
    def confluence(self) -> str:
        """
        Get Confluence server URL.

        :return: Confluence server URL.
        """
        return self._config["Server"]["Confluence"]

    @property
    def projects(self) -> dict:
        """
        Get list of dictionary for all projects configuration.

        :return: List of project configuration.
        """
        return self._config["Projects"]

    def update_custom_fields(self, jira_client: JiraClient) -> None:
        """
        Update the Jira custom fields name in configuration by identifier.

        :param jira_client: Jira client used to request custom fields
        identifier.
        """
        for project in self._config["Projects"]:
            for field in ["Start date", "End date", "Progress"]:
                value = self._config["Projects"][project]["Fields"][field]
                if value:
                    self._config["Projects"][project]["Fields"][
                        field
                    ] = jira_client.custom_field_id_from_name(value)


class YamlConfig(Config):
    """
    This class is used to manage YAML configuration.
    """

    def __init__(self, yaml_config_file: str):
        """
        Constructs the configuration from YAML file.

        :param yaml_config_file: YAML configuration file to parse.
        :raises Exception: If configuration file is invalid.
        """
        logger.info("Parse YAML configuration from %s", yaml_config_file)

        try:
            with open(yaml_config_file) as yaml_config:
                super().__init__(yaml.safe_load(yaml_config))
        except Exception as error:
            raise Exception("Failed to parse YAML configuration") from error

        logger.info("Configuration YAML parsed")


class JsonConfig(Config):
    """
    This class is used to manage JSON configuration.
    """

    def __init__(self, json_config_file: str):
        """
        Constructs the configuration from JSON file.

        :param json_config_file: JSON configuration file to parse.
        :raises Exception: If configuration file is invalid.
        """
        logger.info("Parse JSON configuration from %s", json_config_file)

        try:
            with open(json_config_file) as json_config:
                super().__init__(json.load(json_config))
        except Exception as error:
            raise Exception("Failed to parse JSON configuration") from error

        logger.info("Configuration JSON parsed")


def load_config(config_file: str) -> Config:
    """
    Loads the configuration file (JSON or YAML).

    :param config_file: Configuration file to parse.
    :return: Configuration parsed.
    :raises Exception: If configuration extension file is unknown (.json,
    .yaml, .yml).
    """
    config_type = pathlib.Path(config_file).suffix
    if config_type in [".yaml", ".yml"]:
        return YamlConfig(config_file)
    if config_type == ".json":
        return JsonConfig(config_file)
    raise Exception("Unknown file extension for configuration")
