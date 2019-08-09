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

def get_latest_version(path: Path, file_name: str) -> (str, str):
    if file_name == "main-app":
        filenames = list(path.glob("main-app*.hex"))
    elif file_name == "one-wire":
        filenames = list(path.glob("1-wire-master*.hex"))
    else:
        raise InvalidType

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