import re
import os.path
import time
from PyQt5.QtWidgets import (
    QWizardPage, QWizard, QLabel, QVBoxLayout, QCheckBox, QGridLayout,
    QLineEdit, QProgressBar, QPushButton, QMessageBox, QHBoxLayout,
    QApplication
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal


class D505(QWizard):
    status_style_pass = """QLabel {background: #8cff66;
                        border: 2px solid grey; font-size: 20px}"""
    status_style_fail = """QLabel {background: #ff5c33;
                        border: 2px solid grey; font-size: 20px}"""

    def __init__(self, test_utility, model, serial_manager, report):
        super().__init__()
        self.abort_btn = QPushButton("Abort")
        self.abort_btn.clicked.connect(self.abort)
        self.setButton(QWizard.CustomButton1, self.abort_btn)
        self.button(QWizard.FinishButton).clicked.connect(self.finish)

        qbtn_layout = [QWizard.Stretch, QWizard.NextButton,
                       QWizard.FinishButton, QWizard.CustomButton1]
        self.setButtonLayout(qbtn_layout)

        self.button(QWizard.NextButton).setEnabled(False)

        # This fixes a bug in the default style which hides the QWizard
        # buttons until the window is resized.
        self.setWizardStyle(0)

        setup_id = self.addPage(Setup(self, test_utility, serial_manager,
                                      model, report))
        watchdog_id = self.addPage(WatchDog(self, test_utility, serial_manager,
                                            model, report))
        one_wire_id = self.addPage(OneWireMaster(self, test_utility,
                                                 serial_manager, report))
        cypress_id = self.addPage(CypressBLE(self, test_utility,
                                             serial_manager, report))
        xmega_id = self.addPage(XmegaInterfaces(self, test_utility,
                                                serial_manager, model, report))
        uart_id = self.addPage(UartPower(self, test_utility, serial_manager,
                                         report))
        deep_sleep_id = self.addPage(DeepSleep(self, test_utility,
                                               serial_manager, model, report))
        final_id = self.addPage(FinalPage(test_utility, report))

        self.setup_page = self.page(setup_id)
        self.watchdog_page = self.page(watchdog_id)
        self.one_wire_page = self.page(one_wire_id)
        self.cypress_page = self.page(cypress_id)
        self.xmega_page = self.page(xmega_id)
        self.uart_page = self.page(uart_id)
        self.deep_sleep_page = self.page(deep_sleep_id)
        self.final_page = self.page(final_id)

        self.tu = test_utility
        self.report = report

    def abort(self):
        msg = "Are you sure you want to cancel the test?"
        confirmation = QMessageBox.question(self, "Abort Test?", msg,
                                            QMessageBox.Yes,
                                            QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            self.tu.initUI()
        else:
            pass

    def finish(self):
        self.tu.initUI()
        report_file_path = self.tu.settings.value("report_file_path")
        self.report.set_file_location(report_file_path)
        self.report.generate_report()

    def checked(lbl, chkbx):
        if chkbx.isChecked():
            chkbx.setEnabled(False)
            lbl.setStyleSheet("QLabel {color: grey}")


class Setup(QWizardPage):
    command_signal = pyqtSignal(str)
    complete_signal = pyqtSignal()

    def __init__(self, d505, test_utility, serial_manager, model, report):
        LINE_EDIT_WIDTH = 75
        VERT_SPACING = 25
        RIGHT_SPACING = 125
        LEFT_SPACING = 125

        super().__init__()

        self.d505 = d505
        self.tu = test_utility
        self.sm = serial_manager
        self.model = model
        self.report = report

        self.system_font = QApplication.font().family()
        self.label_font = QFont(self.system_font, 14)
        self.step_a_lbl = QLabel("Connect all peripherals to DUT"
                                 " and apply input power:", self)
        self.step_a_lbl.setFont(self.label_font)
        self.step_a_chkbx = QCheckBox()
        self.step_a_chkbx.setStyleSheet("QCheckBox::indicator {width: 20px; \
                                        height: 20px}")
        self.step_a_chkbx.clicked.connect(
            lambda: D505.checked(self.step_a_lbl, self.step_a_chkbx))

        self.step_b_lbl = QLabel("Record Input voltage: ", self)
        self.step_b_lbl.setFont(self.label_font)
        self.step_b_input = QLineEdit()
        self.step_b_input.setFixedWidth(LINE_EDIT_WIDTH)
        self.step_b_unit = QLabel("V")

        self.step_c_lbl = QLabel("Record input current: ", self)
        self.step_c_lbl.setFont(self.label_font)
        self.step_c_input = QLineEdit()
        self.step_c_input.setFixedWidth(LINE_EDIT_WIDTH)
        self.step_c_unit = QLabel("mA")

        self.step_d_lbl = QLabel("Record 2V supply (right side of C49):", self)
        self.step_d_lbl.setFont(self.label_font)
        self.step_d_input = QLineEdit()
        self.step_d_input.setFixedWidth(LINE_EDIT_WIDTH)
        self.step_d_unit = QLabel("V")

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.parse_values)
        self.submit_button.setFixedWidth(LINE_EDIT_WIDTH)

        self.app0_pbar_lbl = QLabel("Set 'app 0'.")
        self.app0_pbar_lbl.setFont(self.label_font)
        self.app0_pbar = QProgressBar()

        self.btn_layout = QHBoxLayout()
        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.submit_button)
        self.btn_layout.addSpacing(RIGHT_SPACING + 5)

        self.step_a_layout = QHBoxLayout()
        self.step_a_layout.addSpacing(LEFT_SPACING)
        self.step_a_layout.addWidget(self.step_a_lbl)
        self.step_a_layout.addStretch()
        self.step_a_layout.addWidget(self.step_a_chkbx)
        self.step_a_layout.addSpacing(RIGHT_SPACING)

        self.step_b_layout = QHBoxLayout()
        self.step_b_layout.addSpacing(LEFT_SPACING)
        self.step_b_layout.addWidget(self.step_b_lbl)
        self.step_b_layout.addStretch()
        self.step_b_layout.addWidget(self.step_b_input)
        self.step_b_layout.addWidget(self.step_b_unit)
        self.step_b_layout.addSpacing(RIGHT_SPACING - 8)

        self.step_c_layout = QHBoxLayout()
        self.step_c_layout.addSpacing(LEFT_SPACING)
        self.step_c_layout.addWidget(self.step_c_lbl)
        self.step_c_layout.addStretch()
        self.step_c_layout.addWidget(self.step_c_input)
        self.step_c_layout.addWidget(self.step_c_unit)
        self.step_c_layout.addSpacing(RIGHT_SPACING - 18)

        self.step_d_layout = QHBoxLayout()
        self.step_d_layout.addSpacing(LEFT_SPACING)
        self.step_d_layout.addWidget(self.step_d_lbl)
        self.step_d_layout.addStretch()
        self.step_d_layout.addWidget(self.step_d_input)
        self.step_d_layout.addWidget(self.step_d_unit)
        self.step_d_layout.addSpacing(RIGHT_SPACING - 8)

        self.layout = QVBoxLayout()
        self.layout.addStretch()
        self.layout.addLayout(self.step_a_layout)
        self.layout.addSpacing(VERT_SPACING)
        self.layout.addLayout(self.step_b_layout)
        self.layout.addSpacing(VERT_SPACING)
        self.layout.addLayout(self.step_c_layout)
        self.layout.addSpacing(VERT_SPACING)
        self.layout.addLayout(self.step_d_layout)
        self.layout.addSpacing(VERT_SPACING)
        self.layout.addLayout(self.btn_layout)
        self.layout.addSpacing(VERT_SPACING)
        self.layout.addWidget(self.app0_pbar_lbl)
        self.layout.addSpacing(VERT_SPACING)
        self.layout.addWidget(self.app0_pbar)
        self.layout.addStretch()

        # group = QGroupBox()
        # group.setLayout(self.layout)

        # vbox = QVBoxLayout()
        # vbox.addWidget(group)
        # vbox.addStretch()

        self.setLayout(self.layout)
        self.setTitle("Setup")

    def initializePage(self):
        # Flag for tracking page completion and allowing the next button
        # to be re-enabled.
        self.command_signal.connect(self.sm.send_command)
        self.sm.data_ready.connect(self.app_off)
        self.is_complete = False
        self.complete_signal.connect(self.completeChanged)

    def parse_values(self):
        limits = ["Input Voltage", "Input Current", "2V Supply"]
        values = []
        try:
            values.append(float(self.step_b_input.text()))
            values.append(float(self.step_c_input.text()))
            values.append(float(self.step_d_input.text()))
        except ValueError:
            QMessageBox.warning(self, "Warning", "Bad input value!")
            return
        for limit, value in zip(limits, values):
            self.report.write_data(limit, value,
                                   self.model.compare_to_limit(limit, value))

        # Update status values
        self.tu.input_v_status.setText(f"Input Voltage: {values[0]} V")
        self.tu.input_i_status.setText(f"Input Current: {values[1]} mA")
        self.tu.supply_2v_status.setText(f"2V Supply: {values[2]} V")

        if (self.model.compare_to_limit(limits[0], values[0])):
            self.tu.input_v_status.setStyleSheet(
                D505.status_style_pass)
        else:
            self.tu.input_v_status.setStyleSheet(
                D505.status_style_fail)
        if (self.model.compare_to_limit(limits[1], values[1])):
            self.tu.input_i_status.setStyleSheet(
                D505.status_style_pass)
        else:
            self.tu.input_i_status.setStyleSheet(
                D505.status_style_fail)
        if (self.model.compare_to_limit(limits[2], values[2])):
            self.tu.supply_2v_status.setStyleSheet(
                D505.status_style_pass)
        else:
            self.tu.supply_2v_status.setStyleSheet(
                D505.status_style_fail)
        self.app0_pbar.setRange(0, 0)
        self.app0_pbar_lbl.setText("Sending 'app 0' command...")
        self.command_signal.emit("app 0")

    def app_off(self, data):
        self.sm.data_ready.disconnect()
        self.app0_pbar.setRange(0, 1)
        self.app0_pbar.setValue(1)
        self.app0_pbar_lbl.setText("Sent 'app 0' command.")
        self.is_complete = True
        self.complete_signal.emit()
        self.submit_button.setEnabled(False)

    def isComplete(self):
        return self.is_complete


