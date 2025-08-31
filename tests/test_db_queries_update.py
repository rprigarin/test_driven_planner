"""Tests for task update queries."""

from datetime import date

import pytest

from planner.db_access import PlannerAccess, PlannerTask
from planner.db_access import QueryCode

# ________________________________________________________________________________


@pytest.fixture()
def planner_access():
    """General-purpose planner access for updating added tasks."""

    planner = PlannerAccess("test_planner_db_general", "test_planner_col_general")

    yield planner


@pytest.fixture()
def task_update_pair():
    """A tuple consisting of an initial task and an update task."""

    return {
        "task": PlannerTask(
            "go shopping", {"year": date.today().year + 1, "month": 1, "day": 1}
        ),
        "update": PlannerTask(
            "go shopping (remember to buy apples)",
            {"year": date.today().year + 1, "month": 1, "day": 2},
        ),
    }


@pytest.fixture()
def some_task():
    """An active task."""

    return PlannerTask(
        "some task", {"year": date.today().year + 1, "month": 1, "day": 1}
    )


# ________________________________________________________________________________


@pytest.mark.skip
def test_planner_updates_task_by_ID(planner_access, task_update_pair):
    """Identify a task by ID for an update."""

    planner_access.clear_planner()
    task_id = -1

    planner_access.insert(task_update_pair["task"])
    task_id = planner_access.get_id(task_update_pair["task"])
    planner_access.update(task_id, task_update_pair["update"])

    assert planner_access.count_tasks() == 1
    assert planner_access.list_tasks()[0] == task_update_pair["update"]


@pytest.mark.skip
def test_planner_updates_task_by_plannertask_object(planner_access):
    """Use contents of a PlannerTask object to update a task.

    NOTE: PlannerTask cannot uniquely identify a task in a database. After a successful update,
    the same PlannerTask object cannot be used to find it, since the contents of the remote
    task have been updated. Identifying tasks by ID can be useful when this side effect
    is not desirable."""

    planner_access.clear_planner()

    planner_access.insert(task_update_pair["task"])
    planner_access.update(task_update_pair["task"], task_update_pair["update"])

    assert planner_access.count_tasks() == 1
    assert planner_access.list_tasks()[0] == task_update_pair["update"]


@pytest.mark.skip
def test_updating_non_existing_task_does_nothing(planner_access):
    """Update query on an undefined task does not modify the planner.
    An appropriate query code is set when a task is not found."""
    pass


@pytest.mark.skip
@pytest.mark.parametrize(
    "bad_update",
    [
        PlannerTask("some task?", {"year": 0, "month": 0, "day": 0}),
        PlannerTask("some task?", {}),
        PlannerTask(100000, {"year": date.today().year + 1, "month": 1, "day": 1}),
        PlannerTask("some task?", {"day": 22}),
    ],
)
def test_planner_refuses_to_update_task(planner_access, some_task, bad_update):
    """A malformed PlannerTask will not be processed by PlannerAccess."""

    planner_access.clear_planner()
    planner_access.insert(some_task)
    id = planner_access.get_id(some_task)
    planner_access.update(id, bad_update)

    assert planner_access.get_query_code == QueryCode.BAD_UPDATE
    assert planner_access.get_task(id) == some_task
    assert planner_access.get_task(id) != bad_update
