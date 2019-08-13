import re
import os.path
from pathlib import Path
from PyQt5.QtWidgets import (
    QWizardPage, QWizard, QLabel, QVBoxLayout, QCheckBox, QGridLayout,
    QLineEdit, QProgressBar, QPushButton, QMessageBox, QHBoxLayout,
    QApplication)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from setup import Setup
from program import Program
from onewire import OneWireMaster
from ble import CypressBLE
from interfaces import XmegaInterfaces
from uartpower import UartPower
from deepsleep import DeepSleep
from final import FinalPage


class InvalidType(Exception):
    pass


class D505(QWizard):
    """QWizard class for the D505 board. Sets up the QWizard page and adds the
    individual QWizardPage subpages for each set of tests."""



    def __init__(self, test_utility, model, serial_manager, report):
        super().__init__()
        self.status_style_pass = """QLabel {background: #8cff66;
                        border: 2px solid grey; font-size: 20px}"""
        self.status_style_fail = """QLabel {background: #ff5c33;
                        border: 2px solid grey; font-size: 20px}"""
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
        watchdog_id = self.addPage(Program(self, test_utility, serial_manager,
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
        """Prompt user for confirmation and abort test if confirmed."""

        msg = "Are you sure you want to cancel the test?"
        confirmation = QMessageBox.question(self, "Abort Test?", msg,
                                            QMessageBox.Yes,
                                            QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            self.tu.initUI()
        else:
            pass

    def finish(self):
        """Reinitialize the TestUtility main page when tests are finished."""

        self.tu.initUI()
