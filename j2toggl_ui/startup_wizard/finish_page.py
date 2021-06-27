import os
from typing import Optional

from PyQt5.QtWidgets import QWizardPage, QLabel
from PyQt5.uic import loadUi


class FinishPage(QWizardPage):
    Id = 99

    def __init__(self):
        super().__init__()

        self.finishMessageLabel: Optional[QLabel] = None

        self.__init_ui()

        self.setFinalPage(True)

    def __init_ui(self):
        current_path = os.path.dirname(__file__)
        ui_path = os.path.join(current_path, "finish_page.ui")
        loadUi(ui_path, self)

    def initializePage(self) -> None:
        message = self.wizard().final_message
        if message is None:
            message = "Setup is not completed. Please setup settings manually."

        self.finishMessageLabel.setText(message)
