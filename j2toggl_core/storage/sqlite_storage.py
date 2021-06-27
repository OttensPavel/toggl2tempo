import sqlite3

from typing import Optional

from j2toggl_core.app_paths import get_app_file_path
from j2toggl_core.storage.storage import StorageBase
from j2toggl_core.worklog import WorkLog

DATABASE_FILE_NAME = "toggl-sync.db"


class SqliteStorage(StorageBase):
    # TODO: replace errors with more suitable!!!

    __database_init_script = '''CREATE TABLE sync_key
                                (
                                    master_key integer NOT NULL,                                    
                                    second_key integer NOT NULL,
                                    CONSTRAINT pk_sync_key PRIMARY KEY (master_key, second_key),
                                    CONSTRAINT unique_master_key UNIQUE (master_key),
                                    CONSTRAINT unique_second_key UNIQUE (second_key)
                                )'''

    def __init__(self):
        self._conn = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._conn:
            self._conn.close()
            self._conn = None

    def open(self):
        storage_path = get_app_file_path(DATABASE_FILE_NAME)

        db_exists = storage_path.exists() and storage_path.is_file()
        self._conn = sqlite3.connect(str(storage_path))

        if not db_exists:
            self._conn.execute(self.__database_init_script)
            self._conn.commit()

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def add(self, worklog: WorkLog):
        if worklog.master_id is None or worklog.second_id is None:
            raise TypeError()

        self._conn.execute('''INSERT INTO sync_key (master_key, second_key) VALUES (?, ?)''',
                           (worklog.master_id, worklog.second_id))
        self._conn.commit()

    def get_second_id(self, master_id: int) -> Optional[int]:
        cur = self._conn.cursor()
        cur.execute("SELECT second_key FROM sync_key WHERE master_key = ?", (master_id,))
        result = cur.fetchone()

        if result is not None:
            return result[0]

        return None

    def get_master_id(self, second_id: int) -> Optional[int]:
        cur = self._conn.cursor()
        cur.execute("SELECT master_key FROM sync_key WHERE second_key = ?", (second_id,))
        result = cur.fetchone()

        if result is not None:
            return result[0]

        return None

    def delete(self, worklog: WorkLog):
        cur = self._conn.cursor()
        cur.execute("DELETE FROM sync_key WHERE master_key = ? AND second_key = ?",
                    (worklog.master_id, worklog.second_id,))
