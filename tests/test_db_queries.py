"""Confirm behaviour of queries for updating task collection in a temporary planner database.

PlannerAccess is a class designed for simple and consistent querying MongoDB for storing planner tasks.

For example, given planner = PlannerAccess(), assuming successful initialization, tasks can be queried as follows:
    planner.insert_task(date, task)
    planner.update_task(date, task, task)
    planner.delete_task(date, task)

Every query returns a QueryCode value for communicating success and failure of most a recent query, accessed by using:
    planner.get_query_code()

"""

from datetime import date

import pytest

from planner.db_access import PlannerAccess
from planner.db_access import InitCode, QueryCode

# ________________________________________________________________________________


@pytest.fixture()
def planner_access():
    """A single PlannerAccess object used for testing queries.
    User can specify database and collection names to use."""

    planner = PlannerAccess("test_planner_db", "test_planner_col")
    yield planner


# ________________________________________________________________________________


def test_expected_initialization_success(planner_access):
    """Successful initialization means two things:
        1. config.json has been found, validated and parsed
        2. connection with MongoDB has been established

    The sum of these two criteria is a single InitCode that determines whether planner access is availale or not.
    """

    assert planner_access.get_initialization_code() == InitCode.OK


@pytest.mark.parametrize(
    "task_query",
    [
        {"date": date(2025, 7, 25), "task_desc": "my cool task"},
        {
            "date": date(2000, 1, 1),
            "task_desc": "The quick brown fox jumps over the lazy dog",
        },
        {
            "date": date(1999, 1, 1),
            "task_desc": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        },
        {"task_desc": "buy 100 cows", "date": date(2030, 6, 30)},
    ],
)
def test_valid_task_format(planner_access, task_query):
    """A task that passess validation has the following structure:
        - exactly two keys with these exact names: 'date' and 'task_desc'
        - 'date' value is of type date (from Python standard library datetime) with valid parameters
        - 'task_desc' value is of type string and is not empty
    """

    assert planner_access.validate_task_query(task_query)


@pytest.mark.parametrize(
    "task_query",
    [
        {"daet": date(2025, 7, 25), "task-desc": "my cool task"},
        {"date": date(2025, 7, 25)},
        {"task_desc": "my cool task"},
        {0: date(2025, 7, 25), 1: "my cool task"},
    ],
)
def test_invalid_task_format_keys(planner_access, task_query):
    """Test tasks with consistently bad keys."""

    assert not planner_access.validate_task_query(task_query)


@pytest.mark.parametrize(
    "task_query",
    [
        {"date": "my cool task?", "task_desc": date(2024, 1, 1)},
        {"date": "2025-01-01", "task_desc": "date is a string"},
        {"date": date(2025, 7, 10), "task_desc": ""},
        {"date": date(2025, 7, 10), "task_desc": 1000},
        {"date": 65535, "task_desc": "buy a calculator"},
        {"date": 65535, "task_desc": 65535},
        {"date": date(2025, 7, 10), "task_desc": ["c", "h", "a", "r"]},
    ],
)
def test_invalid_task_format_values(planner_access, task_query):
    """Test tasks with consistently bad values."""

    assert not planner_access.validate_task_query(task_query)


@pytest.mark.skip()
@pytest.mark.parametrize(
    "query_task",
    [
        {"task_desc": "Buy food for my cat", "date": date(2025, 9, 1)},
        {"task_desc": "Read about general relativity (2 hr)", "date": date(2025, 9, 3)},
        {"task_desc": "Meet up with friends at 6:00 PM", "date": date(2025, 9, 3)},
    ],
)
def test_valid_task_insertion(planner_access, query_task):
    """Test valid task insertion. Requires a date parameter.
    If a task already exists in the database, nothing happens (QueryCode returns UNCHANGED)
    """

    some_valid_date = date(2025, 8, 13)

    planner_access.insert_task(some_valid_date, query_task)

    assert planner_access.get_query_code() == 0


@pytest.mark.skip()
@pytest.mark.parametrize(
    "query_task",
    [
        {"task_desc": "Buy food for my cat", "date": date(2025, 9, 1)},
        {"task_desc": "Read about general relativity (2 hr)", "date": date(2025, 9, 3)},
        {"task_desc": "Meet up with friends at 6:00 PM", "date": date(2025, 9, 3)},
    ],
)
def test_valid_task_deletion(planner_access, query_task):
    """Tasks can be deleted. If a task does not exist, nothing happens (QueryCode == UNCHANGED)."""

    planner_access.delete_task(query_task)
    assert planner_access.get_query_code() == 0


@pytest.mark.skip()
@pytest.mark.parametrize(
    "update_tasks",
    [
        (
            {"task_desc": "Bake 30000 cookies", "date": date(2025, 9, 1)},
            {"task_desc": "Bake 30 cookies", "date": date(2025, 9, 1)},
        ),
        (
            {"ttttt": "+++++++++", "ddddd": date(2025, 10, 1)},
            {"task_desc": "Exercise", "date": date(2025, 10, 1)},
        ),
    ],
)
def test_task_update(planner_access, update_tasks):
    """User should be able to change task contents at any time.
    Task must be in the database, else the operation fails (QueryCode == UPDATE_FAILED).
    """

    codes = {
        'step1_insert': planner_access.insert_task(update_tasks[0]),
        'step2_update': planner_access.update_task(update_tasks[0], update_tasks[1])
    }

    assert codes['step1_insert'] == QueryCode.OK and codes['step2_insert'] == QueryCode.OK


@pytest.mark.skip()
def test_list_no_tasks_present(planner_access):
    """Planner fetches tasks from the database for a particular day.
    Task count can be 0 or some positive integer.

    Things to consider:
    - excessively large number of tasks returned, hindering performance
    - listing returns the right thing"""

    some_date = date(2025, 8, 9)

    # Clear today's tasks
    planner_access.delete_date_tasks(some_date)

    assert planner_access.get_tasks(some_date) == {}


@pytest.mark.skip()
def test_list_task_present(planner_access):
    some_date = date(2025, 8, 9)
    some_task = {"task_desc": "some task", "date": some_date}

    planner_access.delete_date_tasks(some_date)
    planner_access.insert_task(some_task)

    assert planner_access.get_tasks(some_date) is not None


@pytest.mark.skip()
def test_full_cleanup():
    """Upon user's request, PlannerAccess can perform full cleanup by removing the following:
        - all the created tasks
        - task collection used by PlannerAccess
        - task database used by PlannerAccess

    To make sure PlannerAccess can't accidentally attach itself to an unrelated database and delete its contents, certain checks have to be made.
    """

    pass
