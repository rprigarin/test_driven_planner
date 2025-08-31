"""Tests for task deletion queries."""

from datetime import date

import pytest

from planner.db_access import PlannerAccess, PlannerTask
from planner.db_access import QueryCode

# ________________________________________________________________________________


@pytest.fixture()
def planner_access():
    """General-purpose planner access for deleting added tasks."""

    planner = PlannerAccess("test_planner_db_general", "test_planner_col_general")

    yield planner


@pytest.fixture()
def some_task():
    """An active task."""

    return PlannerTask(
        "some task", {"year": date.today().year + 1, "month": 1, "day": 1}
    )


# ________________________________________________________________________________


@pytest.mark.skip
def test_planner_deletes_task_by_ID(planner_access, some_task):
    """An ID is an integer used to uniquely identify a task for deletion."""

    planner_access.clear_planner()
    task_count_before_deletion = -1
    task_count_after_deletion = -1

    planner_access.insert(some_task)
    task_count_before_deletion = planner_access.count_tasks()

    id_of_interest = planner_access.get_id(some_task)
    planner_access.delete(id_of_interest)
    task_count_after_deletion = planner_access.count_tasks()

    assert task_count_before_deletion == 1 and task_count_after_deletion == 0


@pytest.mark.skip
def test_planner_deletes_task_using_plannertask_object(planner_access, some_task):
    """A PlannerTask object can be used to identify a task for deletion."""

    planner_access.clear_planner()
    task_count_before_deletion = -1
    task_count_after_deletion = -1

    planner_access.insert(some_task)
    task_count_before_deletion = planner_access.count_tasks()

    planner_access.delete(some_task)
    task_count_after_deletion = planner_access.count_tasks()

    assert task_count_before_deletion == 1 and task_count_after_deletion == 0


@pytest.mark.skip
def test_task_not_found_for_delete():
    """If task is not found for deletion, an appropriate query code is set."""
    pass


@pytest.mark.skip
def test_empty_delete_does_not_affect_planner(planner_access):
    """If a task is not found for deletion, the contents of the planner should not be modified."""

    planner_access.clear_planner()
    task_count_before_deletion = -1
    task_count_after_deletion = -1
    various_tasks = [
        # Active
        PlannerTask("task A", {"year": date.today().year + 2, "month": 1, "day": 1}),
        PlannerTask("task B", {"year": date.today().year + 4, "month": 2, "day": 1}),
        PlannerTask("task C", {"year": date.today().year + 6, "month": 3, "day": 1}),
        # Stale
        PlannerTask(
            "exceedingly old task",
            {"year": date.today().year - 200, "month": 1, "day": 1},
        ),
    ]

    for t in various_tasks:
        planner_access.insert(various_tasks)
    task_count_before_deletion = planner_access.count_all_tasks()

    planner_access.delete(
        PlannerTask("non existent task", {"year": 1951, "month": 3, "day": 31})
    )
    task_count_after_deletion = planner_access.count_all_tasks()

    assert task_count_before_deletion == len(
        various_tasks
    ) and task_count_after_deletion == len(various_tasks)


@pytest.mark.skip
def test_planner_deletes_all_stale_tasks(planner_access):
    """After using the planner for a long period of time, it may be desirable to remove stale tasks to reclaim disk space."""
    pass
