"""Tests for task listing queries."""

from datetime import date

import pytest

from planner.db_access import PlannerAccess, PlannerTask
from planner.db_access import QueryCode

# ________________________________________________________________________________


@pytest.fixture()
def planner_access():
    """General-purpose planner access for listing various added tasks."""

    planner = PlannerAccess("test_planner_db_general", "test_planner_col_general")

    yield planner


@pytest.fixture()
def past_future_planner_access():
    """PlannerAccess object specifically for differentiating active task from the stale ones.

    An active task is one that is present today or is set to happen sometime in the future.

    A stale task is one that is set in the past."""

    planner = PlannerAccess(
        "test_planner_db_past_future", "test_planner_col_past_future"
    )
    past_task = PlannerTask(
        "old task", {"year": date.today().year - 1, "month": 1, "day": 1}
    )
    future_task = PlannerTask(
        "future task", {"year": date.today().year + 1, "month": 1, "day": 1}
    )

    planner.insert(past_task)
    planner.insert(future_task)

    yield planner


# ________________________________________________________________________________


@pytest.mark.skip
def test_planner_lists_zero_tasks(planner_access):
    """An empty list will be returned should there be no active tasks present in the planner."""

    planner_access.clear_planner()

    tasks = planner_access.list_tasks()

    assert len(tasks) == 0


@pytest.mark.skip
def test_planner_lists_one_task(planner_access):
    """A list of PlannerTask objects is returned when at least one task is present in the planner."""

    planner_access.clear_planner()
    some_task = PlannerTask("some task", {"year": 2025, "month": 12, "day": 30})

    planner_access.insert(some_task)
    tasks = planner_access.list_tasks()

    assert len(tasks) == 1
    assert type(tasks[0]) is PlannerTask
    assert tasks[0] == some_task


@pytest.mark.skip
def test_planner_lists_multiple_tasks(planner_access):
    """Multiple tasks can be returned from a listing without a particular order."""

    planner_access.clear_planner()
    first_task = PlannerTask("breakfast", {"year": 2025, "month": 12, "day": 30})
    second_task = PlannerTask("lunch", {"year": 2025, "month": 12, "day": 30})
    third_task = PlannerTask("dinner", {"year": 2025, "month": 12, "day": 30})

    planner_access.insert(first_task)
    planner_access.insert(second_task)
    planner_access.insert(third_task)
    tasks = planner_access.list_tasks()

    assert len(tasks) == 3


@pytest.mark.skip
def test_planner_lists_tasks_for_today(planner_access):
    """List tasks for today. The planner's core functionality."""

    planner_access.clear_planner()
    task_A = PlannerTask(
        "task A", {"year": date.today().year - 1, "month": 1, "day": 1}
    )
    task_B = PlannerTask(
        "task B",
        {
            "year": date.today().year,
            "month": date.today().month,
            "day": date.today().day,
        },
    )
    task_C = PlannerTask(
        "task C", {"year": date.today().year + 1, "month": 1, "day": 1}
    )

    planner_access.insert(task_A)
    planner_access.insert(task_B)
    planner_access.insert(task_C)
    tasks = planner_access.list_tasks_today()

    assert len(tasks) == 1
    assert tasks[0] == task_B


@pytest.mark.skip
def test_planner_lists_active_tasks(past_future_planner_access):
    """List active tasks only."""

    tasks = past_future_planner_access.list_tasks()

    assert len(tasks) == 1


@pytest.mark.skip
def test_planner_lists_stale_tasks(past_future_planner_access):
    """List stale tasks only."""

    tasks = past_future_planner_access.list_stale_tasks()

    assert len(tasks) == 1


@pytest.mark.skip
def test_planner_lists_all_tasks(past_future_planner_access):
    """List all tasks."""

    tasks = past_future_planner_access.list_all_tasks()

    assert len(tasks) == 2
