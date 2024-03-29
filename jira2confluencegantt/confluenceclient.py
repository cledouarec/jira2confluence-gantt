"""Client to communicate with Confluence."""

import logging

from atlassian import Confluence

#: Create logger for this file.
logger = logging.getLogger()


class ConfluenceClient:
    """Provide an interface to Confluence server."""

    def __init__(
        self,
        confluence_url: str,
        confluence_username: str,
        confluence_password: str,
    ) -> None:
        """Construct the Confluence client.

        :param confluence_url: URL to connect to Confluence.
        :param confluence_username: Username to connect to Confluence.
        :param confluence_password: Password to connect to Confluence.
        :raises Exception: If URL, username or password are invalids.
        """
        logger.debug("Create Confluence client")

        if not confluence_url:
            msg = "Confluence URL is invalid"
            raise ValueError(msg)
        if not confluence_username:
            msg = "Confluence username is invalid"
            raise ValueError(msg)
        if not confluence_password:
            msg = "Confluence password is invalid"
            raise ValueError(msg)
        try:
            # Fix API version for cloud to avoid issue
            if (
                "atlassian.net" in confluence_url
                or "jira.com" in confluence_url
            ):
                api_version = "cloud"
            else:
                api_version = "latest"

            self.__confluence_client: Confluence = Confluence(
                url=confluence_url,
                username=confluence_username,
                password=confluence_password,
                api_version=api_version,
            )
        except Exception as error:
            msg = "Failed to create Confluence client"
            raise RuntimeError(msg) from error

        logger.debug("Confluence client created")

    def create_new_page(
        self,
        space: str,
        parent_page: str,
        title: str,
        message: str,
    ) -> None:
        """Add new page in Confluence in the given `space`.

        The new page will be located under the `parent_page` and will have the
        given `title` and content `message` in Wiki markup format.

        :param space: Confluence space.
        :param parent_page: Name of the parent page.
        :param title: Page title.
        :param message: Page message.
        """
        logger.debug("Create new page")

        if not self.__confluence_client.page_exists(space, parent_page):
            msg = "Parent page not found"
            raise RuntimeError(msg)
        parent_id = self.__confluence_client.get_page_id(space, parent_page)

        self.__confluence_client.update_or_create(
            parent_id,
            title,
            message,
            representation="wiki",
        )

        logger.debug("New page created")