class WatchDog(QWizardPage):
    command_signal = pyqtSignal(str)
    sleep_signal = pyqtSignal(int)
    complete_signal = pyqtSignal()

    def __init__(self, d505, test_utility, serial_manager, model, report):
        super().__init__()

        self.d505 = d505
        self.tu = test_utility
        self.sm = serial_manager
        self.report = report
        self.model = model

        self.system_font = QApplication.font().family()
        self.label_font = QFont(self.system_font, 14)

        self.batch_lbl = QLabel("Run Xmega programming batch file and verify"
                                " the programming was successful.  ")
        self.batch_lbl.setFont(self.label_font)
        self.batch_chkbx = QCheckBox()
        self.batch_chkbx.setStyleSheet("QCheckBox::indicator {width: 20px; \
                                        height: 20px}")
        self.batch_chkbx.clicked.connect(
            lambda: D505.checked(self.batch_lbl, self.batch_chkbx))

        self.xmega_disconnect_lbl = QLabel("Remove Xmega programmer from "
                                           "connector J2")
        self.xmega_disconnect_lbl.setFont(self.label_font)
        self.xmega_disconnect_chkbox = QCheckBox()
        self.xmega_disconnect_chkbox.setStyleSheet("QCheckBox::indicator \
                                                   {width: 20px; \
                                                   height: 20px}")
        self.xmega_disconnect_chkbox.clicked.connect(self.reset_watchdog)
        self.xmega_disconnect_chkbox.clicked.connect(self.start_uart_tests)
        self.xmega_disconnect_chkbox.clicked.connect(self.update_progressbar)

        self.watchdog_lbl = QLabel("Resetting watchdog...")
        self.watchdog_lbl.setFont(self.label_font)
        self.watchdog_pbar = QProgressBar()
        self.watchdog_pbar.setRange(0, 1)

        self.supply_5v_input_lbl = QLabel("Measure and record the 5 V supply "
                                          "(bottom side of C55):")
        self.supply_5v_input_lbl.setFont(self.label_font)
        self.supply_5v_input = QLineEdit()
        self.supply_5v_input.setEnabled(False)
        self.supply_5v_unit = QLabel("V")
        self.supply_5v_unit.setFont(self.label_font)
        self.supply_5v_input_btn = QPushButton("Submit")
        self.supply_5v_input_btn.setEnabled(False)
        self.supply_5v_input_btn.clicked.connect(self.user_value_handler)

        self.supply_5v_lbl = QLabel("Testing supply 5v...")
        self.supply_5v_lbl.setFont(self.label_font)
        self.supply_5v_pbar = QProgressBar()
        self.supply_5v_pbar.setRange(0, 1)

        self.batch_layout = QHBoxLayout()
        self.batch_layout.addStretch()
        self.batch_layout.addWidget(self.batch_lbl)
        self.batch_layout.addWidget(self.batch_chkbx)
        self.batch_layout.addStretch()

        self.xmega_disconnect_layout = QHBoxLayout()
        self.xmega_disconnect_layout.addStretch()
        self.xmega_disconnect_layout.addWidget(self.xmega_disconnect_lbl)
        self.xmega_disconnect_layout.addWidget(self.xmega_disconnect_chkbox)
        self.xmega_disconnect_layout.addSpacing(288)
        self.xmega_disconnect_layout.addStretch()

        self.supply_5v_layout = QHBoxLayout()
        self.supply_5v_layout.addStretch()
        self.supply_5v_layout.addWidget(self.supply_5v_input_lbl)
        self.supply_5v_layout.addWidget(self.supply_5v_input)
        self.supply_5v_layout.addWidget(self.supply_5v_unit)
        self.supply_5v_layout.addWidget(self.supply_5v_input_btn)
        self.supply_5v_layout.addStretch()

        self.layout = QVBoxLayout()
        self.layout.addStretch()
        self.layout.addLayout(self.batch_layout)
        self.layout.addSpacing(50)
        self.layout.addLayout(self.xmega_disconnect_layout)
        self.layout.addStretch()
        self.layout.addWidget(self.watchdog_lbl)
        self.layout.addWidget(self.watchdog_pbar)
        self.layout.addStretch()
        self.layout.addLayout(self.supply_5v_layout)
        self.layout.addStretch()
        self.layout.addWidget(self.supply_5v_lbl)
        self.layout.addSpacing(25)
        self.layout.addWidget(self.supply_5v_pbar)
        self.layout.addStretch()
        self.layout.setAlignment(Qt.AlignHCenter)

        self.setLayout(self.layout)
        self.setTitle("Watchdog Reset")

    def initializePage(self):
        self.command_signal.connect(self.sm.send_command)
        self.sleep_signal.connect(self.sm.sleep)
        self.complete_signal.connect(self.completeChanged)
        self.d505.button(QWizard.NextButton).setEnabled(False)
        self.d505.button(QWizard.NextButton).setAutoDefault(False)
        # Flag for tracking page completion and allowing the next button
        # to be re-enabled.
        self.is_complete = False

    def isComplete(self):
        if self.is_complete:
            self.d505.button(QWizard.CustomButton1).setDefault(False)
            self.d505.button(QWizard.NextButton).setDefault(True)
        return self.is_complete

    def start_uart_tests(self):
        if self.xmega_disconnect_chkbox.isChecked():
            self.xmega_disconnect_chkbox.setEnabled(False)
            self.xmega_disconnect_lbl.setStyleSheet("QLabel {color: grey}")

    def update_progressbar(self):
        self.watchdog_pbar.setRange(0, 0)

    def reset_watchdog(self):
        self.sm.data_ready.connect(self.watchdog_handler)
        self.command_signal.emit("watchdog")

    def watchdog_handler(self, data):
        self.sm.data_ready.disconnect()
        self.sm.data_ready.connect(self.uart_5v1_handler)
        self.watchdog_pbar.setRange(0, 1)
        self.watchdog_pbar.setValue(1)
        bl_pattern = "bootloader version .*\n"
        app_pattern = "datalogger version .*\n"
        try:
            bootloader_version = re.search(bl_pattern, data).group()
            app_version = re.search(app_pattern, data).group()
        except AttributeError:
            QMessageBox.warning(self, "Warning",
                                "Error in serial data, try this step again")
            return
        bootloader_version = bootloader_version.strip("\r\n")
        app_version = app_version.strip("\r\n")
        self.report.write_data("Xmega Bootloader Version", bootloader_version,
                               True)
        self.report.write_data("Xmega App Version", app_version, True)
        self.command_signal.emit("5V 1")

    def uart_5v1_handler(self, data):
        self.sm.data_ready.disconnect()
        self.supply_5v_input.setEnabled(True)
        self.supply_5v_input_btn.setEnabled(True)

    def user_value_handler(self):
        self.sm.data_ready.connect(self.uart_5v_handler)
        self.supply_5v_input.setEnabled(False)
        self.supply_5v_pbar.setRange(0, 0)
        try:
            supply_5v_val = float(self.supply_5v_input.text())
        except ValueError:
            QMessageBox.warning(self, "Warning", "Bad Input Value!")
            return
        value_pass = self.model.compare_to_limit("5V Supply",
                                                 supply_5v_val)
        self.report.write_data("5V Supply", supply_5v_val, value_pass)
        self.tu.supply_5v_status.setText(
            f"5V Supply: {supply_5v_val} V")
        if (value_pass):
            self.tu.supply_5v_status.setStyleSheet(
                D505.status_style_pass)
        else:
            self.tu.supply_5v_status.setStyleSheet(
                D505.status_style_fail)
        self.command_signal.emit("5V")
        self.supply_5v_input_btn.setEnabled(False)

    def uart_5v_handler(self, data):
        self.sm.data_ready.disconnect()
        self.sm.data_ready.connect(self.uart_5v0_handler)
        data = data.strip("\n").split("\n")
        try:
            uart_5v_val = float(data[1].strip("\n"))
        except ValueError:
            QMessageBox.warning(self, "Warning",
                                "Error in serial data, try this step again")
            return

        value_pass = self.model.compare_to_limit("5V UART",
                                                 uart_5v_val)
        self.report.write_data("5V UART", uart_5v_val, value_pass)

        self.tu.uart_5v_status.setText(f"5V UART {uart_5v_val} V")
        if (value_pass):
            self.tu.uart_5v_status.setStyleSheet(
                D505.status_style_pass)
        else:
            self.tu.uart_5v_status.setStyleSheet(
                D505.status_style_fail)
        self.command_signal.emit("5V 0")

    def uart_5v0_handler(self, data):
        self.sm.data_ready.disconnect()
        self.sm.sleep_finished.connect(self.sleep_handler)
        self.sleep_signal.emit(20)

    def sleep_handler(self):
        self.sm.sleep_finished.disconnect()
        self.sm.data_ready.connect(self.final_5v_handler)
        self.command_signal.emit("5V")

    def final_5v_handler(self, data):
        self.sm.data_ready.disconnect()
        self.supply_5v_pbar.valueChanged.connect(self.completeChanged)
        self.supply_5v_pbar.setRange(0, 1)
        self.supply_5v_pbar.setValue(1)
        data = data.strip("\n").split("\n")
        try:
            uart_off_val = float(data[1].strip("\n"))
        except ValueError:
            QMessageBox.warning(self, "Warning",
                                "Error in serial data, try this step again")
            return
        value_pass = self.model.compare_to_limit("UART Off", uart_off_val)
        self.report.write_data("UART Off", uart_off_val, value_pass)

        self.tu.uart_off_status.setText(
            f"UART Off: {uart_off_val} V")
        if (value_pass):
            self.tu.uart_off_status.setStyleSheet(
                D505.status_style_pass)
        else:
            self.tu.uart_off_status.setStyleSheet(
                D505.status_style_fail)
        self.is_complete = True
        self.complete_signal.emit()


