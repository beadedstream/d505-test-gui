import utilities
import re
from PyQt5.QtWidgets import (
    QWizardPage, QWizard, QLabel, QVBoxLayout, QCheckBox, QGridLayout,
    QLineEdit, QProgressBar, QPushButton, QMessageBox, QHBoxLayout,
    QApplication)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal, QThread


class CypressBLE(QWizardPage):
    """Fourth QWizard page. Handles Cypress BLE tests."""
    command_signal = pyqtSignal(str)
    complete_signal = pyqtSignal()

    def __init__(self, d505, test_utility, serial_manager, report):
        super().__init__()

        self.d505 = d505
        self.tu = test_utility
        self.sm = serial_manager
        self.report = report

        self.system_font = QApplication.font().family()
        self.label_font = QFont(self.system_font, 12)

        self.ble_lbl = QLabel("Run the Cypress programming utility to "
                              "program the CYBLE-224116 BLE module.")
        self.ble_lbl.setFont(self.label_font)
        self.ble_btn_pass = QPushButton("PASS")
        self.ble_btn_pass.setMaximumWidth(75)
        self.ble_btn_fail = QPushButton("FAIL")
        self.ble_btn_fail.setMaximumWidth(75)
        self.ble_btn_pass.clicked.connect(self.ble_pass)
        self.ble_btn_fail.clicked.connect(self.ble_fail)

        self.psoc_disconnect_lbl = QLabel()
        self.psoc_disconnect_lbl.setTextFormat(Qt.RichText)
        self.psoc_disconnect_lbl.setFont(self.label_font)
        self.psoc_disconnect_lbl.setText(
            "Disconnect the PSoC programmer from J1 (backside) and sit the "
            "board all<br/>"
            "the way down into the test fixture pushing against the pogo pins.")
        # self.psoc_disconnect_lbl = QLabel("Disconnect the PSoC programmer "
        #                                   "from J1.")
        self.psoc_disconnect_chkbx = QCheckBox()
        self.psoc_disconnect_chkbx.setStyleSheet("QCheckBox::indicator \
                                                 {width: 20px; height: 20px}")
        self.psoc_disconnect_chkbx.clicked.connect(
            lambda: utilities.checked(self.psoc_disconnect_lbl,
                                 self.psoc_disconnect_chkbx))

        self.pwr_cycle_lbl = QLabel("Power cycle DUT (unplug and replug "
                                    "the battery).")
        self.pwr_cycle_lbl.setFont(self.label_font)
        self.pwr_cycle_chkbx = QCheckBox()
        self.pwr_cycle_chkbx.setStyleSheet("QCheckBox::indicator {width: 20px; \
                                        height: 20px}")
        self.pwr_cycle_chkbx.clicked.connect(
            lambda: utilities.checked(self.pwr_cycle_lbl, self.pwr_cycle_chkbx))

        self.bt_comm_lbl = QLabel("Verify communication to 505 with "
                                  "bluetooth device.")
        self.bt_comm_lbl.setFont(self.label_font)
        self.bt_comm_btn_pass = QPushButton("PASS")
        self.bt_comm_btn_pass.setMaximumWidth(75)
        self.bt_comm_btn_fail = QPushButton("FAIL")
        self.bt_comm_btn_fail.setMaximumWidth(75)
        self.bt_comm_btn_pass.clicked.connect(self.bt_comm_pass)
        self.bt_comm_btn_fail.clicked.connect(self.bt_comm_fail)

        self.leds_lbl = QLabel("Verify the blue & green LEDs are working.")
        self.leds_lbl.setFont(self.label_font)
        self.leds_btn_pass = QPushButton("PASS")
        self.leds_btn_pass.setMaximumWidth(75)
        self.leds_btn_fail = QPushButton("FAIL")
        self.leds_btn_fail.setMaximumWidth(75)
        self.leds_btn_pass.clicked.connect(self.leds_pass)
        self.leds_btn_fail.clicked.connect(self.leds_fail)

        self.psoc_pbar = QProgressBar()
        self.psoc_pbar_lbl = QLabel("PSoC version")
        self.psoc_pbar_lbl.setFont(self.label_font)

        self.psoc_layout = QVBoxLayout()
        self.psoc_layout.addWidget(self.psoc_pbar_lbl)
        self.psoc_layout.addWidget(self.psoc_pbar)

        self.uart_wire_lbl = QLabel("Plug in UART power wire before going to "
                                    "the next step.")
        self.uart_wire_lbl.setFont(self.label_font)

        self.grid = QGridLayout()
        self.grid.setHorizontalSpacing(25)
        self.grid.setVerticalSpacing(50)
        self.grid.addWidget(self.ble_lbl, 0, 0)
        self.grid.addWidget(self.ble_btn_pass, 0, 1)
        self.grid.addWidget(self.ble_btn_fail, 0, 2)
        self.grid.addWidget(self.psoc_disconnect_lbl, 1, 0)
        self.grid.addWidget(self.psoc_disconnect_chkbx, 1, 1)
        self.grid.addWidget(self.pwr_cycle_lbl, 2, 0)
        self.grid.addWidget(self.pwr_cycle_chkbx, 2, 1)
        self.grid.addWidget(self.bt_comm_lbl, 3, 0)
        self.grid.addWidget(self.bt_comm_btn_pass, 3, 1)
        self.grid.addWidget(self.bt_comm_btn_fail, 3, 2)
        self.grid.addWidget(self.leds_lbl, 4, 0)
        self.grid.addWidget(self.leds_btn_pass, 4, 1)
        self.grid.addWidget(self.leds_btn_fail, 4, 2)
        self.grid.addLayout(self.psoc_layout, 5, 0)
        self.grid.addWidget(self.uart_wire_lbl, 6, 0)

        self.hbox = QHBoxLayout()
        self.hbox.addStretch()
        self.hbox.addLayout(self.grid)
        self.hbox.addStretch()

        self.layout = QVBoxLayout()
        self.layout.addStretch()
        self.layout.addLayout(self.hbox)
        self.layout.addStretch()

        self.setLayout(self.layout)
        self.setTitle("Cypress BLE")

    def initializePage(self):
        self.is_complete = False
        self.command_signal.connect(self.sm.send_command)
        self.complete_signal.connect(self.completeChanged)
        self.d505.button(QWizard.NextButton).setEnabled(False)

        self.sm.port_unavailable_signal.disconnect()
        self.sm.port_unavailable_signal.connect(self.port_warning)
        self.sm.no_port_sel.disconnect()
        self.sm.no_port_sel.connect(self.port_warning)

    def port_warning(self):
        """Creates a QMessagebox warning when no serial port selected."""
        QMessageBox.warning(self, "Warning!", "No serial port selected!")
        self.leds_lbl.setStyleSheet("QLabel {color: black}")
        self.leds_btn_pass.setEnabled(True)
        self.leds_btn_fail.setEnabled(True)
        self.psoc_pbar_lbl.setText("PSoC version")
        self.psoc_pbar.setRange(0, 1)
        self.psoc_pbar.setValue(0)

    def ble_pass(self):
        self.tu.ble_prog_status.setText("BLE Programming: PASS")
        self.tu.ble_prog_status.setStyleSheet(
            self.d505.status_style_pass)
        self.ble_lbl.setStyleSheet("QLabel {color: grey}")
        self.report.write_data("ble_prog", "", "PASS")
        self.ble_btn_pass.setEnabled(False)
        self.ble_btn_fail.setEnabled(False)

    def ble_fail(self):
        self.tu.ble_prog_status.setText("BLE Programming: FAIL")
        self.tu.ble_prog_status.setStyleSheet(
            self.d505.status_style_fail)
        self.ble_lbl.setStyleSheet("QLabel {color: grey}")
        self.report.write_data("ble_prog", "", "FAIL")
        self.ble_btn_pass.setEnabled(False)
        self.ble_btn_fail.setEnabled(False)

    def bt_comm_pass(self):
        self.tu.bluetooth_test_status.setText("Bluetooth Test: PASS")
        self.tu.bluetooth_test_status.setStyleSheet(
            self.d505.status_style_pass)
        self.bt_comm_lbl.setStyleSheet("QLabel {color: grey}")
        self.report.write_data("bt_comms", "", "PASS")
        self.bt_comm_btn_pass.setEnabled(False)
        self.bt_comm_btn_fail.setEnabled(False)

    def bt_comm_fail(self):
        self.tu.bluetooth_test_status.setText("Bluetooth Test: FAIL")
        self.tu.bluetooth_test_status.setStyleSheet(
            self.d505.status_style_fail)
        self.bt_comm_lbl.setStyleSheet("QLabel {color: grey}")
        self.report.write_data("bt_comms", "", "FAIL")
        self.bt_comm_btn_pass.setEnabled(False)
        self.bt_comm_btn_fail.setEnabled(False)

    def leds_pass(self):
        self.tu.led_test_status.setText("LED Test: PASS")
        self.tu.led_test_status.setStyleSheet(self.d505.status_style_pass)
        self.leds_lbl.setStyleSheet("QLabel {color: grey}")
        self.report.write_data("led_test", "", "PASS")
        self.leds_btn_pass.setEnabled(False)
        self.leds_btn_fail.setEnabled(False)
        self.psoc_version()

    def leds_fail(self):
        self.tu.led_test_status.setText("LED Test: FAIL")
        self.tu.led_test_status.setStyleSheet(self.d505.status_style_fail)
        self.leds_lbl.setStyleSheet("QLabel {color: grey}")
        self.report.write_data("led_test", "", "FAIL")
        self.leds_btn_pass.setEnabled(False)
        self.leds_btn_fail.setEnabled(False)
        self.psoc_version()

    def psoc_version(self):
        self.sm.data_ready.connect(self.parse_data)
        self.psoc_pbar.setRange(0, 0)
        self.psoc_pbar_lbl.setText("Checking PSoC version...")
        self.command_signal.emit("psoc-version")

    def parse_data(self, data):
        self.sm.data_ready.disconnect()
        pattern = r"([0-9)+.([0-9])+.([0-9])+"
        version = re.search(pattern, data)
        if (version):
            self.report.write_data("ble_ver", version.group(), "PASS")
        else:
            QMessageBox.warning(self, "PSOC Version", "Bad command response.")
            self.report.write_data("ble_ver", "", "FAIL")

        self.psoc_pbar.setRange(0, 1)
        self.psoc_pbar.setValue(1)
        self.psoc_pbar_lbl.setText("Received PSoC version.")
        self.is_complete = True
        self.complete_signal.emit()

    def isComplete(self):
        return self.is_complete
