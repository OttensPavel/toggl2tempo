#!/usr/bin/python3
import sys
import traceback

from loguru import logger

from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtWidgets import QMessageBox

from j2toggl_core.app_paths import get_app_file_path
from j2toggl_core.configuration.json_config import JsonConfig
from j2toggl_core.import_manager import ImportManager
from j2toggl_ui.main_window import MainWindow
from j2toggl_ui.resources.resouces import qInitCommonResources
from j2toggl_ui.startup_wizard.wizard import StartupWizard


def handle_exception(exc_type, exc_value, exc_traceback):
    """ catch unhandled exceptions """

    # KeyboardInterrupt is a special case.
    # We don't raise the error dialog when it occurs.
    if issubclass(exc_type, KeyboardInterrupt):
        return

    message = "Closed due to an error. This is the full error report: {0}"\
        .format(traceback.format_exception(exc_type, exc_value, exc_traceback))
    message = str.replace(message, "\\n", "\n")

    logger.error(message)

    sys.exit(1)


def start_ui():
    init_successful = True

    # Setup logging
    file_log_format = "{time:YYYY-MM-DD HH:mm:ss.SSS}"\
        + "| {level: <8} | {name} | {message} | {exception}"

    log_file_path = get_app_file_path("j2toggl.log")
    logger.add(log_file_path, level="DEBUG", format=file_log_format)

    # Load common resources
    qInitCommonResources()

    # Create app
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Load config
    config = JsonConfig()

    show_configuration_ui: bool = False

    if not config.exists():
        wizard = StartupWizard()
        wizard.exec_()

        result = wizard.result()
        if result != QDialog.Accepted:
            exit(0)

        if wizard.import_path is not None:
            imp_manager = ImportManager(wizard.import_path)
            imp_manager.import_artifacts()
        else:
            show_configuration_ui = True

    try:
        config.load()
    except Exception as configLoadError:
        init_successful = False
        msg = configLoadError.__str__()
        logger.error(msg)

        mb = QMessageBox()
        mb.setIcon(QMessageBox.Critical)
        mb.setWindowTitle("Error")
        mb.setText("Error occurs on load config file.\n\nPlease see app-config.json.sample for more details.")
        mb.setDetailedText(msg)
        mb.exec()

    if not init_successful:
        exit(1)

    main_ui_window = MainWindow(config, show_configuration_ui)
    main_ui_window.show()

    sys.excepthook = handle_exception
    sys.exit(app.exec_())
