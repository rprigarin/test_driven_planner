"""Ensure consistent MongoDB access behaviours and check for query validity."""

import pytest
from pymongo import MongoClient
from pymongo import errors

from planner.db_access import validate_task_query_fields

# ________________________________________________________________________________


@pytest.mark.parametrize(
    "broken_address",
    [
        "mongodb://ABC_bogus_address_EFG:27017/",  # hostname assumed to not exist
        "mongodb://localhost:1/",  # well-known port
        "mongodb://local•host:27017/",  # strange hostnames
        "mongodb://$$$$:27017/",
        "♦♣♠",  # completely irrational address
        "123",
    ],
)
def test_bad_address_connection(broken_address):
    """Test addresses that MongoClient can initialise with but whose connection is guaranteed to fail."""

    wait_time_ms = (
        2000  # must not be zero, else you are not giving enough time to connect
    )
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
        "mongodb://localhost:strange_port/",  # non-numeric port
        "mongodb://localhost:☺/",  # alt codes in port
        "mongodb://localhost:123É/",
        "mongodb://localhost:4294967295/",  # port number exceeding range
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
        {
            "daet": "2025-07-25",
            "task-desc": "my cool task",
        },  # date typo; - instead of _
        {"date": "2025-07-25"},  # task description missing
        {"task_desc": "my cool task"},  # date missing
        {0: "2025-07-25", 1: "my cool task"},  # non-string fields
    ],
)
def test_invalid_task_query_format(task_query):
    assert not validate_task_query_fields(task_query)


def test_planner_access_initialiser():
    """Before connecting to the database, an access object must first be initialised."""

    # Default constructor attempts to read config.json
    planner = PlannerAccess()
    assert planner.get_config_path() == "config.json"

    # Custom config file path can be assigned to a constructor
    planner = PlannerAccess(path="custom_constructor_config.json")
    assert planner.get_config_path() == "custom_constructor_config.json"

    # Can also request config file read using a function
    planner.read_config("config_loaded_from_function.totallyNotJson")
    assert planner.get_config_path() == "config_loaded_from_function.totallyNotJson"


def test_runtime_config_override():
    """Regardless of whether planner access loaded config successfully or not, runtime contents can be overwritten with different values. However, the fields must be valid for this to work.
    Runtime config assignment can be verified with exit codes as follows:

    0 - config dictionary applied successfully
    -1 - issue detected in config dictionary (runtime config left unchanged)"""

    planner = PlannerAccess()
    sample_config = {
        "protocol": "mongodb",
        "hostname": "localhost",
        "port": 27017,
        "timeout_ms": 2000,
    }
    bad_config = {"hi": "how are you doing", "hostname": 12345, "timeout_ms": 0}

    results = [
        planner.assign_runtime_config(sample_config),
        planner.assign_runtime_config(bad_config),
    ]

    assert results[0] == 0 and results[1] == -1

    for i in list(sample_config.keys()):
        assert planner.get_config()[i] == sample_config[i]


def test_config_connection_succeeds_or_times_out():
    """Test the result of constructor I/O. We want to see if the return codes are predictable:

    0 - config file was found and connection was successful
    -1 - config file was found but connection timed out
    -2 - config file was found with one or more bad fields
    -3 - config file was found empty
    -4 - config file was not found"""

    expected_codes = [0, -1, -2, -3, -4]

    planner = PlannerAccess()
    assert planner.get_connection_code() in expected_codes