class OneWireMaster(QWizardPage):
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

        self.system_font = QApplication.font().family()
        self.label_font = QFont(self.system_font, 14)

        self.one_wire_lbl = QLabel()
        self.one_wire_lbl.setFont(self.label_font)
        self.one_wire_pbar = QProgressBar()

        self.layout = QVBoxLayout()
        self.layout.addStretch()
        self.layout.addWidget(self.one_wire_lbl)
        self.layout.addWidget(self.one_wire_pbar)
        self.layout.addStretch()

        self.setLayout(self.layout)
        self.setTitle("Program 1-Wire Master")

    def initializePage(self):
        self.pbar_value = 0
        self.is_complete = False
        self.command_signal.connect(self.sm.send_command)
        self.file_write_signal.connect(self.sm.write_hex_file)
        self.reprogram_signal.connect(self.sm.reprogram_one_wire)
        self.one_wire_test_signal.connect(self.sm.one_wire_test)
        self.complete_signal.connect(self.completeChanged)
        self.sm.data_ready.connect(self.send_hex_file)
        self.sm.line_written.connect(self.update_pbar)
        self.d505.button(QWizard.NextButton).setEnabled(False)
        self.program()

    def isComplete(self):
        return self.is_complete

    def program(self):
        self.one_wire_pbar.setRange(0, 0)
        self.reprogram_signal.emit()
        self.one_wire_lbl.setText("Erasing flash. . .")

    def send_hex_file(self, data):
        self.sm.data_ready.disconnect()
        self.sm.data_ready.connect(self.data_parser)
        self.one_wire_pbar.setRange(0, 545)
        # Check for response from board before proceeding
        pattern = "download hex records now..."
        if (re.search(pattern, data)):
            hex_file_path = self.tu.settings.value("hex_file_path")
            if (os.path.isfile(hex_file_path)):
                self.one_wire_lbl.setText("Programming 1-wire master. . .")
                self.file_write_signal.emit(hex_file_path)
            else:
                QMessageBox.warning(self, "No hex file set or bad file path.")
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
        pattern = "1WireMaster .*\n"
        at_version = re.search(pattern, data)
        if (at_version):
            at_version_val = at_version.group().strip("\r\n")
            self.report.write_data("ATtiny Version", at_version_val, True)
            self.one_wire_lbl.setText("Version recorded.")
            self.tu.xmega_prog_status.setText(
                "Xmega Programming: PASS")
            self.tu.xmega_prog_status.setStyleSheet(
                D505.status_style_pass)
        else:
            self.report.write_data("ATtiny Version", "N/A", False)
            self.tu.xmega_prog_status.setText(
                "Xmega Programming: FAIL")
            self.tu.xmega_prog_status.setStyleSheet(
                D505.status_style_fail)
            QMessageBox.warning(self, "XMega3", "Bad command response.")

        self.is_complete = True
        self.complete_signal.emit()


