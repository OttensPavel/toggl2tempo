#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import os
import shutil
import subprocess
import sys
import urllib.request
import zipfile

from contextlib import contextmanager
from pathlib import Path
from typing import List

""" This script is based on following articles:
* https://dev.to/fpim/setting-up-python-s-windows-embeddable-distribution-properly-1081
* https://docs.python.org/3.6/using/windows.html#finding-modules
* https://docs.python.org/3.8/using/windows.html#windows-embeddable
"""

source_dir = Path("..")

env_dir = source_dir.joinpath("venv", "Scripts")
python_path = str(env_dir.joinpath("python.exe").resolve())
pip_path = str(env_dir.joinpath("pip.exe").resolve())

dist_dir = source_dir.joinpath("dist")
package_dir = dist_dir.joinpath("package")
libs_dir = package_dir.joinpath("libs")


@contextmanager
def pushd(new_dir):
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(previous_dir)


def cleanup_packages():
    packages_bin = libs_dir.joinpath("bin")
    if packages_bin.exists():
        shutil.rmtree(packages_bin)

    for cache_dir in package_dir.rglob("__pycache__"):
        shutil.rmtree(cache_dir)


def trim_qt5_libraries():
    pyqt5_dir = libs_dir.joinpath("PyQt5")

    qt5_libs_dir = pyqt5_dir.joinpath("Qt5")
    if not qt5_libs_dir.exists():
        print(f"Couldn't find PyQt5 libraries by path '{qt5_libs_dir}'", file=sys.stderr)
        exit(1)

    # We don't use translations now
    translations_dir = qt5_libs_dir.joinpath("translations")
    if translations_dir.exists():
        shutil.rmtree(translations_dir)

    # Qml
    remove_nested_objects(
        qt5_libs_dir.joinpath("qml"),
        exclude_names=["Qt", "QtQml"])

    # Plugins
    remove_nested_objects(
        qt5_libs_dir.joinpath("plugins"),
        exclude_names=["generic", "geometryloaders", "iconengines", "imageformats", "platforms",
                       "platformthemes", "renderers", "sceneparsers", "styles"])

    # Main libs
    qt5_bin_path = qt5_libs_dir.joinpath("bin")
    remove_nested_objects(
        qt5_bin_path,
        exclude_names=["Qt5Core.dll", "Qt5Designer.dll", "Qt5Gui.dll", "Qt5QmlModels.dll",
                       "Qt5Widgets.dll", "Qt5WinExtras.dll", "Qt5Xml.dll"],
        pattern="Qt5*.dll")

    # Very large OpenGL lib
    opengl32sw_path = qt5_bin_path.joinpath("opengl32sw.dll")
    opengl32sw_path.unlink(missing_ok=True)

    # Pyd and Pyi files
    remove_nested_objects(
        pyqt5_dir,
        exclude_names=["QtCore.pyd", "QtDesigner.pyd", "QtGui.pyd", "QtQmlModels.pyd",
                       "QtWidgets.pyd", "QtWinExtras.pyd", "QtXml.pyd"],
        pattern="Qt*.pyd")

    remove_nested_objects(pyqt5_dir, exclude_names=[], pattern="*.pyi")


def remove_nested_objects(root_dir_path: Path, exclude_names: List[str], pattern: str = "*"):
    paths_to_remove = list(filter(lambda ptr: ptr.name not in exclude_names, root_dir_path.glob(pattern)))
    for p in paths_to_remove:
        if p.is_dir():
            shutil.rmtree(p)
        elif p.is_file():
            p.unlink()


# Variables
app_name = "toggl2tempo"

python_embedded_version = "python310"
python_embedded_file_name = "python-3.10.10-embed-amd64.zip"
python_embedded_file_hash_sum = "b8c99a1bce379287eae580e7ecd0d8f4afdce0a27268d7f26db205f3362d7bab"
python_embedded_url = "https://www.python.org/ftp/python/3.10.10/python-3.10.10-embed-amd64.zip"
python_embedded_file_path = dist_dir.joinpath(python_embedded_file_name)

# === Read version ===
print("Read version ...")
version_file = source_dir.joinpath("version")
with version_file.open(mode="r", encoding='ascii') as f:
    version = f.read()

# === Remove old package directory
print("Cleanup artifacts of previous build ...")
if package_dir.exists():
    shutil.rmtree(package_dir)

if not dist_dir.exists():
    dist_dir.mkdir()

if not package_dir.exists():
    package_dir.mkdir()

# === Download Python Embedded dist package ===
print("Download Python Embedded dist package ...")
if not python_embedded_file_path.exists():
    urllib.request.urlretrieve(python_embedded_url, python_embedded_file_path)

# Check hash sum
print("Check hash sum ...")
h = hashlib.sha256()

with python_embedded_file_path.open(mode="rb") as f:
    while True:
        block = f.read(2048)
        if len(block) == 0:
            break

        h.update(block)

h.digest()

current_hash_sum = h.hexdigest()
if python_embedded_file_hash_sum != current_hash_sum:
    raise Exception(f"Hash sum {current_hash_sum} of downloaded '{python_embedded_file_name}' \
      doesn't match with expected {python_embedded_file_hash_sum}")

# === Prepare Python embedded dist ===
print("Prepare Python embedded dist ...")

# Unzip archive with Python binaries embedded
with zipfile.ZipFile(python_embedded_file_path, 'r') as zip_ref:
    zip_ref.extractall(package_dir)

# Rename archive with Python bytecode
python_pyc_archive = package_dir.joinpath(f"{python_embedded_version}.zip")
python_pyc_archive = python_pyc_archive.rename(python_pyc_archive.with_name(f"_{python_embedded_version}.zip"))

# Create dir for Python bytecode
python_pyc_dir = package_dir.joinpath(f"{python_embedded_version}.zip")
python_pyc_dir.mkdir()

# Unzip the archive of Python bytecode
with zipfile.ZipFile(python_pyc_archive, 'r') as zip_ref:
    zip_ref.extractall(python_pyc_dir)

# Remove original archive of Python bytecode
python_pyc_archive.unlink()

# Update file of Python paths
path_file = package_dir.joinpath(f"{python_embedded_version}._pth")
with path_file.open(mode="w", encoding="utf-8") as f:
    f.write(f"""
libs
{python_embedded_version}.zip
.

import site
""")

# === Build wheel distribution package ===
print("Build Wheel distribution packages ...")
with pushd(source_dir):
    bdist_process = subprocess.run([python_path, '-m', "build", "--wheel"],
                                   stdout=subprocess.PIPE,
                                   universal_newlines=True)
    if bdist_process.returncode != 0:
        exit(bdist_process.returncode)

# === Install application and requirements ===
print("Install application and requirements ...")
wheel_package_path = dist_dir.joinpath(f"toggl2tempo-{version}-py3-none-any.whl")
pip_process = subprocess.run([pip_path, 'install', "-t", libs_dir, wheel_package_path],
                             stdout=subprocess.PIPE,
                             universal_newlines=True)
if pip_process.returncode != 0:
    exit(pip_process.returncode)

# == Remove unused parts of Qt5
cleanup_packages()
trim_qt5_libraries()

# Copy main script
shutil.copy(source_dir.joinpath("main.py"), package_dir.joinpath(f"{app_name}.py"))

# === Run NSIS to build Windows installer ===
print("Make Windows installer ...")
makensis_process = subprocess.run(['makensis.exe', 'embedded-installer.nsi'],
                                  stdout=subprocess.PIPE,
                                  universal_newlines=True)
if makensis_process.returncode != 0:
    exit(makensis_process.returncode)

print("Success!")
