#!/usr/bin/env python3

import os
import requests.utils

from http import HTTPStatus
from loguru import logger
from typing import Optional

from j2toggl_core.configuration.jira_config import JiraConfig
from j2toggl_core.domain.jira_issue import JiraIssue


class JiraClient:
    _cookieJarFileName = "jira.cookies"
    _jql_separator = ","

    def __init__(self, config: JiraConfig):
        self.__config = config
        self.__session = requests.Session()
        self._user: Optional[JiraUser] = None

    def login(self) -> bool:
        if self._user is not None:
            return True

        # Basic Authentication with JIRA token
        method_uri = self.__make_api_uri("myself")

        r = self.__session.get(url=method_uri, auth=(self.__config.user, self.__config.token))
        if r.status_code == HTTPStatus.OK:
            self.__session.auth = (self.__config.user, self.__config.token)
            self._user = JiraUser.parse(r.json())
        else:
            logger.error("{0}: status {1}, error {2}".format("Basic Authentication", r.status_code, r.text))
            return False

        return True

    def logout(self):
        if os.path.isfile(self._cookieJarFileName):
            os.unlink(self._cookieJarFileName)

    def search_issue(self, key: str) -> Optional[JiraIssue]:
        method_uri = self.__make_api_uri("issue/{0}".format(key))
        logger.debug("{0}: Request method: {1}".format("search_issue", method_uri))
        r = self.__session.get(url=method_uri)

        if r.status_code != 200:
            logger.error("{0}: status {1}, error {2}".format("search_issue", r.status_code, r.text))
            return None
        else:
            return JiraIssue.parse(r.text)

    def search_issues(self, keys):
        method_uri = self.__make_api_uri("search")
        keys_str = self._jql_separator.join(keys)
        body = dict(
            jql=u"key IN (" + keys_str + ")",
            fields=[
                "key",
                "summary",
                "self"
            ])

        r = self.__session.post(url=method_uri, json=body)
        if r.status_code != 200:
            logger.error("{0}: status {1}, error {2}".format("search_issues", r.status_code, r.text))
            return None

        search_result = r.json()

        for issue in search_result["issues"]:
            yield JiraIssue.parse(issue)

    def __make_api_uri(self, relative_url: str):
        return "{0}/rest/api/3/{1}".format(self.__config.host, relative_url)

    @property
    def get_session(self) -> requests.Session:
        return self.__session


class JiraUser:
    def __init__(self, account_id: str, name: str, email: str):
        self.account_id = account_id
        self.name = name
        self.email = email

    @staticmethod
    def parse(jira_session_data: dict):
        from j2toggl_core.exceptions.SyncException import SyncException
        from j2toggl_core.utils.dictionary_utils import get_first_not_null

        _account_id = jira_session_data.get("accountId")
        _name = get_first_not_null(jira_session_data, "name", "displayName")
        _email = jira_session_data.get("emailAddress")

        if _account_id is None:
            raise SyncException("Couldn't read JIRA account identifier.")

        jira_user = JiraUser(_account_id, _name, _email)

        return jira_user
