import os
from typing import Optional

from PyQt5.QtWidgets import QWizardPage, QToolButton, QLineEdit, QLabel, QMessageBox
from PyQt5.uic import loadUi

from j2toggl_core.import_manager import ImportManager
from j2toggl_ui.startup_wizard.finish_page import FinishPage


class ImportPage(QWizardPage):
    Id = 2

    def __init__(self):
        super().__init__()

        self.configurationDirPath: Optional[str] = None
        self.overrideExistedConfiguration: bool = False

        self.selectDirectoryToolButton: Optional[QToolButton] = None
        self.importDirectoryPathLineEdit: Optional[QLineEdit] = None
        self.errorLabel: Optional[QLabel] = None

        self.__init_ui()
        self.__init_signals()

    def __init_ui(self):
        current_path = os.path.dirname(__file__)
        ui_path = os.path.join(current_path, "import_page.ui")
        loadUi(ui_path, self)

    def __init_signals(self):
        self.selectDirectoryToolButton.clicked.connect(self.__select_config_file_to_import)

    def __select_config_file_to_import(self):
        from PyQt5.QtWidgets import QFileDialog

        self.hide_error()

        dialog = QFileDialog()
        directory_path = dialog.getExistingDirectory(
            caption="Select old Toggl2Tempo folder ...",
            options=QFileDialog.DontUseNativeDialog)

        if directory_path is not None:
            self.configurationDirPath = directory_path
            self.importDirectoryPathLineEdit.setText(directory_path)

        self.completeChanged.emit()

    def hide_error(self):
        self.errorLabel.setVisible(False)
        self.errorLabel.setText("")

    def nextId(self):
        return FinishPage.Id

    def isComplete(self):
        is_valid, error_msg = ImportManager.validate(self.configurationDirPath)
        self.errorLabel.setVisible(not is_valid)
        if error_msg is not None:
            self.errorLabel.setText(error_msg)

        return is_valid

    def validatePage(self) -> bool:
        is_valid, error_msg = ImportManager.validate(self.configurationDirPath)
        self.errorLabel.setVisible(not is_valid)
        if error_msg is not None:
            self.errorLabel.setText(error_msg)

        if is_valid:
            self.wizard().import_path = self.configurationDirPath
            self.wizard().final_message = "Configuration and DB will be imported."
        else:
            self.wizard().import_path = None
            self.wizard().final_message = None

        return is_valid
