from d505 import *


class DeepSleep(QWizardPage):
    """Seventh QWizard page. Handles deep sleep tests."""
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
        self.label_font = QFont(self.system_font, 12)

        self.setStyleSheet("QCheckBox::indicator {width: 20px;"
                           "height: 20px}")

        self.ble_lbl = QLabel("Ensure BLE interface is disconnected or off.")
        self.ble_lbl.setFont(self.label_font)
        self.ble_chkbx = QCheckBox()
        self.ble_chkbx.clicked.connect(
            lambda: D505.checked(self.ble_lbl, self.ble_chkbx))

        self.input_i_lbl = QLabel()
        self.input_i_lbl.setTextFormat(Qt.RichText)
        self.input_i_lbl.setFont(self.label_font)
        self.input_i_lbl.setText(
            "Switch current meter to <b>uA</b> and record input current.")
        self.sleep_btn = QPushButton("Sleep Mode")
        self.sleep_btn.clicked.connect(self.sleep_command)
        self.input_i_input = QLineEdit()
        self.input_i_input.setFixedWidth(LINE_EDIT_WIDTH)
        self.input_i_unit = QLabel("uA")

        self.solar_lbl = QLabel()
        self.solar_lbl.setTextFormat(Qt.RichText)
        self.solar_lbl.setText(
            "Switch current meter <font color='red'>back to mA.</font><br/>"
            "Turn on solar panel simulating power supply.<br/>"
            "Use 0.7 V with the current limit set at 2 A.")
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
        self.input_i_layout.addSpacing(50)
        self.input_i_layout.addWidget(self.sleep_btn)
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
        self.sm.data_ready.connect(self.command_finished)
        self.d505.button(QWizard.NextButton).setEnabled(False)

    def sleep_command(self):
        self.command_signal.emit("pClock-off")
        self.sleep_btn.setEnabled(False)

    def command_finished(self):
        self.sleep_btn.setEnabled(True)

    def parse_data(self):
        try:
            deep_sleep_i = float(self.input_i_input.text())
            solar_v = float(self.solar_v_input.text())
            solar_i = float(self.solar_i_input.text())
        except ValueError:
            QMessageBox.warning(self, "Warning", "Bad Input Value!")
            return

        deep_sleep_i_pass = self.model.compare_to_limit("deep_sleep_i",
                                                        deep_sleep_i)
        solar_i_pass = self.model.compare_to_limit("solar_i_min", solar_i)
        solar_v_pass = self.model.compare_to_limit("solar_v", solar_v)

        if deep_sleep_i_pass:
            self.report.write_data("deep_sleep_i", deep_sleep_i, "PASS")
            self.tu.deep_sleep_i_status.setStyleSheet(D505.status_style_pass)
        else:
            self.report.write_data("deep_sleep_i", deep_sleep_i, "FAIL")
            self.tu.deep_sleep_i_status.setStyleSheet(D505.status_style_fail)

        if solar_i_pass:
            self.report.write_data("solar_i", solar_i, "PASS")
            self.tu.solar_charge_i_status.setStyleSheet(D505.status_style_pass)
        else:
            self.report.write_data("solar_i", solar_i, "FAIL")
            self.tu.solar_charge_i_status.setStyleSheet(D505.status_style_fail)

        if solar_v_pass:
            self.report.write_data("solar_v", solar_v, "PASS")
            self.tu.solar_charge_v_status.setStyleSheet(D505.status_style_pass)
        else:
            self.report.write_data("solar_v", solar_v, "FAIL")
            self.tu.solar_charge_v_status.setStyleSheet(D505.status_style_fail)

        # Set status text values
        self.tu.deep_sleep_i_status.setText(
            f"Deep Sleep Current: {deep_sleep_i} uA")
        self.tu.solar_charge_i_status.setText(
            f"Solar Charge Current: {solar_i} mA")
        self.tu.solar_charge_v_status.setText(
            f"Solar Charge Voltage: {solar_v} V")

        self.submit_button.setEnabled(False)
        self.input_i_lbl.setStyleSheet("QLabel {color: grey}")
        self.solar_i_lbl.setStyleSheet("QLabel {color: grey}")
        self.solar_v_lbl.setStyleSheet("QLabel {color: grey}")
        self.is_complete = True
        self.complete_signal.emit()

    def isComplete(self):
        return self.is_complete
