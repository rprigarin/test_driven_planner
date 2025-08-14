"""Set up MongoDB access and manage queries related to planner tasks."""

import os
from enum import Enum
from datetime import date
from json import load, JSONDecodeError

from pymongo import MongoClient
from pymongo import errors

# ________________________________________________________________________________


class InitCode(Enum):
    """Return codes for PlannerAccess initialization phase."""

    OK = 0
    FAIL = -1
    DATABASE_UNREACHABLE = -2
    MISSING_CONFIG = -3
    BAD_CONFIG = -4


class QueryCode(Enum):
    """Return codes for PlannerAccess queries."""

    OK = 0
    FORMAT_CHECK_FAILED = -1
    UPDATE_FAILED = -2


class PlannerAccess:
    """A class for accessing MongoDB and performing planner-related operations."""

    def __init__(self, db_name="planner_db", col_name="planner_col"):

        # Parameters
        self.config: dict
        self.client: MongoClient
        self.init_state: int

        self.db_name = db_name
        self.col_name = col_name

        # Initialization
        if self._load_config() == InitCode.OK and self._connect() == InitCode.OK:
            self.init_state = InitCode.OK
        else:
            self.init_state = InitCode.FAIL

    def _load_config(self):
        """Parse config.json to initialize planner access."""

        # Check if config file exists
        if not os.path.exists("config.json"):
            return InitCode.MISSING_CONFIG

        # Read config file
        try:
            with open("config.json", "r") as conf_file:
                try:
                    self.config = load(conf_file)
                except JSONDecodeError as e:
                    print(f"Config exception {e}")
                    return InitCode.BAD_CONFIG

        except FileNotFoundError as e:
            print(f"Config exception {e}")
            return InitCode.MISSING_CONFIG

        return InitCode.OK

    def _connect(self):
        """Initialize the MongoDB client and attempt connection based on configuration."""

        try:
            self.client = MongoClient(
                self.config["uri"], serverSelectionTimeoutMS=self.config["timeout_ms"]
            )
        except TypeError:
            return InitCode.BAD_CONFIG

        try:
            val = self.client.admin.command("ping")
            if val["ok"] != 1.0:
                return InitCode.DATABASE_UNREACHABLE
        except errors.ServerSelectionTimeoutError:
            return InitCode.DATABASE_UNREACHABLE

        return InitCode.OK

    def get_initialization_code(self):
        """Confirm whether planner access initialized properly using the init_state flag."""

        return self.init_state

    def insert_task(self, task):
        pass

    def delete_task(self, task):
        pass

    def update_task(self, task, new_task):
        pass

    def get_tasks(self, date):
        pass

    def delete_date_tasks(self, date):
        pass

    def delete_all_tasks(self):
        pass

    def validate_task_query(self, task_query):
        # If query isn't a dictionary, don't bother
        if type(task_query) is not dict:
            return False

        return self._task_key_check(task_query) and self._task_value_check(task_query)

    def _task_key_check(self, task_query):
        fields = list(task_query.keys())

        # Must have exactly two keys
        if len(fields) != 2:
            return False

        # Keys must be strings
        for f in fields:
            if type(f) is not str:
                return False

        # Correct key names (order does not matter)
        fields = list(task_query.keys())
        return "task_desc" in fields and "date" in fields

    def _task_value_check(self, task_query):
        # String check
        if type(task_query["date"]) is not date:
            return False
        if type(task_query["task_desc"]) is not str:
            return False

        # Task description must not be empty
        if task_query["task_desc"] == "":
            return False

        return True
