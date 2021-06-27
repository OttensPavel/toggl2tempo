from typing import List

from PyQt5.QtCore import QDate, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDateEdit
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QStatusBar
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout

from j2toggl_core.configuration.config import Config
from j2toggl_core.sync_manager import SyncManager
from j2toggl_core.worklog import WorkLog
from j2toggl_ui.sync_thread import SyncThread
from j2toggl_ui.worklogs_table_widget import WorkLogsTableWidget

WorkLogCollection = List[WorkLog]


class MainWindow(QWidget):
    def __init__(self, config: Config):
        super().__init__()

        self.config = config

        self._sync_manager = SyncManager(config)
        self._sync_thread = SyncThread(self._sync_manager)

        self._init_ui()
        self._init_signals()
        self._init_data()

    def _init_ui(self):
        self._init_widgets()
        self._init_layouts()

        self.setWindowTitle('TogglSync')
        self.setWindowIcon(QIcon(':app-icon'))
        self.setGeometry(400, 400, 800, 480)

    def _init_widgets(self):
        self.sync_button = QPushButton("Sync")
        self.load_button = QPushButton("Only load")

        self.startDatePicker = QDateEdit()
        self.startDatePicker.setCalendarPopup(True)
        self.startDatePicker.setDisplayFormat("dd.MM.yyyy")
        self.startDatePicker.calendarWidget().setFirstDayOfWeek(self.config.first_date_of_week)

        self.endDatePicker = QDateEdit()
        self.endDatePicker.setCalendarPopup(True)
        self.endDatePicker.setDisplayFormat("dd.MM.yyyy")
        self.endDatePicker.calendarWidget().setFirstDayOfWeek(self.config.first_date_of_week)

        self.wlList = WorkLogsTableWidget()

        self.statusBar = QStatusBar()

    def _init_layouts(self):
        # Period selection part
        datesHBox = QHBoxLayout()
        datesHBox.addWidget(QLabel("Period to sync: "))
        datesHBox.addWidget(self.startDatePicker)
        datesHBox.addWidget(self.endDatePicker)

        mainVBox = QVBoxLayout()
        mainVBox.addLayout(datesHBox)

        # Worklog table
        mainVBox.addWidget(self.wlList)

        # Buttons
        buttonsHBox = QHBoxLayout()
        buttonsHBox.addStretch(1)
        buttonsHBox.addWidget(self.load_button)
        buttonsHBox.addWidget(self.sync_button)
        mainVBox.addLayout(buttonsHBox)

        # Status bar
        mainVBox.addWidget(self.statusBar)

        self.setLayout(mainVBox)

    def _init_signals(self):
        # UI
        self.sync_button.clicked.connect(self._on_sync_click)
        self.load_button.clicked.connect(self._on_load_click)

        # Thread events
        self._sync_thread.started.connect(self.on_sync_start)
        self._sync_thread.finished.connect(self.on_sync_finished)

        # Sync process events
        self._sync_manager.showMessage.connect(self.show_warning)
        self._sync_manager.showWorklogList.connect(self.update_worklog_list)
        self._sync_manager.changeStatus.connect(self.change_status)

    def _init_data(self):
        now = QDate.currentDate()
        self.startDatePicker.setDate(now)
        self.endDatePicker.setDate(now)
        self.statusBar.showMessage("Ready to sync.")

    def _on_sync_click(self):
        start_date = self.startDatePicker.date().toPyDate()
        end_date = self.endDatePicker.date().toPyDate()

        if start_date > end_date:
            self.show_warning("Can't start sync", "Start date shouldn't be less than end date")
            return

        self._sync_thread.set_parameters(start_date, end_date)
        self._sync_thread.start()

    def _on_load_click(self):
        start_date = self.startDatePicker.date().toPyDate()
        end_date = self.endDatePicker.date().toPyDate()

        if start_date > end_date:
            self.show_warning("Can't start sync", "Start date shouldn't be less than end date")
            return

        self._sync_thread.set_parameters(start_date, end_date, True)
        self._sync_thread.start()

    @pyqtSlot(str)
    def change_status(self, msg: str):
        self.statusBar.showMessage(msg)

    @pyqtSlot(str, str, str)
    def show_warning(self, title: str, msg: str, details: str = None):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setWindowTitle(title)
        msgBox.setText(msg)
        msgBox.setDetailedText(details)
        msgBox.exec()

    @pyqtSlot()
    def on_sync_start(self):
        self.setDisabled(True)

    @pyqtSlot()
    def on_sync_finished(self):
        self.setDisabled(False)

    @pyqtSlot(list)
    def update_worklog_list(self, worklogs: WorkLogCollection):
        self.wlList.init_data(worklogs)
