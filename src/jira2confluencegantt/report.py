#! python3

"""
Confluence report generation.
"""

from datetime import date
from enum import Enum, unique
import logging
from typing import Any, Optional
from jinja2 import Environment, PackageLoader
from .config import Config
from .confluenceclient import ConfluenceClient
from .jiraclient import JiraClient
from .task import find_task_by_key, Task, TaskList
from .utils import keys_exists

#: Create logger for this file.
logger = logging.getLogger()


@unique
class ChartEngine(Enum):
    """
    This class is used to enumerate all engine used to generate a Gantt chart.
    """

    #: Confluence chart macro
    CONFLUENCE = "Confluence"

    #: PlantUML generator
    PLANT_UML = "PlantUML"


class ReportEngine:
    """
    This class is used to manage report generation on Confluence.
    """

    def __init__(
        self,
        project_name: str,
        output_space: str,
        output_parent_page: str,
        tasks: TaskList,
        confluence_client: Optional[ConfluenceClient] = None,
    ):
        """
        Constructs the report generator for the `project_name`.
        The report will be generated on the Confluence `output_space` with
        given `output_parent_page`.
        The `tasks` list provides all the task information needed to generate
        gantt.
        The `confluence_client` is optional, in the case which the client is
        not provided, only the gantt would be generated.

        :param project_name: Project name.
        :param output_space: Project output Confluence space.
        :param output_parent_page: Project output Confluence parent page.
        :param tasks: Tasks list extracted from Jira.
        :param confluence_client: Confluence client to publish report.
        """
        logger.debug("Create report engine")

        #: Project name
        self._project_name: str = project_name
        #: Project output Confluence space
        self._output_space: str = output_space
        #: Project output Confluence parent page
        self._output_parent_page: str = output_parent_page
        #: Tasks list
        self._tasks: TaskList = tasks
        #: Confluence client
        self._confluence_client: Optional[ConfluenceClient] = confluence_client
        #: Object to manipulate the templates.
        self._templates: Environment = Environment(
            loader=PackageLoader("jira2confluencegantt"),
            keep_trailing_newline=True,
        )

        # Add custom filter to format the date in the templates
        self._templates.filters["format_date"] = ReportEngine._format_date

        logger.debug("Report engine created")

    @staticmethod
    def _format_date(value: date, output_format: str) -> str:
        """
        Convert date to given string `output_format`. This method is used to do
        conversion inside templates.

        :param value: Input date to convert.
        :param output_format: Output string format.
        :return: Date converted in given string format
        """
        return value.strftime(output_format)

    def generate_gantt(self) -> None:
        """
        Generate the gantt chart.
        """

    def publish_report(self) -> None:
        """
        Publish the report with the gantt chart.
        """

    def _generate_content_from_template(
        self, template_name: str, parameters: Any
    ) -> str:
        """
        Generate Confluence content from Jinja2 template.

        :param template_name: Name of the template to use.
        :param parameters: Parameters used by the template.
        :return: Confluence content generated.
        """
        logger.debug("Generated content from %s", template_name)

        # Generate code file from template
        template = self._templates.get_template(template_name)
        content = template.render(parameters=parameters)

        logger.debug("Content from %s generated", template_name)
        return content


class ConfluenceEngine(ReportEngine):
    """
    This class is used to manage report generation on Confluence with a Gantt
    chart generated with Confluence Chart macro.
    """

    #: Confluence Chart macro template
    __CHART_TEMPLATE: str = "confluencechart.jinja2"

    def __init__(
        self,
        project_name: str,
        output_space: str,
        output_parent_page: str,
        tasks: TaskList,
        confluence_client: Optional[ConfluenceClient] = None,
    ):
        """
        Constructs the report generator for the `project_name` with Confluence
        Chart macro.
        The report will be generated on the Confluence `output_space` with
        given `output_parent_page`.
        The `tasks` list provides all the task information needed to generate
        gantt.
        The `confluence_client` is optional, in the case which the client is
        not provided, only the gantt would be generated.

        :param project_name: Project name.
        :param output_space: Project output Confluence space.
        :param output_parent_page: Project output Confluence parent page.
        :param tasks: Tasks list extracted from Jira.
        :param confluence_client: Confluence client to publish report.
        """
        logger.debug("Create Confluence report engine")

        super().__init__(
            project_name,
            output_space,
            output_parent_page,
            tasks,
            confluence_client,
        )

        #: Confluence gantt macro
        self.__gantt: str = ""

        logger.debug("Confluence report engine created")

    def generate_gantt(self) -> None:
        """
        Generate the gantt chart.
        """
        logger.debug(
            "Generate gantt chart with Confluence for %s", self._project_name
        )

        self.__gantt = self._generate_content_from_template(
            ConfluenceEngine.__CHART_TEMPLATE,
            {"tasks": self._tasks.to_pre_order_list()},
        )

        logger.debug(
            "Gantt chart with Confluence for %s generated", self._project_name
        )

    def publish_report(self) -> None:
        """
        Publish the report with the gantt chart.
        """
        if not self._confluence_client:
            return

        logger.debug("Publish report on Confluence with Confluence engine")

        self._confluence_client.create_new_page(
            space=self._output_space,
            parent_page=self._output_parent_page,
            title="[{project}] Gantt".format(project=self._project_name),
            message=self.__gantt,
        )

        logger.debug("Report published on Confluence with Confluence engine")


