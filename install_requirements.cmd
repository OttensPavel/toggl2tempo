@ECHO OFF

SET VENV_DIR=.\venv\Scripts

IF NOT EXIST %VENV_DIR% (
	echo Prepare virtual env ...
	pyw.exe -m venv .\venv
)

%VENV_DIR%\pip.exe install -r requirements.txt
