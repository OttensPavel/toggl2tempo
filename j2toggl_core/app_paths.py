import os
import platform

from pathlib import Path


def get_app_directory_path() -> Path:
    if platform.system().lower() == "windows":
        home_dir = os.getenv('APPDATA')
        if not home_dir:
            raise KeyError("Can't find 'APPDATA' env variable")
    else:
        raise OSError(f"Sorry, {platform.system()} isn't supported.")

    return Path(home_dir).joinpath("toggl2tempo")


def get_app_file_path(file_path: str) -> Path:
    app_dir = get_app_directory_path()

    return app_dir.joinpath(file_path)
