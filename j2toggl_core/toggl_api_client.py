#!/usr/bin/env python3

import dateutil.parser
import re
import requests.utils
from datetime import *

from j2toggl_core.configuration.toggl_config import TogglConfig
from j2toggl_core.utils.datetime_utils import *
from j2toggl_core.worklog import WorkLog
from typing import List

WorkLogCollection = List[WorkLog]


class TogglClient:
    _workspace_id = None

    __toggl_url = "https://api.track.toggl.com"

    _jira_key_re = re.compile("\w+-\d+")

    _projects_to_activities_map = {
        "Analysis": "Design/Analysis",
        "BugFixing": "Bugfixing",
        "CodeReview": "Code Review",
        "CR Fixes": "Code Review Fixes",
        "Development": "Development",
        "Estimation": "Estimation",
        "Interview": "Other",
        "Meetings": "Other",
        "Testing": "Testing",
        "Environment Setup": "Environment Setup",
        "Team Activities": "Other"
    }

    def __init__(self, config: TogglConfig):
        self._config = config
        self._session = requests.Session()
        self._session.auth = (self._config.token, "api_token")

    def login(self) -> bool:
        if not self._config.validate():
            return False

        method_uri = self.__make_api_uri("workspaces")
        r = self._session.get(url=method_uri)
        if not r.ok:
            return False

        workspaces = r.json()
        self._workspace_id = workspaces[0]["id"]

        return True

    def get_detailed_report(self, start_date: datetime, end_date: datetime = None) -> WorkLogCollection:
        if end_date is None:
            end_date = start_date

        method_uri = self.__make_reports_api_url("details")
        since = shrink_time(start_date) + timedelta(0, 1)
        until = shrink_time(end_date) + timedelta(1, -1)
        page_number = 0

        tsr_list = []

        while True:
            page_number += 1

            params = {
                'user_agent': self._config.user_agent,
                'workspace_id': self._workspace_id,
                'since': since.isoformat(),
                'until': until.isoformat(),
                'page': page_number,
            }

            r = self._session.get(url=method_uri, params=params)
            report = r.json()

            per_page = report["per_page"]
            total_count = report["total_count"]

            for tr in report["data"]:
                start = dateutil.parser.parse(tr["start"])
                start = start.replace(second=0, microsecond=0, tzinfo=None)

                end = dateutil.parser.parse(tr["end"])
                end = end.replace(second=0, microsecond=0, tzinfo=None)

                wl = WorkLog()
                wl.master_id = tr["id"]
                wl.project = tr["project"]
                wl.description = tr["description"]
                wl.startTime = start
                wl.endTime = end
                wl.duration = tr["dur"] // 1000  # convert to seconds
                wl.tags = tr["tags"]

                self._calculate_key(wl)
                self._calculate_activity(wl)

                tsr_list.append(wl)

            if (per_page * page_number) >= total_count:
                break

        return tsr_list

    def _calculate_key(self, wl: WorkLog):
        # TODO: What occurs if we add more that one tag to worklog?
        key_tag = next((x for x in wl.tags if x.startswith("key_")), None)

        if key_tag is not None:
            dot_index = key_tag.rfind('_')
            if dot_index < 0:
                wl.key = None
                return

            key = key_tag[dot_index+1:]
            if self._key_is_correct(key):
                wl.key = key
            else:
                wl.key = None
        else:
            dot_index = wl.description.find(".")
            if dot_index < 0:
                wl.key = None
                return

            key = wl.description[:dot_index]
            if self._key_is_correct(key):
                wl.key = key
                wl.description = wl.description[dot_index + 1:].strip()
            else:
                wl.key = None

    def _key_is_correct(self, issue_key: str):
        return self._jira_key_re.match(issue_key)

    def _calculate_activity(self, wl: WorkLog):
        if wl.project in self._projects_to_activities_map:
            wl.activity = self._projects_to_activities_map[wl.project]
        elif wl.project is not None:
            wl.activity = "Other"

    def __make_reports_api_url(self, relative_url: str):
        return "{0}/reports/api/v2/{1}".format(self.__toggl_url, relative_url)

    def __make_api_uri(self, relative_url: str):
        return "{0}/api/v9/{1}".format(self.__toggl_url, relative_url)
