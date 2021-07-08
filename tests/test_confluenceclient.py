#! python3

"""
Unit tests for confluenceclient.
"""

import pytest
from jira2confluencegantt.confluenceclient import ConfluenceClient


def test_create_confluence_client_with_empty_url() -> None:
    """
    Confluence client creation with invalid url must raise an exception.
    """
    with pytest.raises(Exception):
        ConfluenceClient("", "user", "pass")


def test_create_confluence_client_with_empty_username() -> None:
    """
    Confluence client creation with invalid username must raise an exception.
    """
    with pytest.raises(Exception):
        ConfluenceClient("http://test", "", "pass")


def test_create_confluence_client_with_empty_password() -> None:
    """
    Confluence client creation with invalid password must raise an exception.
    """
    with pytest.raises(Exception):
        ConfluenceClient("http://test", "user", "")
