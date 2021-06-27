from typing import Optional

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWizard

from j2toggl_ui.startup_wizard.finish_page import FinishPage
from j2toggl_ui.startup_wizard.import_page import ImportPage
from j2toggl_ui.startup_wizard.welcome_page import WelcomePage


class StartupWizard(QWizard):
    def __init__(self):
        super().__init__()

        self.import_path: Optional[str] = None
        self.final_message: Optional[str] = None

        self.setWindowTitle("Startup wizard")
        self.setWindowIcon(QIcon(':app-icon'))
        # self.setWizardStyle(QWizard.AeroStyle)

        self.setOptions(QWizard.NoCancelButtonOnLastPage)

        self.setPage(WelcomePage.Id, WelcomePage())
        self.setPage(ImportPage.Id, ImportPage())
        self.setPage(FinishPage.Id, FinishPage())
