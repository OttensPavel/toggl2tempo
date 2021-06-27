@ECHO OFF

SET VENV_DIR=.\venv\Scripts

%VENV_DIR%\pyrcc5.exe .\j2toggl_ui\resources.qrc -o .\j2toggl_ui\resouces.py

PAUSE
