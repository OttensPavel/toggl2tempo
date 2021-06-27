@ECHO OFF

SET VENV_DIR=.\venv\Scripts

IF NOT EXIST %VENV_DIR% (
	echo Prepare virtual env ...
	python -m virtualenv .\venv
)

%VENV_DIR%\pip.exe install -r requirements.config