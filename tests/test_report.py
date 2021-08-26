#! python3

"""
Unit tests for report.
"""

import pytest
from jira2confluencegantt.report import create_report_engine


class ConfluenceClient:
    """
    Fake Confluence client used to test.
    """

    def create_new_page(
        self, space: str, parent_page: str, title: str, message: str
    ) -> None:
        """
        Add new page in Confluence in the given `space`. The new page will be
        located under the `parent_page` and will have the given `title` and
        content `message`.

        :param space: Confluence space.
        :param parent_page: Name of the parent page.
        :param title: Page title.
        :param message: Page message.
        """


def test_create_reporter_with_invalid_chart_engine() -> None:
    """
    Reporter creation with invalid chart engine must raise an exception.
    """
    project_config = {"Report": {"Engine": "InvalidEngine"}}
    with pytest.raises(Exception):
        create_report_engine("", project_config, [], ConfluenceClient())


def test_create_reporter_with_confluence_chart_engine() -> None:
    """
    Reporter creation with Confluence chart engine must create it without
    errors.
    """
    project_config = {"Report": {"Engine": "Confluence"}}
    create_report_engine("", project_config, [], ConfluenceClient())


def test_create_reporter_with_plant_uml_chart_engine() -> None:
    """
    Reporter creation with PlantUML chart engine must create it without errors.
    """
    project_config = {"Report": {"Engine": "PlantUML"}}
    create_report_engine("", project_config, [], ConfluenceClient())
