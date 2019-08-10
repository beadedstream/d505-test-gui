import re
from packaging.version import LegacyVersion
from pathlib import Path
from PyQt5.QtWidgets import QCheckBox, QLabel

def checked(lbl, chkbx):
    """Utility function for formatted a checked Qcheckbox."""

    if chkbx.isChecked():
        chkbx.setEnabled(False)
        lbl.setStyleSheet("QLabel {color: grey}")

def unchecked(lbl, chkbx):
    """Utility function for formatting an unchecked Qcheckbox."""

    if chkbx.isChecked():
        chkbx.setEnabled(True)
        chkbx.setChecked(False)
        lbl.setStyleSheet("QLabel {color: black}")

def get_latest_version(filenames: list) -> (str, str):
    current_version = None
    current_filename = None

    for name in filenames:
        p = r"([0-9]+\.[0-9]+[a-z])"
        try:
            version = re.search(p, str(name)).group()
        except AttributeError:
            continue

        if not current_version:
            current_version = version
            current_filename = name

        if LegacyVersion(version) > LegacyVersion(current_version):
            current_version = version
            current_filename = name

    return (current_filename, current_version)

def newer_file_version(file_version: str, board_version: str) -> bool:
    """Compare the file version and board version and return True if the file
    version is newer than the board version and the board should be flashed.
    """
    return LegacyVersion(file_version) > LegacyVersion(board_version) 