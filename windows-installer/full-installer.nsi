### !!! ATTENTION! This script isn't completed.

!define APPNAME "toggl2tempo"
!define DESCRIPTION "Desktop application to sync work logs between Toggl and JIRA Tempo."

!define PYTHON_VER "3.10"
!define WHEEL_FILE "${APPNAME}-${VERSION}-py3-none-any.whl"
!define ABOUTURL  "https://bitbucket.org/togglsync_team/toggl-sync/src/master/"

!define /file VERSION ..\version

Unicode true
RequestExecutionLevel admin # Require admin rights on NT6+ (When UAC is turned on)

InstallDir "$LOCALAPPDATA\${APPNAME}"
LicenseData "..\LICENSE"

Name "${APPNAME} v${VERSION}"
Icon "app-icon.ico"

OutFile "..\dist\toggl2tempo-setup-x64-${VERSION}.exe"

!include "MUI2.nsh"
!Include LogicLib.nsh
!include x64.nsh

;======================================================
; Pages

#!define MUI_HEADERIMAGE
!define MUI_ABORTWARNING
#!define MUI_COMPONENTSPAGE_SMALLDESC
#!define MUI_HEADERIMAGE_BITMAP_NOSTRETCH
!define MUI_FINISHPAGE

#!define MUI_WELCOMEFINISHPAGE_BITMAP "..\somepic.bmp"
#!define MUI_ICON "..\someicon.ico"

#!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_COMPONENTS
#Page custom customerConfig
#Page custom priorApp
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
# TODO: Replace this text
!define MUI_FINISHPAGE_TEXT "Thank you for installing the appname. \r\n\n\nYou can check the install by going to the Test Page at: http://appname/testpage.jsp"

### === Installer ===
function .onInit
    SetShellVarContext all

    ${IfNot} ${RunningX64}
        MessageBox MB_OK|MB_ICONSTOP "Windows x32 architecture doesn't support now. Sorry."
        Abort
    ${EndIf}

    var /GLOBAL python_location_path
    var /GLOBAL python_bin_path
    var /GLOBAL pip_version

    ReadRegStr $python_location_path HKLM64 "Software\Python\PythonCore\${PYTHON_VER}\InstallPath" ""
    ReadRegStr $python_bin_path HKLM64 "Software\Python\PythonCore\${PYTHON_VER}\InstallPath" "ExecutablePath"
    ReadRegStr $pip_version HKLM64 "Software\Python\PythonCore\${PYTHON_VER}\InstalledFeatures" "pip"

    StrCmp $python_location_path "" PythonIsNotInstalled 0
    StrCmp $python_bin_path "" PythonIsNotInstalled 0
    StrCmp $pip_version "" PipIsNotInstalled 0
    Goto NoAbort

    PythonIsNotInstalled:
    MessageBox MB_OK|MB_ICONSTOP "Can't find Python install path. Please install Python ${PYTHON_VER} with PIP."
    Abort

    PipIsNotInstalled:
    MessageBox MB_OK|MB_ICONSTOP "The PIP feature doesn't installed with Python. Please reinstall Python ${PYTHON_VER} with PIP feature."
    Abort

    NoAbort:

functionEnd

section "Python 3.8"
    # Download Python installer
    # Don't forget to install inetc plugin
    !tempfile FILE
    inetc::get /BANNER "Download Python 3.8.2 installer ..." https://www.python.org/ftp/python/3.8.2/python-3.8.2-amd64.exe ${FILE} /END

    Pop $0
    StrCmp $0 "OK" install 0
    MessageBox MB_OK|MB_ICONEXCLAMATION "Download failed. Click 'OK' to abort installation" /SD IDOK
    Quit

    install:
    # Install Python
    # Based on https://docs.python.org/3.8/using/windows.html
    Rename $FILE $FILE.exe
    ExecWait "$FILE.exe InstallAllUsers=1 Include_doc=0 Include_dev=0 Include_tcltk=0 Include_test=0" $0
    IntCmp $0 0 complete 0 0
    MessageBox MB_OK|MB_ICONEXCLAMATION "Installation failed." /SD IDOK
    Quit

    complete:

sectionEnd

section "toggl2tempo"
    # Files for the install directory - to build the installer, these should be in the same directory as the install script (this file)
    SetOutPath $INSTDIR

    # Files added here should be removed by the uninstaller (see section "uninstall")
    File "..\LICENSE"
    File "..\dist\${WHEEL_FILE}"
    File /oname=logo.ico ".\app-icon.ico"

    # Search Python install paths

    # TODO: Can we move this check to separated page?
    DetailPrint "Python install path: $python_location_path"
    DetailPrint "Python executable path: $python_bin_path"

    # Install virtual env
    # TODO: Add check of return code
    ExecWait "$python_location_path\Scripts\pip.exe install virtualenv"

    # Create virtual env
    var /GLOBAL venv_path
    var /GLOBAL venv_scripts_path
    StrCpy $venv_path "$INSTDIR\venv"
    StrCpy $venv_scripts_path "$INSTDIR\venv\Scripts"

    # TODO: Add check of return code
    ExecWait "$python_bin_path -m virtualenv $venv_path"

    # Install package
    # TODO: Add check of return code
    ExecWait "$venv_scripts_path\pip.exe install $INSTDIR\${WHEEL_FILE}"

    # Start Menu
    CreateShortCut "$SMPROGRAMS\${APPNAME}.lnk" "$venv_scripts_path\toggl2tempo.exe" "" "$INSTDIR\logo.ico"
    CreateShortCut "$SMPROGRAMS\${APPNAME} - Debug.lnk" "$venv_scripts_path\toggl2tempo_debug.exe" "" "$INSTDIR\logo.ico"

    # Uninstaller - See function un.onInit and section "uninstall" for configuration
    WriteUninstaller "$INSTDIR\uninstall.exe"

    # Registry information for add/remove programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME} - ${DESCRIPTION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$\"$INSTDIR$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$\"$INSTDIR\logo.ico$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "$\"${ABOUTURL}$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSION}"

    # There is no option for modifying or repairing the install
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoRepair" 1
sectionEnd

### === Uninstaller ===
function un.onInit
    SetShellVarContext all

    MessageBox MB_OKCANCEL "Do you want to remove ${APPNAME}?" IDOK next
        Abort

    next:
functionEnd

section "uninstall"
    # Remove Start Menu launcher
    Delete "$SMPROGRAMS\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\${APPNAME} - Debug.lnk"

    # Remove files
    Delete $INSTDIR\license.txt
    Delete $INSTDIR\${WHEEL_FILE}
    Delete $INSTDIR\uninstall.exe

    # Try to remove the install directory - this will only happen if it is empty
    RMDir /r $INSTDIR

    # Remove uninstaller information from the registry
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
sectionEnd