class CypressBLE(QWizardPage):
    command_signal = pyqtSignal(str)
    complete_signal = pyqtSignal()

    def __init__(self, d505, test_utility, serial_manager, report):
        super().__init__()

        self.d505 = d505
        self.tu = test_utility
        self.sm = serial_manager
        self.report = report

        self.system_font = QApplication.font().family()
        self.label_font = QFont(self.system_font, 14)

        self.ble_lbl = QLabel("Run the Cypress programming utility to "
                              "program the CYBLE-224116 BLE module.")
        self.ble_lbl.setFont(QFont(self.system_font, 12))
        self.ble_btn_pass = QPushButton("PASS")
        self.ble_btn_pass.setMaximumWidth(75)
        self.ble_btn_fail = QPushButton("FAIL")
        self.ble_btn_fail.setMaximumWidth(75)
        self.ble_btn_pass.clicked.connect(self.ble_pass)
        self.ble_btn_fail.clicked.connect(self.ble_fail)

        self.psoc_disconnect_lbl = QLabel("Disconnect the PSoC programmer "
                                          "from J1.")
        self.psoc_disconnect_lbl.setFont(QFont(self.system_font, 12))
        self.psoc_disconnect_chkbx = QCheckBox()
        self.psoc_disconnect_chkbx.setStyleSheet("QCheckBox::indicator \
                                                 {width: 20px; height: 20px}")
        self.psoc_disconnect_chkbx.clicked.connect(
            lambda: D505.checked(self.psoc_disconnect_lbl,
                                 self.psoc_disconnect_chkbx))

        self.pwr_cycle_lbl = QLabel("Power cycle DUT (unplug/replug both "
                                    "battery and red wire from UART).")
        self.pwr_cycle_lbl.setFont(QFont(self.system_font, 12))
        self.pwr_cycle_chkbx = QCheckBox()
        self.pwr_cycle_chkbx.setStyleSheet("QCheckBox::indicator {width: 20px; \
                                        height: 20px}")
        self.pwr_cycle_chkbx.clicked.connect(
            lambda: D505.checked(self.pwr_cycle_lbl, self.pwr_cycle_chkbx))

        self.bt_comm_lbl = QLabel("Verify communication to 505 with "
                                  "bluetooth device.")
        self.bt_comm_lbl.setFont(QFont(self.system_font, 12))
        self.bt_comm_btn_pass = QPushButton("PASS")
        self.bt_comm_btn_pass.setMaximumWidth(75)
        self.bt_comm_btn_fail = QPushButton("FAIL")
        self.bt_comm_btn_fail.setMaximumWidth(75)
        self.bt_comm_btn_pass.clicked.connect(self.bt_comm_pass)
        self.bt_comm_btn_fail.clicked.connect(self.bt_comm_fail)
        self.bt_comm_btn_pass.clicked.connect(self.psoc_version)
        self.bt_comm_btn_fail.clicked.connect(self.psoc_version)

        self.psoc_pbar = QProgressBar()
        self.psoc_pbar_lbl = QLabel("PSoC version")
        self.psoc_pbar_lbl.setFont(QFont(self.system_font, 12))

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
        self.grid.addWidget(QLabel(), 4, 0)
        self.grid.addWidget(self.psoc_pbar_lbl, 5, 0)
        self.grid.addWidget(self.psoc_pbar, 6, 0)

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

    def ble_pass(self):
        self.tu.ble_prog_status.setText("BLE Programming: PASS")
        self.tu.ble_prog_status.setStyleSheet(
            D505.status_style_pass)
        self.ble_lbl.setStyleSheet("QLabel {color: grey}")
        self.ble_btn_pass.setEnabled(False)
        self.ble_btn_fail.setEnabled(False)

    def ble_fail(self):
        self.tu.ble_prog_status.setText("BLE Programming: FAIL")
        self.tu.ble_prog_status.setStyleSheet(
            D505.status_style_fail)
        self.ble_lbl.setStyleSheet("QLabel {color: grey}")
        self.ble_btn_pass.setEnabled(False)
        self.ble_btn_fail.setEnabled(False)

    def bt_comm_pass(self):
        self.tu.bluetooth_test_status.setText("Bluetooth Test: PASS")
        self.tu.bluetooth_test_status.setStyleSheet(
            D505.status_style_pass)
        self.bt_comm_lbl.setStyleSheet("QLabel {color: grey}")
        self.bt_comm_btn_pass.setEnabled(False)
        self.bt_comm_btn_fail.setEnabled(False)

    def bt_comm_fail(self):
        self.tu.bluetooth_test_status.setText("Bluetooth Test: FAIL")
        self.tu.bluetooth_test_status.setStyleSheet(
            D505.status_style_fail)
        self.bt_comm_lbl.setStyleSheet("QLabel {color: grey}")
        self.bt_comm_btn_pass.setEnabled(False)
        self.bt_comm_btn_fail.setEnabled(False)

    def psoc_version(self):
        self.sm.data_ready.connect(self.parse_data)
        self.psoc_pbar.setRange(0, 0)
        self.psoc_pbar_lbl.setText("Checking PSoC version...")
        self.command_signal.emit("psoc-version")

    def parse_data(self, data):
        self.sm.data_ready.disconnect()
        pattern = "([0-9)+.([0-9])+.([0-9])+"
        version = re.search(pattern, data)
        if (version):
            self.report.write_data("BLE Version", version.group(), True)
        else:
            QMessageBox.warning(self, "PSOC Version", "Bad command response.")
            self.report.write_data("BLE Version", "NONE", False)

        self.psoc_pbar.setRange(0, 1)
        self.psoc_pbar.setValue(1)
        self.psoc_pbar_lbl.setText("Received PSoC version.")
        self.is_complete = True
        self.complete_signal.emit()

    def isComplete(self):
        return self.is_complete


