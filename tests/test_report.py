"""Unit tests for report."""


from jira2confluencegantt.config import ChartEngine, Fields, Project, Report
from jira2confluencegantt.report import _create_report_engine
from jira2confluencegantt.task import TaskList


class ConfluenceClient:
    """Fake Confluence client used to test."""

    def create_new_page(
        self,
        space: str,
        parent_page: str,
        title: str,
        message: str,
    ) -> None:
        """Add new page in Confluence in the given `space`.

        The new page will be located under the `parent_page` and will have the
        given `title` and content `message`.

        :param space: Confluence space.
        :param parent_page: Name of the parent page.
        :param title: Page title.
        :param message: Page message.
        """


def test_create_reporter_with_confluence_chart_engine() -> None:
    """Test reporter creation with Confluence chart engine.

    It must create it without errors.
    """
    project = Project(
        name="",
        jql="",
        report=Report(
            space="SPACE",
            parent_page="My Parent Page",
            engine=ChartEngine.CONFLUENCE,
            legend=False,
        ),
        fields=Fields(start_date="", end_date=""),
    )
    _create_report_engine(project, TaskList(), ConfluenceClient())


def test_create_reporter_with_plant_uml_chart_engine() -> None:
    """Test reporter creation with PlantUML chart engine.

    It must create it without errors.
    """
    project = Project(
        name="",
        jql="",
        report=Report(
            space="SPACE",
            parent_page="My Parent Page",
            engine=ChartEngine.PLANT_UML,
            legend=False,
        ),
        fields=Fields(start_date="", end_date=""),
    )
    _create_report_engine(project, TaskList(), ConfluenceClient())
