"""Tests for task insertion queries."""

import pytest

from planner.db_access import PlannerAccess, PlannerTask
from planner.db_access import QueryCode

# ________________________________________________________________________________


@pytest.fixture()
def planner_access():
    """General-purpose planner access for insertion queries."""

    planner = PlannerAccess("test_planner_db_general", "test_planner_col_general")
    yield planner

    # Cleanup
    planner.drop_planner()
    planner.disconnect()


# ________________________________________________________________________________


@pytest.mark.parametrize(
    "task_params",
    [
        {"task_desc": "some task", "date": {"year": 2025, "month": 12, "day": 30}},
    ],
)
def test_planner_inserts_task(planner_access, task_params):
    """PlannerAccess uses a PlannerTask object for inserting queries.
    Success of the operation can be checked by viewing the query code."""

    planner_access.clear_planner()

    planner_access.insert(PlannerTask(task_params["task_desc"], task_params["date"]))

    assert planner_access.get_query_code() == QueryCode.OK


@pytest.mark.parametrize(
    "bad_task_params",
    [
        {"task_desc": "some task", "date": {}},
        {"task_desc": 1, "date": {"year": 2025, "month": 12, "day": 30}},
    ],
)
def test_planner_does_not_insert_bad_task(planner_access, bad_task_params):
    """If there is a problem with the PlannerTask object, PlannerAccess does not add it to the planner."""

    planner_access.clear_planner()

    planner_access.insert(
        PlannerTask(bad_task_params["task_desc"], bad_task_params["date"])
    )

    assert planner_access.get_query_code() == QueryCode.BAD_TASK


def test_planner_does_not_insert_duplicate_task(planner_access):
    """PlannerAccess checks if the task with the same contents (description and date) is already present in the planner.
    If so, the operation fails with an appropriate query code."""

    planner_access.clear_planner()
    first_task = PlannerTask(
        "start new year with a blast", {"year": 2026, "month": 1, "day": 1}
    )
    second_task = PlannerTask(
        "start new year with a blast", {"year": 2026, "month": 1, "day": 1}
    )

    planner_access.insert(first_task)
    planner_access.insert(second_task)

    assert planner_access.get_query_code() == QueryCode.DUPLICATE_TASK_FOUND