class XmegaInterfaces(QWizardPage):
    complete_signal = pyqtSignal()
    command_signal = pyqtSignal(str)
    sleep_signal = pyqtSignal(int)
    imei_signal = pyqtSignal()

    def __init__(self, d505, test_utility, serial_manager, model, report):
        super().__init__()

        self.d505 = d505
        self.tu = test_utility
        self.sm = serial_manager
        self.model = model
        self.report = report

        self.system_font = QApplication.font().family()
        self.label_font = QFont(self.system_font, 14)

        self.xmega_lbl = QLabel("Testing Xmega interfaces.")
        self.xmega_lbl.setFont(self.label_font)
        self.xmega_pbar = QProgressBar()
        self.xmega_pbar.setRange(0, 8)
        self.xmega_pbar_counter = 0

        self.layout = QVBoxLayout()
        self.layout.addStretch()
        self.layout.addWidget(self.xmega_lbl)
        self.layout.addWidget(self.xmega_pbar)
        self.layout.addStretch()
        self.layout.setAlignment(Qt.AlignHCenter)

        self.setLayout(self.layout)
        self.setTitle("XMega Interfaces")

    def initializePage(self):
        self.is_complete = False
        self.complete_signal.connect(self.completeChanged)
        self.command_signal.connect(self.sm.send_command)
        self.sm.data_ready.connect(self.serial_written)
        self.command_signal.emit(f"serial {self.tu.pcba_sn}")
        self.xmega_lbl.setText("Checking serial number. . .")
        self.d505.button(QWizard.NextButton).setEnabled(False)

    def serial_written(self, data):
        self.sm.data_ready.disconnect()
        self.sm.data_ready.connect(self.verify_serial)
        self.command_signal.emit("serial")

    def verify_serial(self, data):
        self.sm.data_ready.disconnect()
        self.sm.data_ready.connect(self.verify_batv)
        pattern = "D505([0-9])*"
        if (re.search(pattern, data)):
            serial_num = re.search(pattern, data).group()
            if (serial_num == self.tu.pcba_sn):
                self.report.write_data("Serial Match", serial_num, True)
            else:
                self.report.write_data("Serial Match", serial_num, False)
        else:
            self.report.write_data("Serial Match", "None", False)
            QMessageBox.warning(self, "Serial Error",
                                "Serial error or malformed value")
        self.xmega_pbar_counter += 1
        self.xmega_pbar.setValue(self.xmega_pbar_counter)
        self.xmega_lbl.setText("Verifying battery voltage. . .")
        self.command_signal.emit("bat_v")

    def verify_batv(self, data):
        self.imei_signal.connect(self.sm.iridium_command)
        self.sm.data_ready.disconnect()
        self.sm.data_ready.connect(self.verify_modem)
        pattern = "([0-9])+.([0-9])+"
        print(data)
        if (re.search(pattern, data)):
            bat_v = float(re.search(pattern, data).group())
            value_pass = self.model.compare_to_limit("Bat V", bat_v)
            if (value_pass):
                self.report.write_data("Bat V", bat_v, True)
            else:
                self.report.write_data("Bat V", bat_v, False)
        else:
            QMessageBox.warning(self, "BatV Error",
                                "Serial error or malformed value")
            self.report.write_data("Bat V", "None", False)
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
                self.report.write_data("Iridium IMEI Match", imei, True)
            else:
                self.report.write_data("Iridium IMEI Match", imei, False)
        else:
            QMessageBox.warning(self, "Modem Error",
                                "Serial error or malformed value")
            self.report.write_data("Iridium IMEI Match", "None", False)
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
                self.report.write_data("Board ID", board_id, True)
            else:
                self.report.write_data("Board ID", board_id, False)
        else:
            QMessageBox.warning(self, "Board ID Error",
                                "Serial error or malformed value")
            self.report.write_data("Board ID", "None", False)
        self.xmega_pbar_counter += 1
        self.xmega_pbar.setValue(self.xmega_pbar_counter)
        self.xmega_lbl.setText("Checking TAC ports. . .")
        self.command_signal.emit("tac-get-info")

    # def gps_loc(self, data):
    #     self.sm.data_ready.disconnect()
    #     self.sm.data_ready.connect(self.spot_read)
    #     # Disabled because cannot test inside. Talk to customer

    def verify_tac(self, data):
        self.sm.data_ready.disconnect()
        self.sm.data_ready.connect(self.flash_test)

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
                self.report.write_data("TAC Ports", "FAIL", False)

        except IndexError:
            QMessageBox.warning(self, "IMEI Error",
                                "Serial error or malformed value")

        self.xmega_pbar_counter += 1
        self.xmega_pbar.setValue(self.xmega_pbar_counter)
        self.xmega_lbl.setText("Checking flash. . .")
        self.command_signal.emit("flash_test")

    def flash_test(self, data):
        self.sm.data_ready.disconnect()
        self.sm.data_ready.connect(self.rtc_alarm_set)
        # Add flash checking after what a failure mode looks like is defined.
        self.xmega_pbar_counter += 1
        self.xmega_pbar.setValue(self.xmega_pbar_counter)
        self.xmega_lbl.setText("Testing alarm. . .")
        self.command_signal.emit("rtc-set 030719 115955")

    def rtc_alarm_set(self, data):
        self.sm.data_ready.disconnect()
        self.sm.data_ready.connect(self.rtc_alarm)
        self.command_signal.emit("rtc-alarm 12:00")

    def rtc_alarm(self, data):
        self.sm.data_ready.disconnect()
        self.sm.data_ready.connect(self.rtc_check_off)
        self.command_signal.emit("rtc-alarmed")

    def rtc_check_off(self, data):
        self.sm.data_ready.disconnect()
        self.sleep_signal.connect(self.sm.sleep)
        self.sm.sleep_finished.connect(self.rtc_wait)
        print(data)
        if "0" not in data:
            self.report.write_data("RTC Alarm", "", False)
        self.sleep_signal.emit(5)

    def rtc_wait(self):
        self.sleep_signal.disconnect()
        self.sm.data_ready.connect(self.rtc_check_on)
        self.command_signal.emit("rtc-alarmed")

    def rtc_check_on(self, data):
        self.sm.data_ready.disconnect()
        self.sm.data_ready.connect(self.snow_depth)
        print(data)
        if "1" not in data:
            self.report.write_data("RTC Alarm", "", False)
        self.xmega_pbar_counter += 1
        self.xmega_pbar.setValue(self.xmega_pbar_counter)
        self.xmega_lbl.setText("Checking range finder. . .")
        self.command_signal.emit("snow-depth")

    def snow_depth(self, data):
        self.sm.data_ready.disconnect()
        pattern = r"[0-9]+\scm"
        if (re.search(pattern, data)):
            value = re.search(pattern, data).group()
            self.report.write_data("Snow Depth", value, True)
        else:
            self.report.write_data("Snow Depth", None, False)
            QMessageBox.warning(self, "Serial Error",
                                "Serial error or malformed value")
        self.xmega_pbar_counter += 1
        self.xmega_pbar.setValue(self.xmega_pbar_counter)
        self.is_complete = True
        self.xmega_lbl.setText("Complete.")
        self.complete_signal.emit()

    def isComplete(self):
        return self.is_complete


