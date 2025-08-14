"""Ensure consistent behaviour when attempting MongoClient connections."""

import pytest

from pymongo import MongoClient
from pymongo import errors

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
    """Test addresses that MongoClient can initialise with but whose connection guarantees failure."""

    timeout_ms = 2000  # NOTE: may require a different value depending on network conditions
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
    """The appropriate MongoDB protocol must be used for connection."""

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
