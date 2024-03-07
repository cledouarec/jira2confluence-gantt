"""Confluence report generation."""

import logging
from datetime import date

from dateutil.parser import isoparse
from jinja2 import Environment, PackageLoader

from .config import ChartEngine, GlobalConfig, Project
from .confluenceclient import ConfluenceClient
from .jiraclient import JiraClient
from .task import Task, TaskList, find_task_by_key, print_tasks

#: Create logger for this file.
logger = logging.getLogger()


class ReportEngine:
    """Manage report generation on Confluence."""

    def __init__(
        self,
        project: Project,
        tasks: TaskList,
        confluence_client: ConfluenceClient | None = None,
    ) -> None:
        """Construct the report generator for the `project`.

        The `tasks` list provides all the task information needed to generate
        gantt.
        The `confluence_client` is optional, in the case which the client is
        not provided, only the gantt would be generated.

        :param project: Project configuration.
        :param tasks: Tasks list extracted from Jira.
        :param confluence_client: Confluence client to publish report.
        """
        logger.debug("Create report engine")

        #: Project configuration
        self._project: Project = project
        #: Tasks list
        self._tasks: TaskList = tasks
        #: Confluence client
        self._confluence_client: ConfluenceClient | None = confluence_client
        #: Object to manipulate the templates.
        self._templates: Environment = Environment(
            loader=PackageLoader("jira2confluencegantt"),
            keep_trailing_newline=True,
            autoescape=True,
        )

        # Add custom filter to format the date in the templates
        self._templates.filters["format_date"] = ReportEngine._format_date

        logger.debug("Report engine created")

    @staticmethod
    def _format_date(value: date, output_format: str) -> str:
        """Convert date to given string `output_format`.

        This method is used to do conversion inside templates.

        :param value: Input date to convert.
        :param output_format: Output string format.
        :return: Date converted in given string format
        """
        return value.strftime(output_format)

    def generate_gantt(self) -> None:
        """Generate the gantt chart."""

    def publish_report(self) -> None:
        """Publish the report with the gantt chart."""

    def _generate_content_from_template(
        self,
        template_name: str,
        parameters: dict,
    ) -> str:
        """Generate Confluence content from Jinja2 template.

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
    """Manage report generation on Confluence with Confluence Chart macro."""

    #: Confluence Chart macro template
    __CHART_TEMPLATE: str = "confluencechart.jinja2"

    def __init__(
        self,
        project: Project,
        tasks: TaskList,
        confluence_client: ConfluenceClient | None = None,
    ) -> None:
        """Construct the report generator  with Confluence Chart macro.

        The report will be generated for the `project_name` on the Confluence
        `output_space` with given `output_parent_page`.
        The `tasks` list provides all the task information needed to generate
        gantt.
        The `confluence_client` is optional, in the case which the client is
        not provided, only the gantt would be generated.

        :param project: Project configuration.
        :param tasks: Tasks list extracted from Jira.
        :param confluence_client: Confluence client to publish report.
        """
        logger.debug("Create Confluence report engine")

        super().__init__(
            project,
            tasks,
            confluence_client,
        )

        #: Confluence gantt macro
        self.__gantt: str = ""

        logger.debug("Confluence report engine created")

    def generate_gantt(self) -> None:
        """Generate the gantt chart."""
        logger.debug(
            "Generate gantt chart with Confluence for %s",
            self._project.name,
        )

        self.__gantt = self._generate_content_from_template(
            ConfluenceEngine.__CHART_TEMPLATE,
            {
                "tasks": self._tasks.to_pre_order_list(),
                "has_legend": self._project.report.legend,
            },
        )

        logger.debug(
            "Gantt chart with Confluence for %s generated",
            self._project.name,
        )

    def publish_report(self) -> None:
        """Publish the report with the gantt chart."""
        if not self._confluence_client:
            return

        logger.debug("Publish report on Confluence with Confluence engine")

        self._confluence_client.create_new_page(
            space=self._project.report.space,
            parent_page=self._project.report.parent_page,
            title=f"[{self._project.name}] Gantt",
            message=self.__gantt,
        )

        logger.debug("Report published on Confluence with Confluence engine")


class PlantUMLEngine(ReportEngine):
    """Manage report generation on Confluence generated with PlantUML."""

    #: PlantUML template
    __PLANT_UML_TEMPLATE: str = "plantuml.jinja2"

    #: PlantUML template
    __PLANT_UML_MACRO_TEMPLATE: str = "plantumlmacro.jinja2"

    def __init__(
        self,
        project: Project,
        tasks: TaskList,
        confluence_client: ConfluenceClient | None = None,
    ) -> None:
        """Construct the report generator for the `project` with PlantUML.

        The `tasks` list provides all the task information needed to generate
        gantt.
        The `confluence_client` is optional, in the case which the client is
        not provided, only the gantt would be generated.

        :param project: Project configuration.
        :param tasks: Tasks list extracted from Jira.
        :param confluence_client: Confluence client to publish report.
        """
        logger.debug("Create PlantUML report engine")

        super().__init__(
            project,
            tasks,
            confluence_client,
        )

        self.__gantt = ""

        logger.debug("PlantUML report engine created")

    def generate_gantt(self) -> None:
        """Generate the gantt chart in SVG format."""
        logger.debug(
            "Generate gantt chart with PlantUML for %s",
            self._project.name,
        )

        self.__gantt = self._generate_content_from_template(
            PlantUMLEngine.__PLANT_UML_TEMPLATE,
            {
                "tasks": self._tasks.to_pre_order_list(),
                "has_legend": self._project.report.legend,
            },
        )

        logger.debug(
            "Gantt chart with PlantUML for %s generated",
            self._project.name,
        )

    def publish_report(self) -> None:
        """Publish the report with the gantt chart."""
        if not self._confluence_client:
            return

        logger.debug("Publish report on Confluence with PlantUML engine")

        message = self._generate_content_from_template(
            PlantUMLEngine.__PLANT_UML_MACRO_TEMPLATE,
            {"plantuml": self.__gantt},
        )
        self._confluence_client.create_new_page(
            space=self._project.report.space,
            parent_page=self._project.report.parent_page,
            title=f"[{self._project.name}] Gantt",
            message=message,
        )

        logger.debug("Report published on Confluence with PlantUML engine")


def _tickets_from_project(jira_client: JiraClient, project: Project) -> list:
    """Get all tickets for a given project configuration.

    The result list will be sorted by start date and end date.

    :param jira_client: Jira client to retrieve tickets information.
    :param project: Project configuration with JQL or fields to extract.
    :return: Tickets list for this project.
    """
    start_date_field = project.fields.start_date
    end_date_field = project.fields.end_date
    fields = [
        "key",
        "summary",
        start_date_field,
        end_date_field,
        "parent",
        "subtasks",
        "issuelinks",
    ]
    if project.fields.progress:
        fields.append(project.fields.progress)

    tickets = jira_client.tickets_from_jql(jql=project.jql, fields=fields)

    def _has_start_and_end_dates(ticket: dict) -> bool:
        """Check if the `ticket` has a start and end dates.

        :param ticket: Ticket to test.
        :return: Boolean status of the check.
        """
        start_date = ticket["fields"].get(start_date_field)
        end_date = ticket["fields"].get(end_date_field)
        return start_date is not None and end_date is not None

    return sorted(
        filter(_has_start_and_end_dates, tickets),
        key=lambda ticket: (
            ticket["fields"][start_date_field],
            ticket["fields"][end_date_field],
        ),
    )


def _create_tasks_from_tickets(tickets: list, project: Project) -> TaskList:
    """Create all tasks from a list of `tickets`.

    The tasks list is ordered according to the start date field.

    :param tickets: Tickets list.
    :param project: Project configuration.
    :return: Tasks list for this project.
    """
    start_date_field = project.fields.start_date
    end_date_field = project.fields.end_date
    progress_field = project.fields.progress
    link_type = project.fields.link

    tasks = TaskList()
    for ticket in tickets:
        # Get blocking tasks
        blocking_tasks = [
            link["inwardIssue"]["key"]
            for link in ticket["fields"]["issuelinks"]
            if link.get("type", {}).get("inward") == link_type
            and "inwardIssue" in link
            and any(
                _ticket["key"] == link["inwardIssue"]["key"]
                for _ticket in tickets
            )
        ]

        # Get parent
        parent = None
        if parent_key := ticket["fields"].get("parent", {}).get("key"):
            parent = find_task_by_key(tasks, parent_key)
        if parent is None:
            parent = tasks

        # Get children
        children = [
            child
            for sub_task in ticket["fields"]["subtasks"]
            if (child := find_task_by_key(tasks, sub_task["key"])) is not None
        ]

        Task(
            key=ticket["key"],
            summary=ticket["fields"]["summary"],
            start_date=isoparse(ticket["fields"][start_date_field]),
            end_date=isoparse(ticket["fields"][end_date_field]),
            progress_in_percent=ticket["fields"].get(progress_field),
            blocking_tasks=blocking_tasks,
            parent=parent,
            children=children,
        )
    return tasks


def _create_report_engine(
    project: Project,
    tasks: TaskList,
    confluence_client: ConfluenceClient | None = None,
) -> ReportEngine:
    """Create the report engine based on `project` configuration.

    The `confluence_client` is optional, in the case which the client is not
    provided, only the gantt would be generated.

    :param project: Project configuration with fields and links to use.
    :param tasks: Tasks list extracted from Jira.
    :param confluence_client: Confluence client to publish report.
    :return: New report engine created.
    """
    chart_engine = project.report.engine

    if chart_engine == ChartEngine.CONFLUENCE:
        return ConfluenceEngine(
            project,
            tasks,
            confluence_client,
        )
    if chart_engine == ChartEngine.PLANT_UML:
        return PlantUMLEngine(
            project,
            tasks,
            confluence_client,
        )
    msg = "Invalid Gantt engine"
    raise ValueError(msg)


def generate_all_reports(global_config: GlobalConfig) -> None:
    """Generate all reports given by `global_config`.

    :param global_config: Global configuration.
    """
    logger.info("Generate report on Confluence")

    for project in global_config.config.projects:
        # Create the tasks from the tickets
        tickets = _tickets_from_project(global_config.jira_client(), project)
        tasks = _create_tasks_from_tickets(tickets, project)
        if logger.getEffectiveLevel() == logging.DEBUG:
            print_tasks(tasks)

        # Create the engine according to engine specified
        engine = _create_report_engine(
            project,
            tasks,
            global_config.confluence_client(),
        )

        # Create gantt and publish on Confluence
        engine.generate_gantt()
        engine.publish_report()

    logger.info("Report on Confluence generated")
