"""Ensure consistent behaviour when attempting MongoClient connections."""

import pytest

from pymongo import MongoClient
from pymongo import errors

# ________________________________________________________________________________


@pytest.mark.parametrize(
    "broken_address",
    [
        # Hostname assumed to not exist
        "mongodb://ABC_bogus_address_EFG:27017/",
        # Well-known ports
        "mongodb://localhost:1/",
        "mongodb://localhost:80/",
        # Strange hostnames
        "mongodb://local•host:27017/",
        "mongodb://$$$$:27017/",
        # Completely irrational addresses
        "♦♣♠",
        "123",
    ],
)
def test_bad_address_connection(broken_address):
    """Test addresses that MongoClient can initialise with but whose connection guarantees failure."""

    timeout_ms = (
        1000  # NOTE: may require a different value depending on network conditions
    )
    client = MongoClient(broken_address, serverSelectionTimeoutMS=timeout_ms)

    # Ping the database and expect connection failure
    with pytest.raises(errors.ConnectionFailure):
        client.admin.command("ping")

    # Cleanup
    client.close()


@pytest.mark.parametrize(
    "broken_address", ["bogusprotocol://localhost:27017/", "https://localhost:27017/"]
)
def test_invalid_URI(broken_address):
    """The appropriate MongoDB protocol must be used for connection.

    In other words, the address must typically start with mongodb:// to be considered valid.
    """

    with pytest.raises(errors.InvalidURI):
        client = MongoClient(broken_address)


@pytest.mark.parametrize(
    "broken_address",
    [
        # Negative port number
        "mongodb://localhost:-27017/",
        # Non-numerical port
        "mongodb://localhost:strange_port/",
        # Alt codes in port
        "mongodb://localhost:☺/",
        "mongodb://localhost:123É/",
        # Port number exceeds reasonable range
        "mongodb://localhost:4294967295/",
        "mongodb://localhost:9999999999999/",
    ],
)
def test_value_errors_during_connection(broken_address):
    """Negative and non-numerical ports will scare MongoClient."""

    with pytest.raises(ValueError):
        client = MongoClient(broken_address)


@pytest.mark.parametrize("broken_address", [""])
def test_config_error(broken_address):
    """Empty address is considered a configuration error by MongoClient."""

    with pytest.raises(errors.ConfigurationError):
        client = MongoClient(broken_address)
