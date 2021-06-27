#!/usr/bin/env python3

import datetime
import dateutil.parser
import requests
import urllib.parse

from http import HTTPStatus
from loguru import logger

from j2toggl_core.exceptions.SyncException import SyncException
from j2toggl_core.configuration.jira_config import JiraConfig
from j2toggl_core.configuration.tempo_config import TempoConfig
from j2toggl_core.jira_api_client import JiraClient
from j2toggl_core.worklog import WorkLog
from typing import List

WorkLogCollection = List[WorkLog]


class TempoClient(JiraClient):

    __tempo_legacy_rest_api_url = "https://api.tempo.io/core"
    __PAGE_SIZE = 50

    def __init__(self, jira_config: JiraConfig, tempo_config: TempoConfig):
        JiraClient.__init__(self, jira_config)

        self.__config = tempo_config
        self.__session = requests.Session()

    def login(self) -> bool:
        if not super().login():
            return False

        self.__session.headers["Authorization"] = "Bearer " + self.__config.token

        return True

    def get_worklogs(self, start_date: datetime, end_date: datetime) -> WorkLogCollection:
        method_uri = self.__make_tempo_api_uri(f"worklogs/user/{self._user.account_id}")

        page_index = 0

        tsr_list = []

        while True:
            params = {
                "from": start_date.strftime("%Y-%m-%d"),  # only dates, for instance "2016-12-23"
                "to": end_date.strftime("%Y-%m-%d"),
                "offset": page_index * self.__PAGE_SIZE,
                "limit": self.__PAGE_SIZE
            }

            r = self.__session.get(url=method_uri, params=params)
            if r.status_code != HTTPStatus.OK:
                error_message = "{method_name}: url: {url} status {error_code}, error {error_message}".format(
                    method_name="get_worklogs",
                    url=method_uri,
                    error_code=r.status_code,
                    error_message=r.text)

                logger.error(error_message)
                raise SyncException(error_message)

            report = r.json()

            records_count = report["metadata"]["count"]
            if not isinstance(records_count, int):
                raise SyncException("Page count metadata MUST BE integer")

            worklogs_part = self._load_worklogs_page(report["results"])
            tsr_list.extend(worklogs_part)

            page_index += 1

            if records_count < self.__PAGE_SIZE:
                break

        return tsr_list

    @staticmethod
    def _load_worklogs_page(tempo_worklogs: dict) -> WorkLogCollection:
        tsrs = []

        for tempo_record in tempo_worklogs:
            wl = WorkLog()

            # Common data
            wl.second_id = tempo_record["tempoWorklogId"]
            wl.key = tempo_record["issue"]["key"]
            wl.description = tempo_record["description"]

            # Times
            duration = tempo_record["timeSpentSeconds"]
            start = dateutil.parser.parse(tempo_record["startDate"] + "T" + tempo_record["startTime"])
            end = start + datetime.timedelta(seconds=duration)

            wl.startTime = start
            wl.endTime = end
            wl.duration = duration

            # Attributes
            if tempo_record["attributes"] and tempo_record["attributes"]["values"]:
                attributes = tempo_record["attributes"]["values"]
                activity_attr = next((x for x in attributes if x["key"] == "_Activity_"), None)
                if activity_attr is not None:
                    wl.activity = urllib.parse.unquote(activity_attr["value"])

            tsrs.append(wl)

        return tsrs

    def add_worklog(self, worklog: WorkLog):
        method_uri = self.__make_tempo_api_uri("worklogs")

        data = self.__worklog_to_dict(worklog)
        r = self.__session.post(url=method_uri, json=data)
        if r.status_code == HTTPStatus.OK:
            answer = r.json()
            worklog.second_id = int(answer["tempoWorklogId"])
        else:
            logger.error("{method_name}: url: {url} status {error_code}, error {error_message}"
                         .format(method_name="add_worklog",
                                 url=method_uri,
                                 error_code=r.status_code,
                                 error_message=r.text))
            return False

        return True

    def update_worklog(self, worklog: WorkLog):
        method_uri = self.__make_tempo_api_uri("worklogs/{worklog_id}".format(worklog_id=worklog.second_id))

        data = self.__worklog_to_dict(worklog)
        r = self.__session.put(url=method_uri, json=data)
        if r.status_code == HTTPStatus.OK:
            answer = r.json()
            worklog.second_id = int(answer["tempoWorklogId"])
        else:
            logger.error("{method_name}: url: {url} status {error_code}, error {error_message}"
                         .format(method_name="add_worklog",
                                 url=method_uri,
                                 error_code=r.status_code,
                                 error_message=r.text))
            return False

        return True

    def delete_worklog(self, worklog: WorkLog):
        method_uri = self.__make_tempo_api_uri("worklogs/{worklog_id}".format(worklog_id=worklog.second_id))

        r = self.__session.delete(url=method_uri)
        return r.ok

    def __worklog_to_dict(self, worklog: WorkLog) -> dict:
        data = {
            "issueKey": worklog.key,
            "timeSpentSeconds": worklog.duration,
            "startDate": worklog.startTime.strftime("%Y-%m-%d"),
            "startTime": worklog.startTime.strftime("%H:%M:00"),
            "description": worklog.description,
            "authorAccountId": self._user.account_id,
            "attributes": [
                {
                    "key": "_Activity_",
                    # Tempo still required that attribute names should be encoded
                    "value": urllib.parse.quote(worklog.activity, safe='')
                },
            ],
        }

        return data

    def __make_tempo_api_uri(self, relative_url: str):
        return "{host}/3/{relative_url}".format(
            host=self.__tempo_legacy_rest_api_url,
            relative_url=relative_url)
