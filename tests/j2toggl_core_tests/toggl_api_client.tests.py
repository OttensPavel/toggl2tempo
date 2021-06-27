import unittest

from datetime import datetime
from parameterized import parameterized

from j2toggl_core.configuration.toggl_config import TogglConfig
from j2toggl_core.toggl_api_client import TogglClient
from j2toggl_core.worklog import WorkLog


class TogglClient_Tests(unittest.TestCase):

    def test_calculate_key_from_desciption_without_dot_after_key_should_return_null_key(self):

        config = TogglConfig()
        client = TogglClient(config)

        worklog = self.create_default_worklog()
        worklog.description = "TEST-001 Development"

        client._calculate_key(worklog)

        self.assertIsNone(worklog.key, "worklog key should be null.")

    def create_default_worklog(self) -> WorkLog:
        wl = WorkLog()
        wl.master_id = 100
        wl.project = "TEST"
        wl.description = "TEST-001. Development."
        wl.startTime = datetime(2020, 10, 29, 17, 15)
        wl.endTime = datetime(2020, 10, 29, 17, 30)
        wl.duration = 15 * 60
        wl.tags = []

        return wl


if __name__ == '__main__':
    unittest.main()
