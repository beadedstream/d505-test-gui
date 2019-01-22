from views import TestUtility
from PyQt5.QtWidgets import (QWizard, QWizardPage, QLabel, QVBoxLayout,
                             QCheckBox, QGridLayout, QProgressBar,
                             QPushButton)


class B505Procedure(QWizard):

    def __init__(self, test_utility):
        super().__init__()
        self.abort_btn = QPushButton("Abort")
        self.abort_btn.clicked.connect(self.abort)
        self.setButton(QWizard.CancelButton, self.abort_btn)

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
        self.test_utility.initUI()


class Setup(QWizardPage):
    def __init__(self):
        super().__init__()
        # self.button(QWizard.CancelButton).clicked.connect(self.abort)
        self.step_a_lbl = QLabel("Connect all peripherals to DUT"
                                 " and apply input power.", self)
        self.step_b_lbl = QLabel("Record Input voltage: ", self)
        self.step_c_lbl = QLabel("Record input current: ", self)
        self.step_d_lbl = QLabel("Record 2V supply (right side of C49).",
                                 self)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.step_a_lbl)
        self.layout.addWidget(self.step_b_lbl)
        self.layout.addWidget(self.step_c_lbl)
        self.layout.addWidget(self.step_d_lbl)
        self.setLayout(self.layout)


class WatchDog(QWizardPage):
    def __init__(self):
        super().__init__()
        self.batch_lbl = QLabel("Run Xmega programming batch file and verify"
                                " the programming was succesful.")
        self.batch_chkbx = QCheckBox()
        self.batch_chkbx.clicked.connect(self.start_uart_tests)
        self.uart_lbl = QLabel("UART Testing in Progress")
        self.uart_pbar = QProgressBar()

        self.layout = QGridLayout()
        self.layout.setHorizontalSpacing(75)
        self.layout.setVerticalSpacing(25)
        self.layout.addWidget(self.batch_lbl, 0, 0)
        self.layout.addWidget(self.batch_chkbx, 0, 1)
        self.setLayout(self.layout)

    def initializePage(self):
        self.batch_chkbx.setEnabled(True)
        self.batch_chkbx.setChecked(False)
        self.batch_lbl.setStyleSheet("")
        self.layout.removeWidget(self.uart_lbl)
        self.layout.removeWidget(self.uart_pbar)

    def start_uart_tests(self):
        if self.batch_chkbx.isChecked():
            self.layout.addWidget(self.uart_lbl, 1, 0)
            self.layout.addWidget(self.uart_pbar, 2, 0)
            self.batch_chkbx.setEnabled(False)
            self.batch_lbl.setStyleSheet("QLabel {color: grey}")


class OneWireMaster(QWizardPage):
    def __init__(self):
        super().__init__()
        self.one_wire_lbl = QLabel("Programming 1-wire master. . .")
        self.one_wire_pbar = QProgressBar()

        self.layout = QGridLayout()
        self.layout.setHorizontalSpacing(75)
        self.layout.setVerticalSpacing(25)
        self.layout.addWidget(self.one_wire_lbl, 0, 0)
        self.layout.addWidget(self.one_wire_pbar, 0, 1)
        self.setLayout(self.layout)


class CypressBLE(QWizardPage):
    def __init__(self):
        super().__init__()
        self.cypress_lbl = QLabel("Run the Cypress programming utility to"
                                  "program the CYBLE-224116 BLE module.")
        self.cypress_chkbx = QCheckBox()
        self.cypress_chkbx.clicked.connect(self.cypress)

        self.ble_lbl = QLabel("Verify communication with Bluetooth device.")
        self.ble_chkbx = QCheckBox()
        self.ble_chkbx.clicked.connect(self.ble)

        self.layout = QGridLayout()
        self.layout.setHorizontalSpacing(75)
        self.layout.setVerticalSpacing(25)
        self.layout.addWidget(self.cypress_lbl, 0, 0)
        self.layout.addWidget(self.cypress_chkbx, 0, 1)
        self.layout.addWidget(self.ble_lbl, 1, 0)
        self.layout.addWidget(self.ble_chkbx, 1, 1)
        self.setLayout(self.layout)

    def initializePage(self):
        self.cypress_chkbx.setEnabled(True)
        self.cypress_chkbx.setChecked(False)
        self.cypress_lbl.setStyleSheet("")
        self.ble_chkbx.setEnabled(True)
        self.ble_chkbx.setChecked(False)
        self.ble_lbl.setStyleSheet("")

    def cypress(self):
        if self.cypress_chkbx.isChecked():
            self.cypress_chkbx.setEnabled(False)
            self.cypress_lbl.setStyleSheet("QLabel {color: grey}")

    def ble(self):
        if self.ble_chkbx.isChecked():
            self.ble_chkbx.setEnabled(False)
            self.ble_lbl.setStyleSheet("QLabel {color: grey}")


class XmegaInterfaces(QWizardPage):
    def __init__(self):
        super().__init__()
        self.xmega_lbl = QLabel("Testing Xmega interfaces.")
        self.xmega_pbar = QProgressBar()

        self.layout = QGridLayout()
        self.layout.setHorizontalSpacing(75)
        self.layout.setVerticalSpacing(25)
        self.layout.addWidget(self.xmega_lbl, 0, 0)
        self.layout.addWidget(self.xmega_pbar, 1, 0)
        self.setLayout(self.layout)


class UartPower(QWizardPage):
    def __init__(self):
        super().__init__()
        self.uart_pwr_lbl = QLabel("Remove battery power")
        self.uart_pwr_chkbx = QCheckBox()

        self.layout = QGridLayout()
        self.layout.setHorizontalSpacing(75)
        self.layout.setVerticalSpacing(25)
        self.layout.addWidget(self.uart_pwr_lbl, 0, 0)
        self.layout.addWidget(self.uart_pwr_chkbx, 0, 1)
        self.setLayout(self.layout)


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
