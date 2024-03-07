"""Client to communicate with Jira."""

import logging

from atlassian import Jira

#: Create logger for this file.
logger = logging.getLogger()


class JiraClient:
    """Provide an interface to Jira server."""

    def __init__(
        self,
        jira_url: str,
        jira_username: str,
        jira_password: str,
    ) -> None:
        """Construct the Jira client.

        :param jira_url: URL to connect to Jira.
        :param jira_username: Username to connect to Jira.
        :param jira_password: Password to connect to Jira.
        :raises Exception: If Jira server is unreachable or
        authentication failed.
        """
        logger.debug("Create Jira client")

        if not jira_url:
            msg = "Jira URL is invalid"
            raise ValueError(msg)
        if not jira_username:
            msg = "Jira username is invalid"
            raise ValueError(msg)
        if not jira_password:
            msg = "Jira password is invalid"
            raise ValueError(msg)
        try:
            self.__jira_client: Jira = Jira(
                url=jira_url,
                username=jira_username,
                password=jira_password,
            )
        except Exception as error:
            msg = "Failed to create Jira client"
            raise RuntimeError(msg) from error

        logger.debug("Jira client created")

    def ticket_field_value(self, key: str, field_name: str) -> str:
        """Get the value of the given `field_name` from an `key` identifier.

        :param key: Ticket identifier.
        :param field_name: Field name of the ticket to retrieve.
        :return: Ticket value for the given field.
        """
        return str(self.__jira_client.issue_field_value(key, field_name))

    def ticket_title(self, key: str) -> str:
        """Get the title from an `key` identifier.

        :param key: Ticket identifier.
        :return: Ticket title.
        """
        return self.ticket_field_value(key, "summary")

    def tickets_from_jql(
        self,
        jql: str,
        fields: list[str] | str | None = None,
    ) -> list:
        """Get tickets from a `jql` request.

        :param jql: JQL request to find tickets.
        :param fields: list of fields, for example: ['priority', 'summary']
        :return: Tickets list found.
        """
        if fields is None:
            fields = "*all"
        return self.__jira_client.jql(jql, fields=fields, limit=1000)["issues"]

    def custom_field_id_from_name(self, custom_field_name: str) -> str:
        """Retrieve custom field identifier from custom field name.

        :param custom_field_name: Custom field name to convert.
        :return: Custom field identifier or name given in input if no custom
        field match.
        """
        all_custom_fields = self.__jira_client.get_all_custom_fields()
        for custom_field in all_custom_fields:
            if custom_field["name"] == custom_field_name:
                return custom_field["id"]
        return custom_field_name
