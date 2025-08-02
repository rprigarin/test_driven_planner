"""Test how the planner puts everything together to deliver a working planner."""

import pytest

# ________________________________________________________________________________


@pytest.mark.skip()
def test_incomplete_planner_initialisation():
    """No dependencies should be left uninitialised when running the planner."""
    assert False


@pytest.mark.skip()
def test_no_db_connection_transitions_to_offline():
    """Planner should smoothly transition to offline mode if the database stops working."""
    assert False


@pytest.mark.skip()
def test_uninitialised_parser_refuses_operation():
    """Uninitialised parser should not process anything."""
    assert False
