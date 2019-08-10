import utilities
import re
from pathlib import Path
from PyQt5.QtWidgets import (
    QWizardPage, QWizard, QLabel, QVBoxLayout, QCheckBox, QGridLayout,
    QLineEdit, QProgressBar, QPushButton, QMessageBox, QHBoxLayout,
    QApplication)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal, QThread


class OneWireMaster(QWizardPage):
    """Third QWizard page. Handles OneWire Master programming."""
    command_signal = pyqtSignal(str)
    reprogram_signal = pyqtSignal()
    file_write_signal = pyqtSignal(str)
    one_wire_test_signal = pyqtSignal()
    complete_signal = pyqtSignal()

    def __init__(self, d505, test_utility, serial_manager, report):
        super().__init__()

        self.d505 = d505
        self.tu = test_utility
        self.sm = serial_manager
        self.report = report
        self.one_wire_master_file = None
        self.hex_files_dir = None

        self.system_font = QApplication.font().family()
        self.label_font = QFont(self.system_font, 12)

        self.one_wire_lbl = QLabel("Program One-Wire-Master")
        self.one_wire_lbl.setFont(self.label_font)
        self.one_wire_pbar = QProgressBar()
        self.start_btn = QPushButton("Start programming")
        self.start_btn.setFont(self.label_font)
        self.start_btn.setMaximumWidth(150)
        self.start_btn.clicked.connect(self.check_version)

        self.layout = QVBoxLayout()
        self.layout.addStretch()
        self.layout.addWidget(self.one_wire_lbl)
        self.layout.addWidget(self.one_wire_pbar)
        self.layout.addWidget(self.start_btn)
        self.layout.addStretch()

        self.setLayout(self.layout)
        self.setTitle("Program 1-Wire Master")

    def initializePage(self):
        self.pbar_value = 0
        self.is_complete = False
        self.sm.line_written.disconnect()
        self.command_signal.connect(self.sm.send_command)
        self.file_write_signal.connect(self.sm.write_hex_file)
        self.reprogram_signal.connect(self.sm.reprogram_one_wire)
        self.one_wire_test_signal.connect(self.sm.one_wire_test)
        self.complete_signal.connect(self.completeChanged)
        self.sm.data_ready.connect(self.compare_versions)
        self.sm.line_written.connect(self.update_pbar)
        self.d505.button(QWizard.NextButton).setEnabled(False)

    def check_version(self):
        self.hex_files_dir = self.tu.settings.value("hex_files_path")

        (self.one_wire_master_file, self.one_wire_master_ver) = (
            utilities.get_latest_version(
                Path(self.hex_files_dir).glob("1-wire-master*.hex"))
        )

        if self.one_wire_master_file:
            self.start_btn.setEnabled(False)
            self.one_wire_test_signal.emit()
        else:
            QMessageBox.warning(self, "Error!",
                                "Missing one-wire-master file!")

    def compare_versions(self, data):
        self.sm.data_ready.disconnect()
        pattern = r"([0-9]+\.[0-9a-zA-Z]+)"
        m = re.search(pattern, data)
        if m:
            board_version = m.group()
        else:
            QMessageBox.warning(self, "Error!", "Bad version data!")
            return

        if utilities.newer_file_version(self.one_wire_master_ver,
                                        board_version):
            self.sm.data_ready.connect(self.send_hex_file)
            self.start_programming()
        else:
            self.one_wire_lbl.setText("File version not newer than board," 
                                      " skipping..")
            self.tu.one_wire_prog_status.setText("1-Wire Programming: PASS")
            self.tu.one_wire_prog_status.setStyleSheet(self.d505.status_style_pass)
            self.one_wire_pbar.setRange(0, 1)
            self.one_wire_pbar.setValue(1)
            self.is_complete = True
            self.complete_signal.emit()

    def isComplete(self):
        return self.is_complete

    def start_programming(self):
        self.one_wire_pbar.setRange(0, 0)
        self.reprogram_signal.emit()
        self.one_wire_lbl.setText("Erasing flash. . .")

    def send_hex_file(self, data):
        self.sm.data_ready.disconnect()

        # Get file length
        count = 0
        try:
            with open(self.one_wire_master_file, "r") as f:
                for line in f:
                    count += 1
            self.one_wire_pbar.setRange(0, count)
        except IOError:
            QMessageBox.warning(self, "Warning",
                                "Can't open one-wire-master file!")
            return

        # Check for response from board before proceeding
        pattern = "download hex records now..."
        if (re.search(pattern, data)):
            self.one_wire_lbl.setText("Programming 1-wire master. . .")
            self.sm.data_ready.connect(self.data_parser)
            self.file_write_signal.emit(str(self.one_wire_master_file))
        else:
            QMessageBox.warning(self, "Xmega1", "Bad command response.")

    def update_pbar(self):
        self.pbar_value += 1
        self.one_wire_pbar.setValue(self.pbar_value)

    def data_parser(self, data):
        self.sm.data_ready.disconnect()
        self.sm.data_ready.connect(self.record_version)
        pattern = "lock bits set"
        if (re.search(pattern, data)):
            self.one_wire_lbl.setText("Programming complete.")
            self.one_wire_test_signal.emit()
        else:
            QMessageBox.warning(self, "Xmega2", "Bad command response.")

    def record_version(self, data):
        self.sm.data_ready.disconnect()
        pattern = r"([0-9]+\.[0-9a-zA-Z]+)"
        onewire_version = re.search(pattern, data)
        if (onewire_version):
            onewire_version_val = onewire_version.group()
            self.report.write_data("onewire_ver", onewire_version_val, "PASS")
            self.one_wire_lbl.setText("Version recorded.")
            self.tu.one_wire_prog_status.setText("1-Wire Programming: PASS")
            self.tu.one_wire_prog_status.setStyleSheet(self.d505.status_style_pass)
        else:
            self.report.write_data("onewire_ver", "N/A", "FAIL")
            self.tu.one_wire_prog_status.setText("Xmega Programming: FAIL")
            self.tu.one_wire_prog_status.setStyleSheet(self.d505.status_style_fail)
            QMessageBox.warning(self, "XMega3", "Bad command response.")

        self.is_complete = True
        self.complete_signal.emit()
