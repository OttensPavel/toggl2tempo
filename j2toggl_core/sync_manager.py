from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from loguru import logger

from j2toggl_core.exceptions.SyncException import SyncException
from j2toggl_core.configuration.config import Config
from j2toggl_core.utils.datetime_utils import *
from j2toggl_core.storage.sqlite_storage import SqliteStorage
from j2toggl_core.tempo_api_client import TempoClient
from j2toggl_core.toggl_api_client import TogglClient
from j2toggl_core.worklog import WorkLog
from typing import List

from j2toggl_core.worklog_state import WorkLogState

WorkLogCollection = List[WorkLog]


class SyncManager(QObject):
    changeStatus = pyqtSignal(str)
    showMessage = pyqtSignal(str, str, str)
    showWorklogList = pyqtSignal(list)

    def __init__(self, config: Config):
        super().__init__()

        self.config = config
        self.toggl_client = TogglClient(self.config.toggl)
        self.tempo_client = TempoClient(self.config.jira, self.config.tempo)

        # Init storage
        self.storage = SqliteStorage()
        self.storage.open()
        self.storage.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.storage.close()

    def sync(self, start_date: date, end_date: date, only_load: bool):
        if not self._login():
            return False

        start_datetime = date2datetime(start_date)
        end_datetime = date2datetime(end_date)

        try:
            self.changeStatus.emit("Load worklogs from Tempo...")
            worklogs_from_tempo = self.tempo_client.get_worklogs(start_datetime, end_datetime)

            self.changeStatus.emit("Load worklogs from Toggl...")
            worklogs_from_toggl = self.toggl_client.get_detailed_report(start_datetime, end_datetime)

            # TODO: Add prepare search by issue keys to check that all tasks exist
            self._calculate_worklogs_statuses(
                toggl_worklogs=worklogs_from_toggl,
                tempo_worklogs=worklogs_from_tempo)

            self.showWorklogList.emit(worklogs_from_toggl)

            if only_load:
                self.changeStatus.emit("Load completed.")
                return False

            self._sync_impl(worklogs_from_toggl)
        except SyncException as sync_exception:
            error_message = f"Sync error occurred: {sync_exception.message}."
            logger.error(error_message)
            self.changeStatus.emit(error_message)
            return False

        return True

    def _login(self):
        # Login Toggl
        self.changeStatus.emit("Toggl authentication...")
        self.toggl_client.login()

        # Login JIRA Tempo
        self.changeStatus.emit("JIRA authentication...")
        if not self.tempo_client.login():
            self.changeStatus.emit("Sorry, authentication failed. Please check log for more details.")
            return False

        return True

    def _calculate_worklogs_statuses(self, toggl_worklogs: WorkLogCollection, tempo_worklogs: WorkLogCollection):
        has_incomplete_worklog = False

        self.storage.open()

        for toggl in toggl_worklogs:
            if toggl.is_invalid:
                toggl.state = WorkLogState.Incomplete
                has_incomplete_worklog = True
            else:
                second_id = self.storage.get_second_id(toggl.master_id)
                if second_id is not None:
                    toggl.second_id = second_id

                    tempo = next((x for x in tempo_worklogs if x.second_id == second_id), None)
                    if tempo is None:
                        raise SyncException(f"Tempo worklog [TempoId={second_id}] doesn't exists")

                    if self._worklog_was_moved(toggl, tempo):
                        toggl.state = WorkLogState.Moved
                    elif self._worklog_was_updated(toggl, tempo):
                        toggl.state = WorkLogState.Updated
                    else:
                        toggl.state = WorkLogState.Synced
                else:
                    toggl.state = WorkLogState.New

        self.storage.close()

        return has_incomplete_worklog

    @staticmethod
    def _worklog_was_moved(toggl: WorkLog, tempo: WorkLog):
        is_moved = False
        description_of_changes = ""

        if tempo.key != toggl.key:
            is_moved = True
            description_of_changes += "Task key was changed: {0} -> {1}\r\n".format(tempo.key, toggl.key)

        if is_moved:
            toggl.tooltip = description_of_changes

        return is_moved

    @staticmethod
    def _worklog_was_updated(toggl: WorkLog, tempo: WorkLog):
        is_updated = False
        description_of_changes = ""

        if tempo.activity != toggl.activity:
            is_updated = True
            description_of_changes += "Activity: {0} -> {1}\r\n".format(tempo.activity, toggl.activity)
        if tempo.startTime != toggl.startTime:
            is_updated = True
            description_of_changes += "Start time: {0} -> {1}\r\n".format(tempo.startTime, toggl.startTime)
        if tempo.duration != toggl.duration:
            is_updated = True
            description_of_changes += "Duration: {0} -> {1}\r\n".format(tempo.duration, toggl.duration)
        if tempo.description != toggl.description:
            is_updated = True
            description_of_changes += "Description: {0} -> {1}\r\n".format(tempo.description, toggl.description)

        if is_updated:
            toggl.tooltip = description_of_changes

        return is_updated

    def _sync_impl(self, worklogs: WorkLogCollection):
        self.changeStatus.emit("Sync in process...")

        total_count = worklogs.__len__()
        progress_counter = 0
        counter = {
            "added": 0,
            "updated": 0,
            "skipped": 0,
            "failed": 0
        }

        self.storage.open()

        for wl in worklogs:
            self.changeStatus.emit("Progress: syncing {current}/{total}"
                                   .format(current=progress_counter, total=total_count))

            if wl.state == WorkLogState.New:
                if self.tempo_client.add_worklog(wl):
                    self.storage.add(wl)
                    counter["added"] += 1
                else:
                    counter["failed"] += 1
            elif wl.state == WorkLogState.Moved:
                # Delete from Tempo
                if not self.tempo_client.delete_worklog(wl):
                    # TODO: Add exception raising and handling
                    continue

                # Delete from DB
                self.storage.delete(wl)
                wl.second_id = None

                # Upload again
                if self.tempo_client.add_worklog(wl):
                    self.storage.add(wl)
                    counter["updated"] += 1
            elif wl.state == WorkLogState.Updated:
                if self.tempo_client.update_worklog(wl):
                    counter["updated"] += 1
                else:
                    counter["failed"] += 1
            else:
                counter["skipped"] += 1

            progress_counter += 1

        self.storage.close()

        self.changeStatus.emit("Result: added {added}/{total_count},"
                               " updated {updated}/{total_count},"
                               " skipped {skipped}/{total_count},"
                               " failed: {failed}/{total_count}."
                               .format(total_count=total_count,
                                       added=counter["added"],
                                       updated=counter["updated"],
                                       skipped=counter["skipped"],
                                       failed=counter["failed"]))
