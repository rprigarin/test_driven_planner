"""Set up MongoDB access and manage queries related to planner tasks."""

import os
from enum import Enum
from datetime import date
from json import load, JSONDecodeError

from pymongo import MongoClient, Database, Collection
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
    BAD_TASK = -1
    DUPLICATE_TASK_FOUND = -2
    INSERT_FAILED = -3


class PlannerTask:
    description: str
    active_date: date
    init_code: InitCode

    def __init__(self, desc, date_params):
        try:
            self.description = desc
            self.active_date = date(
                date_params["year"], date_params["month"], date_params["day"]
            )
            self._validate()
        except Exception as _e:
            self.init_code = InitCode.FAIL

    def _validate(self):
        if type(self.description) is not str:
            self.init_code = InitCode.FAIL
            return

        self.init_code = InitCode.OK

    def get_init_code(self):
        return self.init_code

    def is_valid(self):
        return self.init_code == InitCode.OK


class PlannerAccess:
    """A class for accessing MongoDB and performing planner-related operations."""

    def __init__(self, db_name="planner_db", col_name="planner_col"):

        # Parameters
        # - config file
        self.config: dict

        # - MongoDB session
        self.client: MongoClient
        self.planner_db: Database
        self.planner_col: Collection
        self.db_name = db_name
        self.col_name = col_name

        # - Codes
        self.init_code: InitCode
        self.query_code: QueryCode

        # Initialization
        if self.load_config() == InitCode.OK and self.connect() == InitCode.OK:
            self.init_code = InitCode.OK
        else:
            self.init_code = InitCode.FAIL

        self.query_code = QueryCode.OK

    def load_config(self):
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

    def connect(self):
        """Initialize the MongoDB client and attempt connection based on configuration."""

        # Assign config parameters
        try:
            self.client = MongoClient(
                self.config["uri"], serverSelectionTimeoutMS=self.config["timeout_ms"]
            )
        except TypeError:
            return InitCode.BAD_CONFIG

        # Check connection
        try:
            val = self.client.admin.command("ping")
            if val["ok"] != 1.0:
                return InitCode.DATABASE_UNREACHABLE
        except errors.ServerSelectionTimeoutError:
            return InitCode.DATABASE_UNREACHABLE

        # Create database and collection objects
        self.planner_db = self.client[self.db_name]
        self.planner_col = self.planner_db[self.col_name]

        return InitCode.OK

    def disconnect(self):
        self.client.close()

    def get_initialization_code(self):
        """Confirm whether planner access initialized properly using the init_code flag."""

        return self.init_code

    def get_query_code(self):
        return self.query_code

    def duplicate_exists(self, task: PlannerTask):
        result = self.planner_col.find_one(
            {
                "task_desc": task.description,
                "date": f"{task.active_date.year}-{task.active_date.month}-{task.active_date.day}",
            }
        )

        if result is not None:
            return True
        else:
            return False

    def insert(self, task: PlannerTask):
        if not task.is_valid():
            self.query_code = QueryCode.BAD_TASK
            return

        if self.duplicate_exists(task):
            self.query_code = QueryCode.DUPLICATE_TASK_FOUND
            return

        result = self.planner_col.insert_one(
            {
                "task_desc": task.description,
                "date": f"{task.active_date.year}-{task.active_date.month}-{task.active_date.day}",
            }
        )

        if result is not None:
            self.query_code = QueryCode.OK
        else:
            self.query_code = QueryCode.INSERT_FAILED

    def clear_planner(self):
        _result = self.planner_col.delete_many({})

    def drop_planner(self):
        _result = self.client.drop_database(self.planner_db)
