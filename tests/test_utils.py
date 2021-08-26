#! python3

"""
Unit tests for utils.
"""

import pytest
from jira2confluencegantt.utils import keys_exists


def test_keys_exists_without_dict_type() -> None:
    """
    Key exists function called without a dictionary must raise an exception.
    """
    with pytest.raises(Exception):
        keys_exists(None, "Key")


def test_keys_exists_without_keys() -> None:
    """
    Key exists function called without keys must raise an exception.
    """
    with pytest.raises(Exception):
        keys_exists({})


def test_keys_exists_with_key_searched() -> None:
    """
    Key exists function called with key searched must return True.
    """
    assert keys_exists({"Key": "Value"}, "Key")


def test_keys_exists_without_key_searched() -> None:
    """
    Key exists function called without key searched must return False.
    """
    assert not keys_exists({"Key": "Value"}, "New key")


def test_keys_exists_with_nested_key_searched() -> None:
    """
    Key exists function called with nested key searched must return True.
    """
    assert keys_exists({"Key": {"Nested key": "Value"}}, "Key", "Nested key")


def test_keys_exists_without_nested_key_searched() -> None:
    """
    Key exists function called without nested key searched must return False.
    """
    assert not keys_exists(
        {"Key": {"Nested key": "Value"}}, "Key", "New nested key"
    )


def test_keys_exists_without_complete_nested_key_searched() -> None:
    """
    Key exists function called without key/nested key searched must return
    False.
    """
    assert not keys_exists({"Key": {"Nested key": "Value"}}, "Nested key")
