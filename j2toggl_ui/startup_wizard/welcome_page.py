import os
from typing import Optional

from PyQt5.QtWidgets import QWizardPage, QRadioButton, QMessageBox
from PyQt5.uic import loadUi

from j2toggl_core.import_manager import ImportManager
from j2toggl_ui.startup_wizard.finish_page import FinishPage
from j2toggl_ui.startup_wizard.import_page import ImportPage


class WelcomePage(QWizardPage):
    Id = 1

    def __init__(self):
        super().__init__()

        self.setupViaWizardRadioButton: Optional[QRadioButton] = None
        self.importRadioButton: Optional[QRadioButton] = None

        current_path = os.path.dirname(__file__)
        ui_path = os.path.join(current_path, "welcome_page.ui")
        loadUi(ui_path, self)

    def nextId(self):
        if self.importRadioButton.isChecked():
            return ImportPage.Id
        else:
            return FinishPage.Id

    def validatePage(self) -> bool:
        if self.importRadioButton.isChecked() and ImportManager.configuration_exists():
            mb = QMessageBox()
            mb.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            mb.setModal(True)
            mb.setIcon(QMessageBox.Question)
            mb.setWindowTitle("Are you sure to replace current configuration?")
            mb.setText("Current installation already has configuration and DB. " +
                       "Import configuration will replace them. " +
                       "Are you sure?")
            mb.exec_()

            return mb.result() == QMessageBox.Yes

        return True
