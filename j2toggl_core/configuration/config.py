from j2toggl_core.configuration.jira_config import JiraConfig
from j2toggl_core.configuration.tempo_config import TempoConfig
from j2toggl_core.configuration.toggl_config import TogglConfig


class Config:

    def __init__(self):
        self.first_date_of_week = 1

        self.jira: JiraConfig = JiraConfig()
        self.toggl: TogglConfig = TogglConfig()
        self.tempo: TempoConfig = TempoConfig()

    def load(self):
        raise NotImplementedError()

    def save(self):
        raise NotImplementedError()

    def exists(self) -> bool:
        raise NotImplementedError()

    def validate(self) -> (bool, str):
        raise NotImplementedError()
