#!/usr/bin/env python3

import re

from j2toggl_core.worklog_state import WorkLogState


class WorkLog:

    def __init__(self):
        self.state = WorkLogState.Unknown

        self.master_id = None
        self.second_id = None
        self.key = None
        self.activity = None

        self.project = None
        self.description = None
        self.startTime = None
        self.endTime = None
        self.duration = None
        self.tags = None

        self.tooltip = None

    @property
    def is_invalid(self):
        result = self.key is None \
            or self.project is None \
            or self.activity is None \
            or self.description is None \
            or self.duration <= 0

        return result
