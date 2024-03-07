"""Unit tests for confluenceclient."""

import pytest

from jira2confluencegantt.confluenceclient import ConfluenceClient


def test_create_confluence_client_with_empty_url() -> None:
    """Test Confluence client creation with invalid url.

    It must raise an exception.
    """
    with pytest.raises(ValueError, match="Confluence URL is invalid"):
        ConfluenceClient("", "user", "pass")


def test_create_confluence_client_with_empty_username() -> None:
    """Test Confluence client creation with invalid username.

    It must raise an exception.
    """
    with pytest.raises(ValueError, match="Confluence username is invalid"):
        ConfluenceClient("http://test", "", "pass")


def test_create_confluence_client_with_empty_password() -> None:
    """Test Confluence client creation with invalid password.

    It must raise an exception.
    """
    with pytest.raises(ValueError, match="Confluence password is invalid"):
        ConfluenceClient("http://test", "user", "")
