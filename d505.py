import time
import re
from PyQt5.QtWidgets import (
    QWizardPage, QWizard, QLabel, QVBoxLayout, QCheckBox, QGridLayout,
    QLineEdit, QProgressBar, QPushButton, QMessageBox, QHBoxLayout,
    QApplication, QGroupBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal, QThread


class D505(QWizard):

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

        # self.addPage(Setup(model, report))
        # self.addPage(WatchDog(test_utility, serial_manager, model, report))
        # self.addPage(OneWireMaster())
        # self.addPage(CypressBLE(serial_manager, report))
        # self.addPage(XmegaInterfaces())
        # self.addPage(UartPower())
        self.addPage(DeepSleep(serial_manager, model, report))
        self.addPage(FinalPage())

        self.test_utility = test_utility

        self.sm = serial_manager
        self.serial_thread = QThread()
        self.sm.moveToThread(self.serial_thread)
        self.serial_thread.start()

        self.input_v = ""
        self.input_i = ""

    def abort(self):
        msg = "Are you sure you want to cancel the test?"
        confirmation = QMessageBox.question(self, "Abort Test?", msg,
                                            QMessageBox.Yes,
                                            QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            self.serial_thread.quit()
            self.test_utility.initUI()
        else:
            pass

    def finish(self):
        self.test_utility.initUI()
        # DO: Generate report
        self.serial_thread.quit()

    def checked(lbl, chkbx):
        if chkbx.isChecked():
            chkbx.setEnabled(False)
            lbl.setStyleSheet("QLabel {color: grey}")

    def close(self):
        self.serial_thread.quit()


class Setup(QWizardPage):
    def __init__(self, model, report):
        LINE_EDIT_WIDTH = 75
        VERT_SPACING = 25
        RIGHT_SPACING = 125
        LEFT_SPACING = 125

        super().__init__()

        self.model = model
        self.report = report

        # Flag for tracking page completion and allowing the next button
        # to be re-enabled.
        self.is_complete = False

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
        self.step_a_chkbx.clicked.connect(self.measure_values)

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
        self.submit_button.clicked.connect(self.completeChanged)
        self.submit_button.clicked.connect(self.parse_values)
        self.submit_button.setFixedWidth(LINE_EDIT_WIDTH)

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
        self.layout.addStretch()

        # group = QGroupBox()
        # group.setLayout(self.layout)

        # vbox = QVBoxLayout()
        # vbox.addWidget(group)
        # vbox.addStretch()

        self.setLayout(self.layout)

    def parse_values(self):
        self.submit_button.setEnabled(False)
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

    def measure_values(self):
        self.is_complete = True

    def isComplete(self):
        return self.is_complete


class WatchDog(QWizardPage):
    command_signal = pyqtSignal(str)
    sleep_signal = pyqtSignal(int)

    def __init__(self, test_utility, serial_manager, model, report):
        super().__init__()

        self.sm = serial_manager
        self.report = report
        self.model = model

        self.command_signal.connect(self.sm.send_command)
        self.sleep_signal.connect(self.sm.sleep)

        # Flag for tracking page completion and allowing the next button
        # to be re-enabled.
        self.is_complete = False

        self.system_font = QApplication.font().family()
        self.label_font = QFont(self.system_font, 14)

        self.batch_lbl = QLabel("Run Xmega programming batch file and verify"
                                " the programming was succesful.  ")
        self.batch_lbl.setFont(self.label_font)
        self.batch_chkbx = QCheckBox()
        self.batch_chkbx.setStyleSheet("QCheckBox::indicator {width: 20px; \
                                        height: 20px}")
        self.batch_chkbx.clicked.connect(self.start_uart_tests)
        self.batch_chkbx.clicked.connect(self.batch_chkbx_clicked)
        self.batch_chkbx.clicked.connect(self.update_progressbar)

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

    def isComplete(self):
        return self.is_complete

    def start_uart_tests(self):
        if self.batch_chkbx.isChecked():
            # self.layout.insertWidget(2, self.uart_lbl)
            # self.layout.insertWidget(3, self.uart_pbar)
            # self.uart_lbl.show()
            # self.uart_pbar.show()
            self.batch_chkbx.setEnabled(False)
            self.batch_lbl.setStyleSheet("QLabel {color: grey}")

    def update_progressbar(self):
        self.watchdog_pbar.setRange(0, 0)

    def batch_chkbx_clicked(self):
        self.sm.data_ready.connect(self.watchdog_handler)
        self.command_signal.emit("watchdog")

    def watchdog_handler(self, data):
        self.sm.data_ready.disconnect()
        self.sm.data_ready.connect(self.uart_5v1_handler)
        self.watchdog_pbar.setRange(0, 1)
        self.watchdog_pbar.setValue(1)
        print(data)
        bl_pattern = "bootloader version .*\n"
        app_pattern = "datalogger version .*\n"
        try:
            bootloader_version = re.search(bl_pattern, data).group()
            app_version = re.search(app_pattern, data).group()
        except AttributeError:
            QMessageBox.warning(self, "Warning",
                                "Error in serial data, try this step again")
            return
        self.report.write_data("Xmega Bootloader Version", bootloader_version,
                               True)
        self.report.write_data("Xmega App Version", app_version, True)
        self.command_signal.emit("5V 1")

    def uart_5v1_handler(self, data):
        self.sm.data_ready.disconnect()
        self.supply_5v_input.setEnabled(True)
        self.supply_5v_input_btn.setEnabled(True)

    def user_value_handler(self):
        self.sm.data_ready.connect(self.uart_5v0_handler)
        self.supply_5v_input.setEnabled(False)
        self.supply_5v_pbar.setRange(0, 0)
        try:
            supply_5v_val = float(self.supply_5v_input.text())
        except ValueError:
            QMessageBox.warning(self, "Warning", "Bad Input Value!")
            return
        self.report.write_data("5V Supply", supply_5v_val,
                               self.model.compare_to_limit("5V Supply",
                                                           supply_5v_val))
        self.command_signal.emit("5V")

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
        self.report.write_data("5V UART", uart_5v_val,
                               self.model.compare_to_limit("5V UART",
                                                           uart_5v_val))
        self.command_signal.emit("5V 0")

    def uart_5v0_handler(self, data):
        self.sm.data_ready.disconnect()
        self.sm.sleep_finished.connect(self.sleep_handler)
        self.sleep_signal.emit(10)

    def sleep_handler(self):
        self.sm.sleep_finished.disconnect()
        self.sm.data_ready.connect(self.final_5v_handler)
        self.command_signal.emit("5V")

    def final_5v_handler(self, data):
        self.sm.data_ready.disconnect()
        self.supply_5v_pbar.valueChanged.connect(self.completeChanged)
        self.is_complete = True
        self.supply_5v_pbar.setRange(0, 1)
        self.supply_5v_pbar.setValue(1)
        data = data.strip("\n").split("\n")
        try:
            uart_off_val = float(data[1].strip("\n"))
        except ValueError:
            QMessageBox.warning(self, "Warning",
                                "Error in serial data, try this step again")
            return
        self.report.write_data("UART Off", uart_off_val,
                               self.model.compare_to_limit("5V UART",
                                                           uart_off_val))
        self.report.generate_report()


class OneWireMaster(QWizardPage):
    def __init__(self):
        super().__init__()

        self.system_font = QApplication.font().family()
        self.label_font = QFont(self.system_font, 14)

        self.one_wire_lbl = QLabel("Programming 1-wire master. . .")
        self.one_wire_lbl.setFont(self.label_font)
        self.one_wire_pbar = QProgressBar()

        self.layout = QVBoxLayout()
        self.layout.addStretch()
        self.layout.addWidget(self.one_wire_lbl)
        self.layout.addWidget(self.one_wire_pbar)
        self.layout.addStretch()

        self.setLayout(self.layout)


class CypressBLE(QWizardPage):
    command_signal = pyqtSignal(str)

    def __init__(self, serial_manager, report):
        super().__init__()

        self.sm = serial_manager
        self.command_signal.connect(self.sm.send_command)

        self.report = report

        self.system_font = QApplication.font().family()
        self.label_font = QFont(self.system_font, 14)

        self.cypress_lbl = QLabel("Run the Cypress programming utility to"
                                  "program the CYBLE-224116 BLE module.")
        self.cypress_lbl.setFont(self.label_font)
        self.cypress_chkbx = QCheckBox()
        self.cypress_chkbx.setStyleSheet("QCheckBox::indicator {width: 20px; \
                                        height: 20px}")
        self.cypress_chkbx.clicked.connect(
            lambda: D505.checked(self.cypress_lbl, self.cypress_chkbx))

        self.pwr_cycle_lbl = QLabel("Power cycle DUT (unplug/replug both UART "
                                    "and battery).")
        self.pwr_cycle_lbl.setFont(self.label_font)
        self.pwr_cycle_chkbx = QCheckBox()
        self.pwr_cycle_chkbx.setStyleSheet("QCheckBox::indicator {width: 20px; \
                                        height: 20px}")
        self.pwr_cycle_chkbx.clicked.connect(
            lambda: D505.checked(self.pwr_cycle_lbl, self.pwr_cycle_chkbx))

        self.bt_comm_lbl = QLabel("Very communication to 505 with "
                                  "bluetooth device")
        self.bt_comm_lbl.setFont(self.label_font)
        self.bt_comm_chkbx = QCheckBox()
        self.bt_comm_chkbx.setStyleSheet("QCheckBox::indicator {width: 20px; \
                                        height: 20px}")
        self.bt_comm_chkbx.clicked.connect(
            lambda: D505.checked(self.bt_comm_lbl, self.bt_comm_chkbx))
        self.bt_comm_chkbx.clicked.connect(self.psoc_version)

        self.grid = QGridLayout()
        self.grid.setHorizontalSpacing(75)
        self.grid.setVerticalSpacing(25)
        self.grid.addWidget(self.cypress_lbl, 0, 0)
        self.grid.addWidget(self.cypress_chkbx, 0, 1)
        self.grid.addWidget(self.pwr_cycle_lbl, 1, 0)
        self.grid.addWidget(self.pwr_cycle_chkbx, 1, 1)
        self.grid.addWidget(self.bt_comm_lbl, 2, 0)
        self.grid.addWidget(self.bt_comm_chkbx, 2, 1)

        self.hbox = QHBoxLayout()
        self.hbox.addStretch()
        self.hbox.addLayout(self.grid)
        self.hbox.addStretch()

        self.layout = QVBoxLayout()
        self.layout.addStretch()
        self.layout.addLayout(self.hbox)
        self.layout.addStretch()

        self.setLayout(self.layout)

    def psoc_version(self):
        self.sm.data_ready.connect(self.parse_data)
        self.command_signal.emit("psoc-version")

    def parse_data(self, data):
        self.sm.data_ready.disconnect()
        formatted_data = data.strip("\n")
        print(formatted_data)
        self.report.write_data("BLE Version", formatted_data, True)


class XmegaInterfaces(QWizardPage):
    def __init__(self):
        super().__init__()

        self.system_font = QApplication.font().family()
        self.label_font = QFont(self.system_font, 14)

        self.xmega_lbl = QLabel("Testing Xmega interfaces.")
        self.xmega_lbl.setFont(self.label_font)
        self.xmega_pbar = QProgressBar()

        self.layout = QVBoxLayout()
        self.layout.addStretch()
        self.layout.addWidget(self.xmega_lbl)
        self.layout.addWidget(self.xmega_pbar)
        self.layout.addStretch()
        self.layout.setAlignment(Qt.AlignHCenter)

        self.setLayout(self.layout)


class UartPower(QWizardPage):
    def __init__(self):
        super().__init__()

        self.system_font = QApplication.font().family()
        self.label_font = QFont(self.system_font, 14)

        self.uart_pwr_lbl = QLabel("Remove battery power; verify UART power"
                                   " interface is working")
        self.uart_pwr_lbl.setFont(self.label_font)
        self.uart_pwr_chkbx = QCheckBox()
        self.uart_pwr_chkbx.setStyleSheet("QCheckBox::indicator {width: 20px; \
                                        height: 20px}")
        # self.uart_pwr_chkbx.clicked.connect(self.red_led)
        self.uart_pwr_chkbx.clicked.connect(
            lambda: D505.checked(self.uart_pwr_lbl, self.uart_pwr_chkbx))

        self.red_led_lbl = QLabel("Bring magnet over Hall-Effect sensor and"
                                  " verify red LED blinks")
        self.red_led_lbl.setFont(self.label_font)
        self.red_led_chkbx = QCheckBox()
        self.red_led_chkbx.setStyleSheet("QCheckBox::indicator {width: 20px; \
                                        height: 20px}")
        # self.red_led_chkbx.clicked.connect(self.leds)
        self.red_led_chkbx.clicked.connect(
            lambda: D505.checked(self.red_led_lbl, self.red_led_chkbx))

        self.leds_lbl1 = QLabel("Remove UART power connection, reconnect the"
                                " battery & UART")
        self.leds_lbl2 = QLabel(" connections and verify the green, red & blue"
                                " LEDs blink in the appropriate sequence")
        self.leds_lbl1.setFont(self.label_font)
        self.leds_lbl2.setFont(self.label_font)
        self.leds_chkbx = QCheckBox()
        self.leds_chkbx.clicked.connect(
            lambda: D505.checked(self.leds_lbl1, self.leds_chkbx))
        self.leds_chkbx.clicked.connect(
            lambda: D505.checked(self.leds_lbl2, self.leds_chkbx))
        self.leds_chkbx.setStyleSheet("QCheckBox::indicator {width: 20px; \
                                        height: 20px}")

        self.grid = QGridLayout()
        self.grid.setHorizontalSpacing(75)
        self.grid.setVerticalSpacing(25)
        self.grid.addWidget(self.uart_pwr_lbl, 0, 0)
        self.grid.addWidget(self.uart_pwr_chkbx, 0, 1)
        self.grid.addWidget(self.red_led_lbl, 1, 0)
        self.grid.addWidget(self.red_led_chkbx, 1, 1)
        self.grid.addWidget(self.leds_lbl1, 2, 0)
        self.grid.addWidget(self.leds_lbl2, 3, 0)
        self.grid.addWidget(self.leds_chkbx, 3, 1)

        self.layout = QVBoxLayout()
        self.layout.addStretch()
        self.layout.addLayout(self.grid)
        self.layout.addStretch()

        self.setLayout(self.layout)

    # def red_led(self):
    #     if self.red_led_chkbx.isChecked():
    #         self.red_led.chkbx.setEnabled(False)
    #         self.red_led_lbl.setStyleSheet("QLabel {color: grey}")

    # def leds(self):
    #     if self.leds_chkbx.isChecked():
    #         self.leds.chkbx.setEnabled(False)
    #         self.leds_lbl1.setStyleSheet("QLabel {color: grey}")
    #         self.leds_lbl2.setStyleSheet("QLabel {color: grey}")


class DeepSleep(QWizardPage):
    command_signal = pyqtSignal(str)

    def __init__(self, serial_manager, model, report):
        LINE_EDIT_WIDTH = 75
        RIGHT_SPACING = 50
        LEFT_SPACING = 50

        super().__init__()

        self.sm = serial_manager
        self.model = model
        self.report = report

        self.command_signal.connect(self.sm.send_command)

        self.system_font = QApplication.font().family()
        self.label_font = QFont(self.system_font, 14)

        self.setStyleSheet("QCheckBox::indicator {width: 20px;"
                           "height: 20px}")

        self.disconnect_lbl = QLabel("Disconnect the PSoC programmer")
        self.disconnect_lbl.setFont(self.label_font)
        self.disconnect_chkbx = QCheckBox()

        self.ble_lbl = QLabel("Ensure BLE interface is disconnected or off")
        self.ble_lbl.setFont(self.label_font)
        self.ble_chkbx = QCheckBox()
        self.ble_chkbx.clicked.connect(self.send_commands)

        self.input_i_lbl = QLabel("Switch current meter to uA and record input"
                                  " current")
        self.input_i_lbl.setFont(self.label_font)
        self.input_i_input = QLineEdit()
        self.input_i_input.setFixedWidth(LINE_EDIT_WIDTH)
        self.input_i_unit = QLabel("uA")

        self.solar_lbl = QLabel("Switch current meter to mA and turn on the "
                                " 'solar panel simulating power supply'")
        self.solar_lbl.setFont(self.label_font)

        self.solar_v_lbl = QLabel("Record solar charger voltage")
        self.solar_v_lbl.setFont(self.label_font)
        self.solar_v_input = QLineEdit()
        self.solar_v_input.setFixedWidth(LINE_EDIT_WIDTH)
        self.solar_v_unit = QLabel("V")
        self.solar_v_unit.setFont(self.label_font)

        self.solar_i_lbl = QLabel("Record solar charger current")
        self.solar_i_lbl.setFont(self.label_font)
        self.solar_i_input = QLineEdit()
        self.solar_i_input.setFixedWidth(LINE_EDIT_WIDTH)
        self.solar_i_unit = QLabel("mA")
        self.solar_i_unit.setFont(self.label_font)

        self.disconnect_layout = QHBoxLayout()
        self.disconnect_layout.addSpacing(LEFT_SPACING)
        self.disconnect_layout.addWidget(self.disconnect_lbl)
        self.disconnect_layout.addStretch()
        self.disconnect_layout.addWidget(self.disconnect_chkbx)
        self.disconnect_layout.addSpacing(RIGHT_SPACING)

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
        self.layout.addLayout(self.disconnect_layout)
        self.layout.addLayout(self.ble_layout)
        self.layout.addLayout(self.input_i_layout)
        self.layout.addSpacing(10)
        self.layout.addLayout(self.solar_layout)
        self.layout.addSpacing(5)
        self.layout.addLayout(self.solar_v_layout)
        self.layout.addLayout(self.solar_i_layout)
        self.layout.addStretch()

        self.setLayout(self.layout)

    def send_commands(self):
        self.sm.data_ready.connect(self.receive_commands)
        self.command_signal.emit("app 0")
        time.sleep(0.1)
        self.command_signal.emit("pClock-off")

    def receive_commands(self, data):
        print(data)

    def parse_data(self):
        pass


class FinalPage(QWizardPage):
    def __init__(self):
        self.system_font = QApplication.font().family()
        self.label_font = QFont(self.system_font, 14)

        super().__init__()

        # Placeholder until logic is built in
        self.test_status = "Successful"
        self.test_status_labl = QLabel(f"Test {self.test_status}!")
        self.test_status_labl.setFont(self.label_font)
        self.break_down_lbl = QLabel("Remove power and disconect all"
                                     " peripherals from DUT")
        self.break_down_lbl.setFont(self.label_font)

        self.layout = QVBoxLayout()
        self.layout.addStretch()
        self.layout.addWidget(self.test_status_labl)
        self.layout.addWidget(self.break_down_lbl)
        self.layout.addStretch()
        self.layout.setAlignment(Qt.AlignHCenter)
        self.setLayout(self.layout)