class UartPower(QWizardPage):
    complete_signal = pyqtSignal()
    command_signal = pyqtSignal(str)

    def __init__(self, d505, test_utility, serial_manager, report):
        super().__init__()

        self.d505 = d505
        self.tu = test_utility
        self.sm = serial_manager
        self.report = report

        self.system_font = QApplication.font().family()
        self.label_font = QFont(self.system_font, 14)

        self.uart_pwr_lbl = QLabel("Remove battery power.")
        self.uart_pwr_lbl.setFont(self.label_font)
        self.uart_pwr_chkbx = QCheckBox()
        self.uart_pwr_chkbx.setStyleSheet("QCheckBox::indicator {width: 20px; \
                                        height: 20px}")
        self.uart_pwr_chkbx.clicked.connect(
            lambda: D505.checked(self.uart_pwr_lbl, self.uart_pwr_chkbx))
        self.uart_pwr_chkbx.clicked.connect(self.verify_uart)

        self.uart_pbar_lbl = QLabel("Verify UART interface")
        self.uart_pbar_lbl.setFont(self.label_font)
        self.uart_pbar = QProgressBar()

        self.red_led_lbl = QLabel("Bring magnet over Hall-Effect sensor and"
                                  " verify red LED blinks.")
        self.red_led_lbl.setFont(self.label_font)
        self.red_led_chkbx = QCheckBox()
        self.red_led_chkbx.setStyleSheet("QCheckBox::indicator {width: 20px; \
                                        height: 20px}")
        self.red_led_chkbx.clicked.connect(
            lambda: D505.checked(self.red_led_lbl, self.red_led_chkbx))
        self.red_led_chkbx.clicked.connect(self.hall_effect)

        self.leds_lbl = QLabel("Remove UART power connection, reconnect the"
                               " battery & UART connections and verify the "
                               " green, red & blue LEDs blink in the "
                               " appropriate sequence.")
        self.leds_lbl.setWordWrap(True)
        self.leds_lbl.setFont(self.label_font)
        self.leds_chkbx = QCheckBox()
        self.leds_chkbx.setStyleSheet("QCheckBox::indicator {width: 20px; \
                                        height: 20px}")
        self.leds_chkbx.clicked.connect(
            lambda: D505.checked(self.leds_lbl, self.leds_chkbx))
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
        self.grid.addWidget(self.red_led_lbl, 5, 0)
        self.grid.addWidget(self.red_led_chkbx, 5, 1)
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

    def hall_effect(self):
        self.tu.hall_effect_status.setText(
            "Hall Effect Sensor Test: PASS")
        self.tu.hall_effect_status.setStyleSheet(
            D505.status_style_pass)

    def verify_uart(self):
        self.sm.data_ready.connect(self.rx_psoc)
        self.uart_pbar.setRange(0, 0)
        self.uart_pbar_lbl.setText("Verifying UART interface...")
        self.command_signal.emit("psoc-version")

    def rx_psoc(self, data):
        self.sm.data_ready.disconnect()
        pattern = "([0-9)+.([0-9])+.([0-9])+"
        version = re.search(pattern, data)
        if (version):
            self.uart_pbar.setRange(0, 1)
            self.uart_pbar.setValue(1)
            self.uart_pbar_lbl.setText("UART interface functional.")
        else:
            QMessageBox.warning(self, "UART Power", "Bad command response.")
            self.report.write_data("UART Interface w/o batt", "NONE", False)

    def isComplete(self):
        return self.is_complete

    def page_complete(self):
        self.tu.led_test_status.setText("LED Test: PASS")
        self.tu.led_test_status.setStyleSheet(
            D505.status_style_pass)
        self.is_complete = True
        self.complete_signal.emit()


