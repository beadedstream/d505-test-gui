import utilities
import re
from PyQt5.QtWidgets import (
    QWizardPage, QWizard, QLabel, QVBoxLayout, QCheckBox, QGridLayout,
    QLineEdit, QProgressBar, QPushButton, QMessageBox, QHBoxLayout,
    QApplication)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal, QThread


class XmegaInterfaces(QWizardPage):
    """Fifth QWizard page. Tests Xmega programming interfaces."""
    complete_signal = pyqtSignal()
    command_signal = pyqtSignal(str)
    sleep_signal = pyqtSignal(int)
    imei_signal = pyqtSignal()
    flash_test_signal = pyqtSignal()
    gps_test_signal = pyqtSignal()
    serial_test_signal = pyqtSignal(str)
    rtc_test_signal = pyqtSignal()

    def __init__(self, d505, test_utility, serial_manager, model, report):
        super().__init__()

        self.d505 = d505
        self.tu = test_utility
        self.sm = serial_manager
        self.model = model
        self.report = report

        self.complete_signal.connect(self.completeChanged)
        self.command_signal.connect(self.sm.send_command)
        self.imei_signal.connect(self.sm.iridium_command)
        self.flash_test_signal.connect(self.sm.flash_test)
        self.gps_test_signal.connect(self.sm.gps_test)
        self.serial_test_signal.connect(self.sm.set_serial)
        self.rtc_test_signal.connect(self.sm.rtc_test)

        self.sm.flash_test_succeeded.connect(self.flash_pass)
        self.sm.flash_test_failed.connect(self.flash_fail)
        self.sm.gps_test_succeeded.connect(self.gps_pass)
        self.sm.gps_test_failed.connect(self.gps_fail)
        self.sm.serial_test_succeeded.connect(self.serial_pass)
        self.sm.serial_test_failed.connect(self.serial_fail)
        self.sm.rtc_test_succeeded.connect(self.rtc_pass)
        self.sm.rtc_test_failed.connect(self.rtc_fail)

        self.system_font = QApplication.font().family()
        self.label_font = QFont(self.system_font, 12)

        self.xmega_lbl = QLabel("Testing Xmega interfaces.")
        self.xmega_lbl.setFont(self.label_font)
        self.xmega_pbar = QProgressBar()

        self.repeat_tests = QPushButton("Repeat Tests")
        self.repeat_tests.setMaximumWidth(150)
        self.repeat_tests.setFont(self.label_font)
        self.repeat_tests.setStyleSheet("background-color: grey")
        self.repeat_tests.clicked.connect(self.initializePage)

        self.layout = QVBoxLayout()
        self.layout.addStretch()
        self.layout.addWidget(self.xmega_lbl)
        self.layout.addWidget(self.xmega_pbar)
        self.layout.addSpacing(230)
        self.layout.addWidget(self.repeat_tests)
        self.layout.addStretch()
        self.layout.setAlignment(Qt.AlignHCenter)

        self.setLayout(self.layout)
        self.setTitle("XMega Interfaces")

    def initializePage(self):
        self.is_complete = False
        self.page_pass_status = True
        self.sm.data_ready.connect(self.check_serial)

        self.xmega_pbar.setRange(0, 9)
        self.xmega_pbar.setValue(0)
        self.xmega_pbar_counter = 0

        self.d505.button(QWizard.NextButton).setEnabled(False)
        self.repeat_tests.setEnabled(False)
        self.xmega_lbl.setText("Checking serial number. . .")

        self.tu.xmega_inter_status.setText("Xmega Interfaces:_____")

        self.command_signal.emit(f"serial {self.tu.pcba_sn}")

    def page_pass(self):
        self.tu.xmega_inter_status.setText("Xmega Interfaces: PASS")
        self.tu.xmega_inter_status.setStyleSheet(
            self.d505.status_style_pass)

    def page_fail(self):
        self.tu.xmega_inter_status.setText("Xmega Interfaces: FAIL")
        self.tu.xmega_inter_status.setStyleSheet(
            self.d505.status_style_fail)
        self.page_pass_status = False

    def check_serial(self):
        self.sm.data_ready.disconnect()
        self.sm.data_ready.connect(self.verify_batv)
        self.serial_test_signal.emit(self.tu.pcba_sn)

    def serial_pass(self, serial_num):
        self.report.write_data("serial_match", serial_num, "PASS")
        self.xmega_pbar_counter += 1
        self.xmega_pbar.setValue(self.xmega_pbar_counter)
        self.xmega_lbl.setText("Verifying battery voltage. . .")
        self.command_signal.emit("bat_v")

    def serial_fail(self, data):
        self.report.write_data("serial_match", data, "FAIL")
        self.xmega_pbar_counter += 1
        self.xmega_pbar.setValue(self.xmega_pbar_counter)
        self.page_fail()
        self.xmega_lbl.setText("Verifying battery voltage. . .")
        self.command_signal.emit("bat_v")

    def verify_batv(self, data):
        self.sm.data_ready.disconnect()
        self.sm.data_ready.connect(self.verify_modem)
        pattern = "([0-9])+.([0-9])+"
        if (re.search(pattern, data)):
            bat_v = float(re.search(pattern, data).group())
            value_pass = self.model.compare_to_limit("bat_v", bat_v)
            if (value_pass):
                self.report.write_data("bat_v", bat_v, "PASS")
            else:
                self.report.write_data("bat_v", bat_v, "FAIL")
                self.page_fail()
        else:
            QMessageBox.warning(self, "BatV Error",
                                "Serial error or bad value")
            self.report.write_data("bat_v", "", "FAIL")
            self.page_fail()

        self.xmega_pbar_counter += 1
        self.xmega_pbar.setValue(self.xmega_pbar_counter)
        self.xmega_lbl.setText("Checking IMEI number. . .")
        self.imei_signal.emit()

    def verify_modem(self, data):
        self.sm.data_ready.disconnect()
        self.sm.data_ready.connect(self.verify_board_id)
        pattern = "([0-9]){15}"
        m = re.search(pattern, data)
        if (m):
            imei = m.group()
            if (imei == self.tu.settings.value("iridium_imei")):
                self.report.write_data("iridium_match", imei, "PASS")
            else:
                self.report.write_data("iridium_match", imei, "FAIL")
                self.page_fail()
        else:
            QMessageBox.warning(self, "Iridium Modem Error",
                                "Serial error or bad value")
            self.report.write_data("iridium_match", "", "FAIL")
            self.page_fail()

        self.xmega_pbar_counter += 1
        self.xmega_pbar.setValue(self.xmega_pbar_counter)
        self.xmega_lbl.setText("Verifying board id. . .")
        self.command_signal.emit("board_id")

    def verify_board_id(self, data):
        self.sm.data_ready.disconnect()
        self.sm.data_ready.connect(self.verify_tac)
        pattern = r"([0-9A-Fa-f][0-9A-Fa-f]\s+){7}([0-9A-Fa-f][0-9A-Fa-f]){1}"
        if (re.search(pattern, data)):
            board_id = re.search(pattern, data).group()
            if (board_id[-2:] == "28"):
                self.report.write_data("board_id", board_id, "PASS")
            else:
                self.report.write_data("board_id", board_id, "FAIL")
                self.page_fail()
        else:
            QMessageBox.warning(self, "Board ID Error",
                                "Serial error or bad value")
            self.report.write_data("board_id", "", "FAIL")
            self.page_fail()

        self.xmega_pbar_counter += 1
        self.xmega_pbar.setValue(self.xmega_pbar_counter)
        self.xmega_lbl.setText("Checking TAC ports. . .")
        self.command_signal.emit("tac-get-info")

    def verify_tac(self, data):
        data = data.split("\n")

        try:
            port1 = data[2][0:8]
            port2 = data[7][0:8]
            port3 = data[12][0:8]
            port4 = data[17][0:8]

            if not (port1 == self.tu.settings.value("port1_tac_id") and
                    port2 == self.tu.settings.value("port2_tac_id") and
                    port3 == self.tu.settings.value("port3_tac_id") and
                    port4 == self.tu.settings.value("port4_tac_id")):
                self.report.write_data("tac_connected", "", "FAIL")
                self.page_fail()
            else:
                self.report.write_data("tac_connected", "", "PASS")

        except IndexError:
            QMessageBox.warning(self, "TAC Connection",
                                "Serial error or bad value")
            self.report.write_data("tac_connected", "", "FAIL")
            self.page_fail()

        self.xmega_pbar_counter += 1
        self.xmega_pbar.setValue(self.xmega_pbar_counter)
        self.xmega_lbl.setText("Checking flash. . .")
        self.flash_test_signal.emit()

    def flash_pass(self):
        self.sm.data_ready.disconnect()
        self.sm.data_ready.connect(self.snow_depth)
        self.xmega_pbar_counter += 1
        self.xmega_pbar.setValue(self.xmega_pbar_counter)
        self.report.write_data("flash_comms", "", "PASS")
        self.xmega_lbl.setText("Testing alarm. . .")
        self.rtc_test_signal.emit()

    def flash_fail(self):
        self.sm.data_ready.disconnect()
        self.sm.data_ready.connect(self.snow_depth)
        QMessageBox.warning(self, "Flash", "Flash test failed!")
        self.report.write_data("flash_comms", "", "FAIL")
        self.xmega_pbar_counter += 1
        self.xmega_pbar.setValue(self.xmega_pbar_counter)
        self.xmega_lbl.setText("Testing alarm. . .")
        self.page_fail()
        self.rtc_test_signal.emit()

    def rtc_pass(self):
        self.xmega_pbar_counter += 1
        self.xmega_pbar.setValue(self.xmega_pbar_counter)
        self.report.write_data("rtc_alarm", "", "PASS")
        self.xmega_lbl.setText("Checking GPS connection. . .")
        self.gps_test_signal.emit()

    def rtc_fail(self):
        self.xmega_pbar_counter += 1
        self.xmega_pbar.setValue(self.xmega_pbar_counter)
        self.report.write_data("rtc_alarm", "", "FAIL")
        self.xmega_lbl.setText("Checking GPS connection. . .")
        self.page_fail()
        self.gps_test_signal.emit()

    def gps_pass(self):
        self.xmega_pbar_counter += 1
        self.xmega_pbar.setValue(self.xmega_pbar_counter)
        self.report.write_data("gps_comms", "", "PASS")
        self.xmega_lbl.setText("Checking range finder. . .")
        self.command_signal.emit("snow-depth")

    def gps_fail(self):
        self.xmega_pbar_counter += 1
        self.xmega_pbar.setValue(self.xmega_pbar_counter)
        self.report.write_data("gps_comms", "", "FAIL")
        self.xmega_lbl.setText("Checking range finder. . .")
        self.page_fail()
        self.command_signal.emit("snow-depth")

    def snow_depth(self, data):
        self.sm.data_ready.disconnect()
        pattern = r"[0-9]+\scm"
        if (re.search(pattern, data)):
            value_string = re.search(pattern, data).group()
            # Get rid of units
            distance = value_string[:-3]
            self.report.write_data("sonic_connected", distance, "PASS")
        else:
            self.report.write_data("sonic_connected", "", "FAIL")
            QMessageBox.warning(self, "Sonic Connection",
                                "Serial error or bad value")
            self.page_fail()
        self.xmega_pbar_counter += 1
        self.xmega_pbar.setValue(self.xmega_pbar_counter)
        self.is_complete = True
        self.xmega_lbl.setText("Complete.")
        self.complete_signal.emit()

    def isComplete(self):
        if self.is_complete:
            self.repeat_tests.setEnabled(True)
            if self.page_pass_status:
                self.page_pass()

        return self.is_complete
