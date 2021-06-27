import os
from typing import Optional

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QComboBox
from PyQt5.uic import loadUi

from j2toggl_ui.resources.resouces import qInitCommonResources
from j2toggl_core.configuration.config import Config


class SettingsWindow(QDialog):
    DayOfWeek = {
        1: 0,
        7: 1,
    }

    def __init__(self, config: Config):
        super().__init__()

        qInitCommonResources()

        self.config = config
        self.config_has_changed = False

        self.firstWeekDayComboBox: Optional[QComboBox] = None

        self.jiraHostLineEdit: Optional[QLineEdit] = None
        self.jiraUserLineEdit: Optional[QLineEdit] = None
        self.jiraTokenLineEdit: Optional[QLineEdit] = None

        self.tempoTokenLineEdit: Optional[QLineEdit] = None

        self.togglHostLineEdit: Optional[QLineEdit] = None
        self.togglUserLineEdit: Optional[QLineEdit] = None
        self.togglTokenLineEdit: Optional[QLineEdit] = None

        self.saveButton: Optional[QPushButton] = None
        self.cancelButton: Optional[QPushButton] = None
        self.applyButton: Optional[QPushButton] = None

        self._load_ui()
        self._init_widgets()
        self._init_signals()

        self._load_config()

        self.setWindowTitle("Settings")
        self.setWindowIcon(QIcon(':app-icon'))

    def _load_ui(self):
        current_path = os.path.dirname(__file__)
        ui_path = os.path.join(current_path, "settings_window.ui")

        loadUi(ui_path, self)

    def _init_widgets(self):
        self.firstWeekDayComboBox.addItem("Monday", 1)
        self.firstWeekDayComboBox.addItem("Sunday", 7)

    def _init_signals(self):
        self.cancelButton.clicked.connect(self._close)
        self.saveButton.clicked.connect(self._save)
        self.applyButton.clicked.connect(self._apply)

    def _load_config(self):
        week_day_index = self.DayOfWeek[self.config.first_date_of_week]
        self.firstWeekDayComboBox.setCurrentIndex(week_day_index)

        self.config.first_date_of_week = self.firstWeekDayComboBox.currentData()

        jira_config = self.config.jira
        if jira_config.host is not None:
            self.jiraHostLineEdit.setText(self.config.jira.host)
        if jira_config.user is not None:
            self.jiraUserLineEdit.setText(self.config.jira.user)
        if jira_config.token is not None:
            self.jiraTokenLineEdit.setText(self.config.jira.token)

        tempo_config = self.config.tempo
        if tempo_config.token is not None:
            self.tempoTokenLineEdit.setText(tempo_config.token)

        toggl_config = self.config.toggl
        if toggl_config.user_agent is not None:
            self.togglUserLineEdit.setText(toggl_config.user_agent)
        if toggl_config.token is not None:
            self.togglTokenLineEdit.setText(toggl_config.token)

    def _save(self):
        self._apply()
        self._close()

    def _apply(self):
        self._save_config()

    def _close(self):
        self.close()

    def _save_config(self):
        self.config.first_date_of_week = self.firstWeekDayComboBox.currentData()

        jira_config = self.config.jira
        jira_config.host = self.jiraHostLineEdit.text()
        jira_config.user = self.jiraUserLineEdit.text()
        jira_config.token = self.jiraTokenLineEdit.text()

        tempo_config = self.config.tempo
        tempo_config.token = self.tempoTokenLineEdit.text()

        toggl_config = self.config.toggl
        toggl_config.user_agent = self.togglUserLineEdit.text()
        toggl_config.token = self.togglTokenLineEdit.text()

        self.config.save()

        self.config_has_changed = True
