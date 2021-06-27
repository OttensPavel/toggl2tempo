import os
import platform

from pathlib import Path


def get_user_file_path(file_path: str) -> Path:
    if platform.system().lower() == "windows":
        home_dir = os.getenv('APPDATA')
        if not home_dir:
            raise KeyError("Can't find 'APPDATA' env variable")
    else:
        raise OSError(f"Sorry, {platform.system()} isn't supported.")

    user_file_path = Path(home_dir).joinpath("toggl2tempo", file_path)

    return user_file_path
