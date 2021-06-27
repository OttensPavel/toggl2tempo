import json
from json import JSONDecodeError
from pathlib import Path

import jsonschema

from jsonschema import ValidationError
from loguru import logger

from j2toggl_core.app_paths import get_app_file_path, get_app_directory_path
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

    def __init__(self, directory_path: Path = None):
        super().__init__()

        if directory_path is not None:
            self.config_path = Path(directory_path).joinpath(CONFIG_FILE_NAME)
        else:
            self.config_path = get_app_file_path(CONFIG_FILE_NAME)

    def exists(self) -> bool:
        return self.config_path.exists()

    def validate(self) -> (bool, str):
        logger.info(f"Validate JSON-config file '{self.config_path}'")

        if not self.config_path.exists():
            return False, f"File '{self.config_path}' does not exist"

        if not self.config_path.is_file():
            return False, f"Path '{self.config_path}' is not file"

        # Load JSON from file
        try:
            with self.config_path.open() as config_file:
                data = json.load(config_file)
        except JSONDecodeError as e:
            return False, f"Failed to read JSON config file: {e}"

        # Validate by JSON schema
        try:
            jsonschema.validate(data, self._configSchema)
        except ValidationError as e:
            return False, f"JSON config is incorrect: {e.message}"

        return True, None

    def load(self):
        config_path = get_app_file_path(CONFIG_FILE_NAME)

        logger.info(f"Load config from '{config_path}'")

        # Load config from file
        data = None
        if config_path.exists() and config_path.is_file():
            with config_path.open() as config_file:
                data = json.load(config_file)

        # Load settings
        if data is not None:
            # Validate by JSON schema
            jsonschema.validate(data, self._configSchema)

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

    def save(self):
        config_dir = get_app_directory_path()
        config_dir.mkdir(exist_ok=True)

        config_path = get_app_file_path(CONFIG_FILE_NAME)

        logger.info(f"Save config to '{config_path}'")

        data = {
            "application": {
                "firstDateOfWeek": self.first_date_of_week,
            },
            "jira": {
                "host": self.jira.host,
                "user": self.jira.user,
                "token": self.jira.token
            },
            "tempo": {
                "token": self.tempo.token,
            },
            "toggl": {
                "user_agent": self.toggl.user_agent,
                "token": self.toggl.token,
            }
        }

        with config_path.open(mode="w") as config_file:
            json.dump(data, config_file, indent=4)
