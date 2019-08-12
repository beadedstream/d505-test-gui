import utilities
import re
from PyQt5.QtWidgets import (
    QWizardPage, QWizard, QLabel, QVBoxLayout, QCheckBox, QGridLayout,
    QLineEdit, QProgressBar, QPushButton, QMessageBox, QHBoxLayout,
    QApplication)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal, QThread


class UartPower(QWizardPage):
    """Sixth QWizard page. Handles UART power and LED tests."""
    complete_signal = pyqtSignal()
    command_signal = pyqtSignal(str)

    def __init__(self, d505, test_utility, serial_manager, report):
        super().__init__()

        self.d505 = d505
        self.tu = test_utility
        self.sm = serial_manager
        self.report = report

        self.system_font = QApplication.font().family()
        self.label_font = QFont(self.system_font, 12)

        self.uart_pwr_lbl = QLabel("Remove battery power.")
        self.uart_pwr_lbl.setFont(self.label_font)
        self.uart_pwr_chkbx = QCheckBox()
        self.uart_pwr_chkbx.setStyleSheet("QCheckBox::indicator {width: 20px; "
                                          "height: 20px}")
        self.uart_pwr_chkbx.clicked.connect(
            lambda: utilities.checked(self.uart_pwr_lbl, self.uart_pwr_chkbx))
        self.uart_pwr_chkbx.clicked.connect(self.verify_uart)

        self.uart_pbar_lbl = QLabel("Verify UART interface")
        self.uart_pbar_lbl.setFont(self.label_font)
        self.uart_pbar = QProgressBar()

        self.hall_effect_lbl = QLabel("Bring magnet over Hall-Effect sensor and"
                                  " verify red LED blinks.")
        self.hall_effect_lbl.setFont(self.label_font)
        self.hall_effect_btn_pass = QPushButton("PASS")
        self.hall_effect_btn_pass.setMaximumWidth(75)
        self.hall_effect_btn_fail = QPushButton("FAIL")
        self.hall_effect_btn_fail.setMaximumWidth(75)
        self.hall_effect_btn_pass.clicked.connect(self.hall_effect_pass)
        self.hall_effect_btn_fail.clicked.connect(self.hall_effect_fail)

        self.leds_lbl = QLabel("Remove UART power connection and reconnect the"
                               " battery.")
        self.leds_lbl.setWordWrap(True)
        self.leds_lbl.setFont(self.label_font)
        self.leds_chkbx = QCheckBox()
        self.leds_chkbx.setStyleSheet("QCheckBox::indicator {width: 20px; \
                                        height: 20px}")
        self.leds_chkbx.clicked.connect(
            lambda: utilities.checked(self.leds_lbl, self.leds_chkbx))
        self.leds_chkbx.clicked.connect(self.page_complete)

        self.grid = QGridLayout()
        self.grid.setHorizontalSpacing(75)
        self.grid.setVerticalSpacing(25)
        self.grid.addWidget(self.uart_pwr_lbl, 0, 0)
        self.grid.addWidget(self.uart_pwr_chkbx, 0, 1)
        self.grid.addWidget(QLabel(), 1, 0)
        self.grid.addWidget(self.uart_pbar_lbl, 2, 0)
        self.grid.addWidget(self.uart_pbar, 3, 0)
        self.grid.addWidget(QLabel(), 4, 0)
        self.grid.addWidget(self.hall_effect_lbl, 5, 0)
        self.grid.addWidget(self.hall_effect_btn_pass, 5, 1)
        self.grid.addWidget(self.hall_effect_btn_fail, 5, 2)
        self.grid.addWidget(self.leds_lbl, 6, 0)
        self.grid.addWidget(self.leds_chkbx, 6, 1)

        self.layout = QVBoxLayout()
        self.layout.addStretch()
        self.layout.addLayout(self.grid)
        self.layout.addStretch()

        self.setLayout(self.layout)
        self.setTitle("UART Power")

    def initializePage(self):
        self.is_complete = False
        self.complete_signal.connect(self.completeChanged)
        self.command_signal.connect(self.sm.send_command)
        self.d505.button(QWizard.NextButton).setEnabled(False)
        self.hall_effect_btn_pass.setEnabled(False)
        self.hall_effect_btn_fail.setEnabled(False)
        self.leds_chkbx.setEnabled(False)

    def verify_uart(self):
        self.sm.data_ready.connect(self.rx_psoc)
        self.uart_pbar.setRange(0, 0)
        self.uart_pbar_lbl.setText("Verifying UART interface...")
        self.command_signal.emit("psoc-version")

    def rx_psoc(self, data):
        self.sm.data_ready.disconnect()
        pattern = r"([0-9)+.([0-9])+.([0-9])+"
        version = re.search(pattern, data)
        if (version):
            self.uart_pbar.setRange(0, 1)
            self.uart_pbar.setValue(1)
            self.uart_pbar_lbl.setText("UART interface functional.")
            self.uart_pbar_lbl.setStyleSheet("QLabel {color: grey}")
            self.report.write_data("uart_comms", "", "PASS")
        else:
            QMessageBox.warning(self, "UART Power", "Bad command response.")
            self.report.write_data("uart_comms", "", "FAIL")
        self.hall_effect_btn_pass.setEnabled(True)
        self.hall_effect_btn_fail.setEnabled(True)

    def hall_effect_pass(self):
        self.tu.hall_effect_status.setText(
            "Hall Effect Sensor Test: PASS")
        self.tu.hall_effect_status.setStyleSheet(
            self.d505.status_style_pass)
        self.hall_effect_btn_pass.setEnabled(False)
        self.hall_effect_btn_fail.setEnabled(False)
        self.leds_chkbx.setEnabled(True)

    def hall_effect_fail(self):
        self.tu.hall_effect_status.setText(
            "Hall Effect Sensor Test: FAIL")
        self.tu.hall_effect_status.setStyleSheet(
            self.d505.status_style_fail)
        self.hall_effect_btn_pass.setEnabled(False)
        self.hall_effect_btn_fail.setEnabled(False)
        self.leds_chkbx.setEnabled(True)

    def isComplete(self):
        return self.is_complete

    def page_complete(self):
        self.tu.led_test_status.setText("LED Test: PASS")
        self.report.write_data("led_test", "", "PASS")
        self.tu.led_test_status.setStyleSheet(
            self.d505.status_style_pass)
        self.is_complete = True
        self.complete_signal.emit()