class PlantUMLEngine(ReportEngine):
    """
    This class is used to manage report generation on Confluence with a Gantt
    chart generated with PlantUML.
    """

    #: PlantUML template
    __PLANT_UML_TEMPLATE: str = "plantuml.jinja2"

    #: PlantUML template
    __PLANT_UML_MACRO_TEMPLATE: str = "plantumlmacro.jinja2"

    def __init__(
        self,
        project_name: str,
        output_space: str,
        output_parent_page: str,
        tasks: TaskList,
        confluence_client: Optional[ConfluenceClient] = None,
    ):
        """
        Constructs the report generator for the `project_name` with PlantUML.
        The report will be generated on the Confluence `output_space` with
        given `output_parent_page`.
        The `tasks` list provides all the task information needed to generate
        gantt.
        The `confluence_client` is optional, in the case which the client is
        not provided, only the gantt would be generated.

        :param project_name: Project name.
        :param output_space: Project output Confluence space.
        :param output_parent_page: Project output Confluence parent page.
        :param tasks: Tasks list extracted from Jira.
        :param confluence_client: Confluence client to publish report.
        """
        logger.debug("Create PlantUML report engine")

        super().__init__(
            project_name,
            output_space,
            output_parent_page,
            tasks,
            confluence_client,
        )

        self.__gantt = ""

        logger.debug("PlantUML report engine created")

    def generate_gantt(self) -> None:
        """
        Generate the gantt chart in SVG format.
        """
        logger.debug(
            "Generate gantt chart with PlantUML for %s", self._project_name
        )

        self.__gantt = self._generate_content_from_template(
            PlantUMLEngine.__PLANT_UML_TEMPLATE,
            {"tasks": self._tasks.to_pre_order_list()},
        )

        logger.debug(
            "Gantt chart with PlantUML for %s generated", self._project_name
        )

    def publish_report(self) -> None:
        """
        Publish the report with the gantt chart.
        """
        if not self._confluence_client:
            return

        logger.debug("Publish report on Confluence with PlantUML engine")

        message = self._generate_content_from_template(
            PlantUMLEngine.__PLANT_UML_MACRO_TEMPLATE,
            {"plantuml": self.__gantt},
        )
        self._confluence_client.create_new_page(
            space=self._output_space,
            parent_page=self._output_parent_page,
            title="[{project}] Gantt".format(project=self._project_name),
            message=message,
        )

        logger.debug("Report published on Confluence with PlantUML engine")


def _tickets_from_project(
    jira_client: JiraClient, project_config: dict
) -> list:
    """
    Get all tickets with needed fields for a given project configuration and
    sorted the list by start date and end date.

    :param jira_client: Jira client to retrieve tickets information.
    :param project_config: Project configuration with JQL or fields to extract.
    :return: Tickets list for this project.
    """
    start_date_field = project_config["Fields"]["Start date"]
    end_date_field = project_config["Fields"]["End date"]
    fields = [
        "key",
        "summary",
        start_date_field,
        end_date_field,
        project_config["Fields"]["Progress"],
        "parent",
        "subtasks",
        "issuelinks",
    ]
    tickets = jira_client.tickets_from_jql(
        jql=project_config["JQL"], fields=fields
    )

    def _has_start_and_end_dates(ticket: dict) -> bool:
        """
        Check if the `ticket` has a start and end dates.

        :param ticket: Ticket to test.
        :return: Boolean status of the check.
        """
        start_date = ticket["fields"][start_date_field]
        end_date = ticket["fields"][end_date_field]
        return start_date is not None and end_date is not None

    return sorted(
        filter(_has_start_and_end_dates, tickets),
        key=lambda ticket: (
            ticket["fields"][start_date_field],
            ticket["fields"][end_date_field],
        ),
    )


