import re
import avr
from packaging.version import LegacyVersion
from pathlib import Path
from PyQt5.QtWidgets import (
    QWizardPage, QWizard, QLabel, QVBoxLayout, QCheckBox, QGridLayout,
    QLineEdit, QProgressBar, QPushButton, QMessageBox, QHBoxLayout,
    QApplication, QSizePolicy
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal, QThread
