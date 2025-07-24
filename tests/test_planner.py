"""Test how the planner puts everything together to deliver a working planner."""

import unittest

# ________________________________________________________________________________


class TestPlanner(unittest.TestCase):
    def test_incomplete_planner_initialisation(self):
        """No dependencies should be left uninitialised when running the planner."""
        self.fail("Not implemented")

    def test_no_db_connection_transitions_to_offline(self):
        """Planner should smoothly transition to offline mode if the database stops working."""
        self.fail("Not implemented")

    def test_uninitialised_parser_refuses_operation(self):
        """Uninitialised parser should not process anything."""
        self.fail("Not implemented")
