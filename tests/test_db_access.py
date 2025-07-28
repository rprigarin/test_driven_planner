"""Ensure consistent MongoDB access behaviours and check for query validity."""

import pytest
from pymongo import MongoClient
from pymongo import errors

from planner.db_access import validate_task_query_fields

# ________________________________________________________________________________


@pytest.mark.parametrize(
    "broken_address",
    [
        "mongodb://ABC_bogus_address_EFG:27017/",   # hostname assumed to not exist
        "mongodb://localhost:1/",                   # well-known port
        "mongodb://local•host:27017/",              # strange hostnames
        "mongodb://$$$$:27017/",
        "♦♣♠",                                      # completely irrational address
        "123",
    ],
)
def test_bad_address_connection(broken_address):
    """Test addresses that MongoClient can initialise with but whose connection is guaranteed to fail."""

    wait_time_ms = 2000
    client = MongoClient(broken_address, serverSelectionTimeoutMS=wait_time_ms)

    with pytest.raises(errors.ConnectionFailure):
        client.admin.command("ping")

    # Need to shut down connection afterwards
    client.close()


@pytest.mark.parametrize(
    "broken_address", ["bogusprotocol://localhost:27017/", "https://localhost:27017/"]
)
def test_invalid_URI(broken_address):
    """MongoClient does not like addresses not starting with mongodb://"""

    with pytest.raises(errors.InvalidURI):
        client = MongoClient(broken_address)


@pytest.mark.parametrize(
    "broken_address",
    [
        "mongodb://localhost:strange_port/",    # non-numeric port
        "mongodb://localhost:☺/",               # alt codes in port
        "mongodb://localhost:123É/",
        "mongodb://localhost:4294967295/",      # port number exceeding range
    ],
)
def test_value_errors_during_connection(broken_address):
    """Non-numerical ports will scare off MongoClient."""

    with pytest.raises(ValueError):
        client = MongoClient(broken_address)


@pytest.mark.parametrize("broken_address", [""])
def test_config_error(broken_address):
    """Empty address is considered a configuration error by MongoClient."""

    with pytest.raises(errors.ConfigurationError):
        client = MongoClient(broken_address)


@pytest.mark.parametrize(
    "task_query", [{"date": "2025-07-25", "task_desc": "my cool task"}]
)
def test_valid_task_query_format(task_query):
    assert validate_task_query_fields(task_query)


@pytest.mark.parametrize(
    "task_query",
    [
        {"daet": "2025-07-25", "task-desc": "my cool task"},    # date typo; - instead of _
        {"date": "2025-07-25"},                                 # task description missing
        {"task_desc": "my cool task"},                          # date missing
        {0: "2025-07-25", 1: "my cool task"},                   # non-string fields
    ],
)
def test_invalid_task_query_format(task_query):
    assert not validate_task_query_fields(task_query)
