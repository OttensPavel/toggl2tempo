from PyQt5.QtCore import QThread
from datetime import date
from j2toggl_core.sync_manager import SyncManager


class SyncThread(QThread):
    def __init__(self, sync_manager: SyncManager):
        QThread.__init__(self)
        self._sync_manager = sync_manager
        self.start_date = None
        self.end_date = None
        self.only_load = False

    def set_parameters(self, start_date: date, end_date: date, only_load: bool = False):
        self.start_date = start_date
        self.end_date = end_date
        self.only_load = only_load

    def run(self):
        self._sync_manager.sync(self.start_date, self.end_date, self.only_load)
