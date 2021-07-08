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
        project_config: dict,
        tickets: list,
        confluence_client: Optional[ConfluenceClient] = None,
    ):
        """
        Constructs the report generator for the `project_name` with the given
        `project_config`. The `tickets` list provides all the information
        needed by the config. The `confluence_client` is optional, in the case
        which the client is not provided, only the gantt would be generated.

        :param project_name: Project name.
        :param project_config: Project configuration with fields and links to
        use.
        :param tickets: Tickets list extracted from JQL.
        :param confluence_client: Confluence client to publish report.
        """
        logger.debug("Create report engine")

        #: Project name
        self._project_name: str = project_name
        #: Project configuration
        self._project_config: dict = project_config
        #: Tickets list
        self._tickets: list = tickets
        #: Confluence client
        self._confluence_client: ConfluenceClient = confluence_client
        #: Object to manipulate the templates.
        self._templates: Environment = Environment(
            loader=PackageLoader("jira2confluencegantt"),
            keep_trailing_newline=True,
        )

        logger.debug("Report engine created")

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
        project_config: dict,
        tickets: list,
        confluence_client: Optional[ConfluenceClient] = None,
    ):
        """
        Constructs the report generator for the `project_name` with the given
        `project_config`. The `tickets` list provides all the information
        needed by the config. The `confluence_client` is optional, in the case
        which the client is not provided, only the gantt would be generated.

        :param project_name: Project name.
        :param project_config: Project configuration with fields and links to
        use.
        :param tickets: Tickets list extracted from JQL.
        :param confluence_client: Confluence client to publish report.
        """
        logger.debug("Create Confluence report engine")

        super().__init__(
            project_name, project_config, tickets, confluence_client
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

        start_date_field = self._project_config["Fields"]["Start date"]
        end_date_field = self._project_config["Fields"]["End date"]
        progress_field = self._project_config["Fields"]["Progress"]

        tasks = list()
        for ticket in self._tickets:
            task = {
                "key": ticket["key"],
                "start": ConfluenceEngine.__convert_date(
                    ticket["fields"][start_date_field]
                ),
                "stop": ConfluenceEngine.__convert_date(
                    ticket["fields"][end_date_field]
                ),
                "percent": ticket["fields"][progress_field],
            }
            tasks.append(task)

        self.__gantt = self._generate_content_from_template(
            ConfluenceEngine.__CHART_TEMPLATE, {"tasks": tasks}
        )

        logger.debug(
            "Gantt chart with Confluence for %s generated", self._project_name
        )

    @staticmethod
    def __convert_date(jira_date: str) -> str:
        """
        Convert date from Jira to Confluence format.

        :param jira_date: Input date in Jira format.
        :return: Date converted in Confluence format.
        """
        return date.fromisoformat(jira_date).strftime("%d/%m/%Y")

    def publish_report(self) -> None:
        """
        Publish the report with the gantt chart.
        """
        if not self._confluence_client:
            return

        logger.debug("Publish report on Confluence with Confluence engine")

        self._confluence_client.create_new_page(
            space=self._project_config["Report"]["Space"],
            parent_page=self._project_config["Report"]["Parent page"],
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
        project_config: dict,
        tickets: list,
        confluence_client: Optional[ConfluenceClient] = None,
    ):
        """
        Constructs the report generator for the `project_name` with the given
        `project_config`. The `tickets` list provides all the information
        needed by the config. The `confluence_client` is optional, in the case
        which the client is not provided, only the gantt would be generated.

        :param project_name: Project name.
        :param project_config: Project configuration with fields and links to
        use.
        :param tickets: Tickets list extracted from JQL.
        :param confluence_client: Confluence client to publish report.
        """
        logger.debug("Create PlantUML report engine")

        super().__init__(
            project_name, project_config, tickets, confluence_client
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

        start_date_field = self._project_config["Fields"]["Start date"]
        end_date_field = self._project_config["Fields"]["End date"]
        progress_field = self._project_config["Fields"]["Progress"]
        link_type = self._project_config["Fields"]["Link"]

        tasks = list()
        for ticket in self._tickets:
            links = []
            if link_type:
                for link in ticket["fields"]["issuelinks"]:
                    if link["type"]["inward"] == link_type and keys_exists(
                        link, "inwardIssue"
                    ):
                        links.append(link["inwardIssue"]["key"])

            task = {
                "key": ticket["key"],
                "summary": ticket["fields"]["summary"]
                .replace("[", "<U+005b>")
                .replace("]", "<U+005d>"),
                "start": ticket["fields"][start_date_field],
                "stop": ticket["fields"][end_date_field],
                "percent": ticket["fields"][progress_field],
                "links": links,
            }
            tasks.append(task)

        self.__gantt = self._generate_content_from_template(
            PlantUMLEngine.__PLANT_UML_TEMPLATE, {"tasks": tasks}
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
            space=self._project_config["Report"]["Space"],
            parent_page=self._project_config["Report"]["Parent page"],
            title="[{project}] Gantt".format(project=self._project_name),
            message=message,
        )

        logger.debug("Report published on Confluence with PlantUML engine")


def tickets_by_projects(jira_client: JiraClient, project_config: dict) -> list:
    """
    Get all tickets for a given project configuration. The tickets list is
    ordered according to the start date field.

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
        "issuelinks",
    ]
    tickets = jira_client.tickets_from_jql(
        jql=project_config["JQL"], fields=fields
    )

    def has_start_and_end_dates(ticket: dict) -> bool:
        """
        Check if the `ticket` has a start and end dates.

        :param ticket: Ticket to test.
        :return: Boolean status of the check.
        """
        start_date = ticket["fields"][start_date_field]
        end_date = ticket["fields"][end_date_field]
        return start_date is not None and end_date is not None

    return sorted(
        filter(has_start_and_end_dates, tickets),
        key=lambda ticket: (
            ticket["fields"][start_date_field],
            ticket["fields"][end_date_field],
            ticket["key"],
        ),
    )


def create_report_engine(
    project_name: str,
    project_config: dict,
    tickets: list,
    confluence_client: Optional[ConfluenceClient] = None,
) -> ReportEngine:
    """
    Create the report engine depending of the engine configured by the
    `project_config`. The `confluence_client` is optional, in the case
    which the client is not provided, only the gantt would be generated.

    :param project_name: Project name.
    :param project_config: Project configuration with fields and links to
    use.
    :param tickets: Tickets list extracted from JQL.
    :param confluence_client: Confluence client to publish report.
    :return: New report engine created.
    """
    chart_engine = ChartEngine(project_config["Report"]["Engine"])
    if chart_engine == ChartEngine.CONFLUENCE:
        return ConfluenceEngine(
            project_name, project_config, tickets, confluence_client
        )
    if chart_engine == ChartEngine.PLANT_UML:
        return PlantUMLEngine(
            project_name, project_config, tickets, confluence_client
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
        tickets = tickets_by_projects(jira_client, project_config)

        # Create the engine according to engine specified
        engine = create_report_engine(
            project_name, project_config, tickets, confluence_client
        )

        # Create gantt and publish on Confluence
        engine.generate_gantt()
        engine.publish_report()

    logger.info("Report on Confluence generated")
