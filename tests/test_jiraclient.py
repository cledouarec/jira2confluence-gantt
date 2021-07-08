#! python3

"""
Unit tests for jiraclient.
"""

import pytest
from jira2confluencegantt.jiraclient import JiraClient


def test_create_jira_client_with_empty_url() -> None:
    """
    Jira client creation with invalid url must raise an exception.
    """
    with pytest.raises(Exception):
        JiraClient("", "user", "pass")


def test_create_jira_client_with_empty_username() -> None:
    """
    Jira client creation with invalid url must raise an exception.
    """
    with pytest.raises(Exception):
        JiraClient("http://test", "", "pass")


def test_create_jira_client_with_empty_password() -> None:
    """
    Jira client creation with invalid password must raise an exception.
    """
    with pytest.raises(Exception):
        JiraClient("http://test", "user", "")
