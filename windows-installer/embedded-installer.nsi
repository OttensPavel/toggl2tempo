Unicode true

!define APPNAME "toggl2tempo"
!define DESCRIPTION "Desktop application to sync work logs between Toggl and JIRA Tempo."
!define ABOUTURL  "https://bitbucket.org/togglsync_team/toggl-sync/src/master/"
!define /file VERSION ..\version

RequestExecutionLevel user

InstallDir "$LOCALAPPDATA\${APPNAME}"
LicenseData "..\license.txt"

Name "${APPNAME} v${VERSION}"
Icon "app-icon.ico"
OutFile "..\dist\toggl2tempo-setup-x64-${VERSION}.exe"

!Include LogicLib.nsh
!include x64.nsh

# Just three pages - license agreement, install location, and installation
Page license
Page directory
Page instfiles

# === Installer ===
function .onInit
    ${IfNot} ${RunningX64}
        MessageBox MB_OK|MB_ICONSTOP "Windows x32 architecture doesn't support now."
        Abort
    ${EndIf}

functionEnd

section "install"
    # Files for the install directory - to build the installer, these should be in the same directory as the install script (this file)
    SetOutPath $INSTDIR

    # Files added here should be removed by the uninstaller (see section "uninstall")
    File /r "..\dist\package\*"
    File ".\app-icon.ico"

    # Start Menu
    CreateShortCut "$SMPROGRAMS\${APPNAME}.lnk" "$INSTDIR\pythonw.exe" "${APPNAME}.py" "$INSTDIR\app-icon.ico"
    CreateShortCut "$SMPROGRAMS\${APPNAME} - Debug.lnk" "$INSTDIR\python.exe" "${APPNAME}.py" "$INSTDIR\app-icon.ico"

    # Uninstaller - See function un.onInit and section "uninstall" for configuration
    WriteUninstaller "$INSTDIR\uninstall.exe"

    # Registry information for add/remove programs
    WriteRegStr   HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME} - ${DESCRIPTION}"
    WriteRegStr   HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    WriteRegStr   HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
    WriteRegStr   HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$\"$INSTDIR$\""
    WriteRegStr   HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$\"$INSTDIR\app-icon.ico$\""
    WriteRegStr   HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "$\"${ABOUTURL}$\""
    WriteRegStr   HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSION}"

    # There is no option for modifying or repairing the install
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoModify" 1
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoRepair" 1
sectionEnd

### === Uninstaller ===
function un.onInit
    MessageBox MB_OKCANCEL "Do you want to remove ${APPNAME}?" IDOK next
        Abort

    next:
functionEnd

section "uninstall"
    # Remove Start Menu launcher
    Delete "$SMPROGRAMS\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\${APPNAME} - Debug.lnk"

    # Try to remove the install directory
    RMDir /r $INSTDIR

    # Remove uninstaller information from the registry
    DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
sectionEnd
