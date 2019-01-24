from views import TestUtility
from PyQt5.QtWidgets import (
    QWizardPage, QWizard, QLabel, QVBoxLayout, QCheckBox, QGridLayout,
    QLineEdit, QProgressBar, QPushButton, QMessageBox, QHBoxLayout,
    QApplication, QGroupBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class D505Procedure(QWizard):

    def __init__(self, test_utility):
        super().__init__()
        self.abort_btn = QPushButton("Abort")
        self.abort_btn.clicked.connect(self.abort)
        self.setButton(QWizard.CustomButton1, self.abort_btn)

        btn_layout = [QWizard.Stretch, QWizard.BackButton, QWizard.NextButton,
                      QWizard.CustomButton1]
        self.setButtonLayout(btn_layout)

        self.addPage(Setup())
        self.addPage(WatchDog())
        self.addPage(OneWireMaster())
        self.addPage(CypressBLE())
        self.addPage(XmegaInterfaces())
        self.addPage(UartPower())
        self.addPage(DeepSleep())
        self.addPage(FinalPage())

        self.test_utility = test_utility

    def abort(self):
        msg = "Are you sure you want to cancel the test?"
        confirmation = QMessageBox.question(self, "Abort Test?", msg,
                                            QMessageBox.Yes,
                                            QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            self.test_utility.initUI()
        else:
            pass


class Setup(QWizardPage):
    def __init__(self):
        LINE_EDIT_WIDTH = 75
        VERT_SPACING = 25
        RIGHT_SPACING = 125
        LEFT_SPACING = 125

        super().__init__()

        self.system_font = QApplication.font().family()
        self.label_font = QFont(self.system_font, 14)
        self.step_a_lbl = QLabel("Connect all peripherals to DUT"
                                 " and apply input power:", self)
        self.step_a_lbl.setFont(self.label_font)
        self.step_a_chkbx = QCheckBox()
        self.step_a_chkbx.setStyleSheet("QCheckBox::indicator {width: 20px; \
                                        height: 20px}")

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
        self.layout.addStretch()

        group = QGroupBox()
        group.setLayout(self.layout)

        vbox = QVBoxLayout()
        vbox.addWidget(group)

        self.setLayout(vbox)


class WatchDog(QWizardPage):
    def __init__(self):
        LINE_EDIT_WIDTH = 75
        VERT_SPACING = 25
        RIGHT_SPACING = 200

        super().__init__()

        self.system_font = QApplication.font().family()
        self.label_font = QFont(self.system_font, 14)

        self.batch_lbl = QLabel("Run Xmega programming batch file and verify"
                                " the programming was succesful.  ")
        self.batch_lbl.setFont(self.label_font)
        self.batch_chkbx = QCheckBox()
        self.batch_chkbx.setStyleSheet("QCheckBox::indicator {width: 20px; \
                                        height: 20px}")
        self.batch_chkbx.clicked.connect(self.start_uart_tests)

        self.uart_lbl = QLabel("UART Testing in Progress")
        self.uart_lbl.setFont(self.label_font)
        self.uart_pbar = QProgressBar()

        self.supply_5v_lbl = QLabel("Measure and record the 5 V supply "
                                    "(bottom side of C55):")
        self.supply_5v_lbl.setFont(self.label_font)
        self.supply_5v_input = QLineEdit()
        self.supply_5v_unit = QLabel("V")

        self.batch_layout = QHBoxLayout()
        self.batch_layout.addStretch()
        self.batch_layout.addWidget(self.batch_lbl)
        self.batch_layout.addWidget(self.batch_chkbx)
        self.batch_layout.addStretch()

        self.supply_5v_layout = QHBoxLayout()
        self.supply_5v_layout.addStretch()
        self.supply_5v_layout.addWidget(self.supply_5v_lbl)
        self.supply_5v_layout.addWidget(self.supply_5v_input)
        self.supply_5v_layout.addWidget(self.supply_5v_unit)
        self.supply_5v_layout.addStretch()

        self.layout = QVBoxLayout()
        self.layout.addStretch()
        self.layout.addLayout(self.batch_layout)
        self.layout.addStretch()
        self.layout.setAlignment(Qt.AlignHCenter)

        self.setLayout(self.layout)

    def initializePage(self):
        self.batch_chkbx.setEnabled(True)
        self.batch_chkbx.setChecked(False)
        self.batch_lbl.setStyleSheet("")
        self.layout.removeWidget(self.uart_lbl)
        self.layout.removeWidget(self.uart_pbar)
        self.uart_lbl.hide()
        self.uart_pbar.hide()

    def start_uart_tests(self):
        if self.batch_chkbx.isChecked():
            self.layout.insertWidget(2, self.uart_lbl)
            self.layout.insertWidget(3, self.uart_pbar)
            self.uart_lbl.show()
            self.uart_pbar.show()
            self.batch_chkbx.setEnabled(False)
            self.batch_lbl.setStyleSheet("QLabel {color: grey}")


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
    def __init__(self):
        super().__init__()

        self.system_font = QApplication.font().family()
        self.label_font = QFont(self.system_font, 14)

        self.cypress_lbl = QLabel("Run the Cypress programming utility to"
                                  "program the CYBLE-224116 BLE module.")
        self.cypress_lbl.setFont(self.label_font)
        self.cypress_chkbx = QCheckBox()
        self.cypress_chkbx.setStyleSheet("QCheckBox::indicator {width: 20px; \
                                        height: 20px}")
        self.cypress_chkbx.clicked.connect(lambda:
                                           self.checked(self.cypress_lbl,
                                                        self.cypress_chkbx))

        self.ble_lbl = QLabel("Verify communication with Bluetooth device.")
        self.ble_lbl.setFont(self.label_font)
        self.ble_chkbx = QCheckBox()
        self.ble_chkbx.setStyleSheet("QCheckBox::indicator {width: 20px; \
                                        height: 20px}")
        self.ble_chkbx.clicked.connect(lambda:
                                       self.checked(self.ble_lbl,
                                                    self.ble_chkbx))

        self.bt_comm_lbl = QLabel("Very communication to 505 with "
                                  "bluetooth device")
        self.bt_comm_lbl.setFont(self.label_font)
        self.bt_comm_chkbx = QCheckBox()
        self.bt_comm_chkbx.setStyleSheet("QCheckBox::indicator {width: 20px; \
                                        height: 20px}")
        self.bt_comm_chkbx.clicked.connect(lambda:
                                           self.checked(self.bt_comm_lbl,
                                                        self.bt_comm_chkbx))

        self.grid = QGridLayout()
        self.grid.setHorizontalSpacing(75)
        self.grid.setVerticalSpacing(25)
        self.grid.addWidget(self.cypress_lbl, 0, 0)
        self.grid.addWidget(self.cypress_chkbx, 0, 1)
        self.grid.addWidget(self.ble_lbl, 1, 0)
        self.grid.addWidget(self.ble_chkbx, 1, 1)
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

    def initializePage(self):
        self.cypress_chkbx.setEnabled(True)
        self.cypress_chkbx.setChecked(False)
        self.cypress_lbl.setStyleSheet("")
        self.ble_chkbx.setEnabled(True)
        self.ble_chkbx.setChecked(False)
        self.ble_lbl.setStyleSheet("")
        self.bt_comm_chkbx.setEnabled(True)
        self.bt_comm_chkbx.setChecked(False)
        self.bt_comm_lbl.setStyleSheet("")

    def checked(self, lbl, chkbx):
        if chkbx.isChecked():
            chkbx.setEnabled(False)
            lbl.setStyleSheet("QLabel {color: grey}")


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
        self.uart_pwr_chkbx.clicked.connect(self.red_led)
        self.uart_pwr_chkbx.clicked.connect(lambda: self.checked(
                                            self.uart_pwr_lbl,
                                            self.uart_pwr_chkbx))

        self.red_led_lbl = QLabel("Bring magnet over Hall-Effect sensor and"
                                  " verify red LED blinks")
        self.red_led_lbl.setFont(self.label_font)
        self.red_led_chkbx = QCheckBox()
        self.red_led_chkbx.setStyleSheet("QCheckBox::indicator {width: 20px; \
                                        height: 20px}")
        self.red_led_chkbx.clicked.connect(self.leds)
        self.red_led_chkbx.clicked.connect(lambda: self.checked(
                                    self.red_led_lbl,
                                    self.red_led_chkbx))

        self.leds_lbl1 = QLabel("Remove UART power connection, reconnect the"
                                " battery & UART")
        self.leds_lbl2 = QLabel(" connections and verify the green, red & blue"
                                " LEDs blink in the appropriate sequence")
        self.leds_lbl1.setFont(self.label_font)
        self.leds_lbl2.setFont(self.label_font)
        self.leds_chkbx = QCheckBox()
        self.leds_chkbx.clicked.connect(lambda: self.checked(
                                            self.leds_lbl1,
                                            self.leds_chkbx))
        self.leds_chkbx.clicked.connect(lambda: self.checked(
                                            self.leds_lbl2,
                                            self.leds_chkbx))
        self.leds_chkbx.setStyleSheet("QCheckBox::indicator {width: 20px; \
                                        height: 20px}")

        self.grid = QGridLayout()
        self.grid.setHorizontalSpacing(75)
        self.grid.setVerticalSpacing(25)
        self.grid.addWidget(self.uart_pwr_lbl, 0, 0)
        self.grid.addWidget(self.uart_pwr_chkbx, 0, 1)

        self.layout = QVBoxLayout()
        self.layout.addStretch()
        self.layout.addLayout(self.grid)
        self.layout.addStretch()

        self.setLayout(self.layout)

    def red_led(self):
        self.grid.addWidget(self.red_led_lbl, 1, 0)
        self.grid.addWidget(self.red_led_chkbx, 1, 1)
        if self.red_led_chkbx.isChecked():
            self.red_led.chkbx.setEnabled(False)
            self.red_led_lbl.setStyleSheet("QLabel {color: grey}")

    def leds(self):
        self.grid.addWidget(self.leds_lbl1, 2, 0)
        self.grid.addWidget(self.leds_lbl2, 3, 0)
        self.grid.addWidget(self.leds_chkbx, 3, 1)
        if self.leds_chkbx.isChecked():
            self.leds.chkbx.setEnabled(False)
            self.leds_lbl1.setStyleSheet("QLabel {color: grey}")
            self.leds_lbl2.setStyleSheet("QLabel {color: grey}")

    def checked(self, lbl, chkbx):
        if chkbx.isChecked():
            chkbx.setEnabled(False)
            lbl.setStyleSheet("QLabel {color: grey}")


class DeepSleep(QWizardPage):
    def __init__(self):
        super().__init__()
        self.instructions_lbl = QLabel("Disconnect the PSoC programmer")
        self.ble_lbl = QLabel("Ensure BLE interface is disconnected or off")

        self.layout = QGridLayout()
        self.layout.setHorizontalSpacing(75)
        self.layout.setVerticalSpacing(25)
        self.layout.addWidget(self.instructions_lbl, 0, 0)
        self.layout.addWidget(self.ble_lbl, 0, 1)
        self.setLayout(self.layout)


class FinalPage(QWizardPage):
    def __init__(self):
        super().__init__()
        # Placeholder until logic is built in
        self.test_status = "Successful"
        self.test_status_labl = QLabel(f"Test {self.test_status}!")
        self.break_down_lbl = QLabel("Remove power and disconect all"
                                     " peripherals from DUT")

        self.layout = QGridLayout()
        self.layout.setHorizontalSpacing(75)
        self.layout.setVerticalSpacing(25)
        self.layout.addWidget(self.test_status_labl, 0, 0)
        self.layout.addWidget(self.break_down_lbl, 0, 1)
        self.setLayout(self.layout)