def _create_tasks_from_tickets(
    tickets: list, project_config: dict
) -> TaskList:
    """
    Create all tasks from a list of `tickets` and a given `project_config`.
    The tasks list is ordered according to the start date field.

    :param tickets: Tickets list.
    :param project_config: Project configuration.
    :return: Tasks list for this project.
    """
    start_date_field = project_config["Fields"]["Start date"]
    end_date_field = project_config["Fields"]["End date"]
    progress_field = project_config["Fields"]["Progress"]
    link_type = project_config["Fields"]["Link"]

    tasks = TaskList()
    for ticket in tickets:
        # By default a task without progress is considered not started
        progress = ticket["fields"][progress_field]
        if progress is None:
            progress = 0.0

        # Get blocking tasks
        blocking_tasks = []
        for link in ticket["fields"]["issuelinks"]:
            if link["type"]["inward"] == link_type and keys_exists(
                link, "inwardIssue"
            ):
                # Add only if the blocking task is present in the ticket list.
                for _ticket in tickets:
                    if _ticket["key"] == link["inwardIssue"]["key"]:
                        blocking_tasks.append(link["inwardIssue"]["key"])
                        break

        # Get parent
        parent = None
        if keys_exists(ticket["fields"], "parent", "key"):
            parent = find_task_by_key(tasks, ticket["fields"]["parent"]["key"])
        if parent is None:
            parent = tasks

        # Get children
        children = []
        for sub_task in ticket["fields"]["subtasks"]:
            child = find_task_by_key(tasks, sub_task["key"])
            if child:
                children.append(child)

        Task(
            key=ticket["key"],
            summary=ticket["fields"]["summary"],
            start_date=date.fromisoformat(ticket["fields"][start_date_field]),
            end_date=date.fromisoformat(ticket["fields"][end_date_field]),
            progress_in_percent=progress,
            blocking_tasks=blocking_tasks,
            parent=parent,
            children=children,
        )
    return tasks


def _create_report_engine(
    project_name: str,
    project_config: dict,
    tasks: TaskList,
    confluence_client: Optional[ConfluenceClient] = None,
) -> ReportEngine:
    """
    Create the report engine depending of the engine configured by the
    `project_config`. The `confluence_client` is optional, in the case
    which the client is not provided, only the gantt would be generated.

    :param project_name: Project name.
    :param project_config: Project configuration with fields and links to
    use.
    :param tasks: Tasks list extracted from Jira.
    :param confluence_client: Confluence client to publish report.
    :return: New report engine created.
    """
    chart_engine = ChartEngine(project_config["Report"]["Engine"])
    output_space = project_config["Report"]["Space"]
    output_parent_page = project_config["Report"]["Parent page"]

    if chart_engine == ChartEngine.CONFLUENCE:
        return ConfluenceEngine(
            project_name,
            output_space,
            output_parent_page,
            tasks,
            confluence_client,
        )
    if chart_engine == ChartEngine.PLANT_UML:
        return PlantUMLEngine(
            project_name,
            output_space,
            output_parent_page,
            tasks,
            confluence_client,
        )
    raise Exception("Invalid Gantt engine")


def generate_all_reports(
    jira_client: JiraClient,
    config: Config,
    confluence_client: Optional[ConfluenceClient] = None,
) -> None:
    """
    Generate all reports. The `confluence_client` is optional, in the case
    which the client is not provided, only the gantt would be generated.

    :param jira_client: Jira client to retrieve tickets information.
    :param confluence_client: Confluence client to publish gantt charts.
    :param config: Global configuration.
    """
    logger.info("Generate report on Confluence")

    config.update_custom_fields(jira_client)

    for project_name, project_config in config.projects.items():
        # Create the tasks from the tickets
        tickets = _tickets_from_project(jira_client, project_config)
        tasks = _create_tasks_from_tickets(tickets, project_config)

        # Create the engine according to engine specified
        engine = _create_report_engine(
            project_name, project_config, tasks, confluence_client
        )

        # Create gantt and publish on Confluence
        engine.generate_gantt()
        engine.publish_report()

    logger.info("Report on Confluence generated")
