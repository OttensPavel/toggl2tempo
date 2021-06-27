from pathlib import Path
from shutil import copy

from j2toggl_core.app_paths import get_app_directory_path
from j2toggl_core.configuration.json_config import CONFIG_FILE_NAME, JsonConfig
from j2toggl_core.storage.sqlite_storage import DATABASE_FILE_NAME


class ImportManager:
    def __init__(self, source_path: str):
        self.source_path = source_path

    def import_artifacts(self):
        directory_path = Path(self.source_path)

        db_file_path = directory_path.joinpath(DATABASE_FILE_NAME)
        config_file_path = directory_path.joinpath(CONFIG_FILE_NAME)

        if not db_file_path.exists() or not db_file_path.is_file():
            raise IOError(f"DB file '{db_file_path}' doesn't exists")

        if not config_file_path.exists() or not config_file_path.is_file():
            raise IOError(f"Config file '{config_file_path}' doesn't exists")

        target_path = get_app_directory_path()
        if not target_path.exists():
            target_path.mkdir()

        copy(db_file_path, target_path)
        copy(config_file_path, target_path)

    @staticmethod
    def configuration_exists() -> bool:
        configuration_path = get_app_directory_path()
        db_file_path = configuration_path.joinpath(DATABASE_FILE_NAME)
        config_file_path = configuration_path.joinpath(CONFIG_FILE_NAME)

        return db_file_path.exists() or config_file_path.exists()

    @staticmethod
    def validate(source_path_str: str) -> (bool, str):
        if source_path_str is None or len(source_path_str) == 0:
            return False, None

        source_path = Path(source_path_str)
        source_db_file_path = source_path.joinpath(DATABASE_FILE_NAME)
        source_config_file_path = source_path.joinpath(CONFIG_FILE_NAME)

        if not source_db_file_path.exists() or not source_config_file_path.exists():
            return False, f"The directory should contain two files: '{CONFIG_FILE_NAME}' and '{DATABASE_FILE_NAME}'."

        config = JsonConfig(directory_path=source_path)
        isValid, errorMsg = config.validate()
        if not isValid:
            return False, errorMsg

        return True, None
