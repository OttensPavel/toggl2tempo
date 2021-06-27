import json
from pathlib import Path

import jsonschema
import os

from loguru import logger

from j2toggl_core.app_paths import get_user_file_path
from j2toggl_core.configuration.config import Config

CONFIG_FILE_NAME = "app-config.json"


class JsonConfig(Config):
    # See http://json-schema.org/latest/json-schema-validation.html to update schema
    _configSchema = {
        "type": "object",
        "properties": {
            "application": {
                "type": "object",
                "properties": {
                    "firstDateOfWeek": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 7
                    }
                }
            },
            "jira": {
                "type": "object",
                "properties": {
                    "host": {"type": "string"},
                    "user": {"type": "string"},
                    "token": {"type": "string"},
                }
            },
            "tempo": {
                "type": "object",
                "properties": {
                    "token": {"type": "string"},
                }
            },
            "toggl": {
                "type": "object",
                "properties": {
                    "user_agent": {"type": "string"},
                    "token": {"type": "string"},
                }
            },
        },
    }

    def load(self):
        appdata_directory_path = os.getenv('APPDATA')
        if not appdata_directory_path:
            raise IOError("Can't find APPDATA env variable")

        config_path = get_user_file_path(CONFIG_FILE_NAME)

        logger.info(f"Load config from '{config_path}'")

        # Load config from file
        if config_path.exists() and config_path.is_file():
            with config_path.open() as config_file:
                data = json.load(config_file)
        else:
            raise IOError("Can't find config file: {0}".format(config_path))

        # Validate by JSON schema
        jsonschema.validate(data, self._configSchema)

        # Load settings
        if data is not None:
            # Application settings
            self.first_date_of_week = data["application"]["firstDateOfWeek"]

            # Jira settings
            self.jira.host = data["jira"]["host"]
            self.jira.user = data["jira"]["user"]
            self.jira.token = data["jira"]["token"]

            # Tempo settings
            self.tempo.token = data["tempo"]["token"]

            # Toggl settings
            self.toggl.token = data["toggl"]["token"]
            self.toggl.user_agent = data["toggl"]["user_agent"]
