"""Manage configuration file."""

import json
import logging
from dataclasses import dataclass
from enum import Enum, unique
from pathlib import Path

import yaml
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    SecretStr,
    StrictBool,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

from .confluenceclient import ConfluenceClient
from .jiraclient import JiraClient

#: Create logger for this file.
logger = logging.getLogger()


class Secrets(BaseSettings):
    """Store all secrets from environment variables."""

    #: Specific configuration
    model_config = SettingsConfigDict(
        frozen=False,
        env_file=".env",
        env_file_encoding="utf-8",
    )

    #: Username for Jira/Confluence
    user: str = Field(alias="ATLASSIAN_USER")
    #: Token for Jira/Confluence
    token: SecretStr = Field(alias="ATLASSIAN_TOKEN")


class ImmutableModel(BaseModel):
    """Provide immutable model. It is used as base madel."""

    #: Specific configuration
    model_config = ConfigDict(frozen=False)


class Server(ImmutableModel):
    """Store server configuration."""

    #: Jira URL
    jira: HttpUrl
    #: Confluence URL
    confluence: HttpUrl | None = None


@unique
class ChartEngine(Enum):
    """Enumerate all engine used to generate a Gantt chart."""

    #: Confluence chart macro
    CONFLUENCE = "Confluence"
    #: PlantUML generator
    PLANT_UML = "PlantUML"


class Report(ImmutableModel):
    """Store report configuration."""

    #: Confluence output space.
    space: str
    #: Confluence parent page.
    parent_page: str
    #: Engine to produce gantt.
    engine: ChartEngine = ChartEngine.CONFLUENCE
    #: Enable gantt legend.
    legend: StrictBool = False


class Fields(BaseModel):
    """Store fields configuration."""

    #: Jira field to get start date.
    start_date: str
    #: Jira field to get as end date.
    end_date: str
    #: Jira field to get task completion.
    progress: str | None = None
    #: Jira link to use as dependency.
    link: str = "is blocked by"


class Project(ImmutableModel):
    """Store project configuration."""

    #: Project name
    name: str
    #: Query to retrieve tickets
    jql: str
    #: Report configuration.
    report: Report
    #: Fields configuration
    fields: Fields


class Config(ImmutableModel):
    """Store main configuration excepted secrets."""

    #: Server configuration.
    server: Server
    #: List of all projects
    projects: list[Project]


@dataclass
class GlobalConfig:
    """Global configuration."""

    #: Secrets configuration.
    secrets: Secrets
    # Main configuration.
    config: Config

    def json(self) -> str:
        """Return the configuration in json format.

        :return: Configuration string in JSON format.
        """
        return f"""
        {
            {
                "secrets": {self.secrets.model_dump_json()},
                "config": {self.config.model_dump_json()}
            }
        }"""

    def confluence_client(self) -> ConfluenceClient:
        """Create and return a Jira client.

        :return: Jira client.
        """
        return ConfluenceClient(
            str(self.config.server.confluence),
            self.secrets.user,
            self.secrets.token.get_secret_value(),
        )

    def jira_client(self) -> JiraClient:
        """Create and return a Jira client.

        :return: Jira client.
        """
        return JiraClient(
            str(self.config.server.jira),
            self.secrets.user,
            self.secrets.token.get_secret_value(),
        )

    def update_custom_fields(self) -> None:
        """Update the Jira custom fields name by field identifier."""
        jira_client = self.jira_client()
        for project in self.config.projects:
            project.fields.start_date = jira_client.custom_field_id_from_name(
                project.fields.start_date,
            )
            project.fields.end_date = jira_client.custom_field_id_from_name(
                project.fields.end_date,
            )
            if project.fields.progress:
                project.fields.progress = (
                    jira_client.custom_field_id_from_name(
                        project.fields.progress,
                    )
                )


def _parse_yaml_config(yaml_config_file: Path) -> dict:
    """Construct the configuration from YAML file.

    :param yaml_config_file: YAML configuration file to parse.
    :raises Exception: If configuration file is invalid.
    """
    logger.info("Parse YAML configuration from %s", yaml_config_file)

    try:
        with yaml_config_file.open(encoding="utf-8") as yaml_config:
            return yaml.safe_load(yaml_config)
    except yaml.YAMLError as error:
        msg = "Failed to parse YAML configuration"
        raise ValueError(msg) from error


def _parse_json_config(json_config_file: Path) -> dict:
    """Construct the configuration from JSON file.

    :param json_config_file: JSON configuration file to parse.
    :raises Exception: If configuration file is invalid.
    """
    logger.info("Parse JSON configuration from %s", json_config_file)

    try:
        with json_config_file.open(encoding="utf-8") as json_config:
            return json.load(json_config)
    except json.JSONDecodeError as error:
        msg = "Failed to parse JSON configuration"
        raise ValueError(msg) from error


def load_global_config(config_file: str) -> GlobalConfig:
    """Load the configuration file (JSON or YAML) and the secrets.

    :param config_file: Configuration file to parse.
    :return: Configuration parsed.
    :raises Exception: If configuration extension file is unknown (.json,
    .yaml, .yml).
    :raises ValidationError: If configuration is invalid.
    """
    config_file_path = Path(config_file)
    if config_file_path.suffix in [".yaml", ".yml"]:
        config = _parse_yaml_config(config_file_path)
    elif config_file_path.suffix == ".json":
        config = _parse_json_config(config_file_path)
    else:
        msg = "Unknown file extension for configuration"
        raise ValueError(msg)
    return GlobalConfig(Secrets(), Config.model_validate(config))