class DeepSleep(QWizardPage):
    command_signal = pyqtSignal(str)
    complete_signal = pyqtSignal()

    def __init__(self, d505, test_utility, serial_manager, model, report):
        LINE_EDIT_WIDTH = 75
        RIGHT_SPACING = 50
        LEFT_SPACING = 50

        super().__init__()

        self.d505 = d505
        self.tu = test_utility
        self.sm = serial_manager
        self.model = model
        self.report = report

        self.system_font = QApplication.font().family()
        self.label_font = QFont(self.system_font, 14)

        self.setStyleSheet("QCheckBox::indicator {width: 20px;"
                           "height: 20px}")

        self.ble_lbl = QLabel("Ensure BLE interface is disconnected or off")
        self.ble_lbl.setFont(self.label_font)
        self.ble_chkbx = QCheckBox()
        self.ble_chkbx.clicked.connect(self.send_commands)
        self.ble_chkbx.clicked.connect(
            lambda: D505.checked(self.ble_lbl, self.ble_chkbx))

        self.input_i_lbl = QLabel("Switch current meter to uA and record input"
                                  " current")
        self.input_i_lbl.setFont(self.label_font)
        self.input_i_input = QLineEdit()
        self.input_i_input.setFixedWidth(LINE_EDIT_WIDTH)
        self.input_i_unit = QLabel("uA")

        self.solar_lbl = QLabel("Switch current meter to mA and turn on the "
                                " 'solar panel simulating power supply' \n"
                                "(0.7 V with current limit set at 2 A).")
        # self.solar_lbl.setWordWrap(True)
        self.solar_lbl.setFont(self.label_font)
        self.solar_chkbx = QCheckBox()
        self.solar_chkbx.clicked.connect(lambda: D505.checked(
            self.solar_lbl, self.solar_chkbx))

        self.solar_v_lbl = QLabel("Record solar charger voltage at Q22 pin 3.")
        self.solar_v_lbl.setFont(self.label_font)
        self.solar_v_input = QLineEdit()
        self.solar_v_input.setFixedWidth(LINE_EDIT_WIDTH)
        self.solar_v_unit = QLabel("V")
        self.solar_v_unit.setFont(self.label_font)

        self.solar_i_lbl = QLabel("Record solar charger current.")
        self.solar_i_lbl.setFont(self.label_font)
        self.solar_i_input = QLineEdit()
        self.solar_i_input.setFixedWidth(LINE_EDIT_WIDTH)
        self.solar_i_unit = QLabel("mA")
        self.solar_i_unit.setFont(self.label_font)

        self.submit_button = QPushButton("Submit")
        self.submit_button.setMaximumWidth(75)
        self.submit_button.clicked.connect(self.parse_data)

        self.btn_layout = QHBoxLayout()
        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.submit_button)
        self.btn_layout.addSpacing(RIGHT_SPACING + 5)

        self.ble_layout = QHBoxLayout()
        self.ble_layout.addSpacing(LEFT_SPACING)
        self.ble_layout.addWidget(self.ble_lbl)
        self.ble_layout.addStretch()
        self.ble_layout.addWidget(self.ble_chkbx)
        self.ble_layout.addSpacing(RIGHT_SPACING)

        self.input_i_layout = QHBoxLayout()
        self.input_i_layout.addSpacing(LEFT_SPACING)
        self.input_i_layout.addWidget(self.input_i_lbl)
        self.input_i_layout.addStretch()
        self.input_i_layout.addWidget(self.input_i_input)
        self.input_i_layout.addWidget(self.input_i_unit)
        self.input_i_layout.addSpacing(RIGHT_SPACING - 16)

        self.solar_layout = QHBoxLayout()
        self.solar_layout.addSpacing(LEFT_SPACING)
        self.solar_layout.addWidget(self.solar_lbl)
        self.solar_layout.addStretch()
        self.solar_layout.addWidget(self.solar_chkbx)
        self.solar_layout.addSpacing(RIGHT_SPACING)

        self.solar_v_layout = QHBoxLayout()
        self.solar_v_layout.addSpacing(LEFT_SPACING)
        self.solar_v_layout.addWidget(self.solar_v_lbl)
        self.solar_v_layout.addStretch()
        self.solar_v_layout.addWidget(self.solar_v_input)
        self.solar_v_layout.addWidget(self.solar_v_unit)
        self.solar_v_layout.addSpacing(RIGHT_SPACING - 10)

        self.solar_i_layout = QHBoxLayout()
        self.solar_i_layout.addSpacing(LEFT_SPACING)
        self.solar_i_layout.addWidget(self.solar_i_lbl)
        self.solar_i_layout.addStretch()
        self.solar_i_layout.addWidget(self.solar_i_input)
        self.solar_i_layout.addWidget(self.solar_i_unit)
        self.solar_i_layout.addSpacing(RIGHT_SPACING - 26)

        self.layout = QVBoxLayout()
        self.layout.addStretch()
        self.layout.addLayout(self.ble_layout)
        self.layout.addSpacing(25)
        self.layout.addLayout(self.input_i_layout)
        self.layout.addSpacing(25)
        self.layout.addLayout(self.solar_layout)
        self.layout.addSpacing(25)
        self.layout.addLayout(self.solar_v_layout)
        self.layout.addSpacing(25)
        self.layout.addLayout(self.solar_i_layout)
        self.layout.addSpacing(25)
        self.layout.addLayout(self.btn_layout)
        self.layout.addStretch()

        self.setLayout(self.layout)
        self.setTitle("Deep Sleep")

    def initializePage(self):
        self.is_complete = False
        self.command_signal.connect(self.sm.send_command)
        self.complete_signal.connect(self.completeChanged)
        self.d505.button(QWizard.NextButton).setEnabled(False)

    def send_commands(self):
        self.command_signal.emit("pClock-off")

    def parse_data(self):
        try:
            deep_sleep_i = float(self.input_i_input.text())
            solar_v = float(self.solar_v_input.text())
            solar_i = float(self.solar_i_input.text())
        except ValueError:
            QMessageBox.warning(self, "Warning", "Bad Input Value!")
            return

        deep_sleep_i_pass = self.model.compare_to_limit("Deep Sleep Current",
                                                        deep_sleep_i)
        solar_i_pass = self.model.compare_to_limit("Solar Current",
                                                   solar_i)

        self.report.write_data("Deep Sleep Current", deep_sleep_i,
                               deep_sleep_i_pass)
        self.report.write_data("Solar Charge Voltage", solar_v, True)
        self.report.write_data("Solar Charge Current", solar_i, solar_i_pass)

        # Set status text values
        self.tu.deep_sleep_i_status.setText(
            f"Deep Sleep Current: {deep_sleep_i} uA")
        self.tu.solar_charge_i_status.setText(
            f"Solar Charge Current: {solar_i} mA")
        self.tu.solar_charge_v_status.setText(
            f"Solar Charge Voltage: {solar_v} V")

        if deep_sleep_i_pass:
            self.tu.deep_sleep_i_status.setStyleSheet(
                D505.status_style_pass)
        else:
            self.tu.deep_sleep_i_status.setStyleSheet(
                D505.status_style_fail)

        if solar_i_pass:
            self.tu.solar_charge_i_status.setStyleSheet(
                D505.status_style_pass)
        else:
            self.tu.solar_charge_i_status.setStyleSheet(
                D505.status_style_fail)

        self.tu.solar_charge_v_status.setStyleSheet(
            D505.status_style_pass)

        self.submit_button.setEnabled(False)
        self.is_complete = True
        self.complete_signal.emit()

    def isComplete(self):
        return self.is_complete


class FinalPage(QWizardPage):
    def __init__(self, test_utility, report):
        self.system_font = QApplication.font().family()
        self.label_font = QFont(self.system_font, 14)

        super().__init__()

        self.tu = test_utility
        self.report = report

    def initializePage(self):
        # Check test result
        test_result = self.report.test_result

        if test_result == "PASS":
            self.test_status = "Successful"
        else:
            self.test_status = "Failed"

        self.test_status_labl = QLabel(f"Test {self.test_status}!")
        self.test_status_labl.setFont(self.label_font)
        self.break_down_lbl = QLabel("Remove power and disconnect all"
                                     " peripherals from DUT.")
        self.break_down_lbl.setFont(self.label_font)

        self.layout = QVBoxLayout()
        self.layout.addStretch()
        self.layout.addWidget(self.test_status_labl)
        self.layout.addSpacing(25)
        self.layout.addWidget(self.break_down_lbl)
        self.layout.addStretch()
        self.layout.setAlignment(Qt.AlignHCenter)
        self.setLayout(self.layout)
        self.setTitle("Test Completed")
