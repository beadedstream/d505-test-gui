from d505 import *


class Setup(QWizardPage):
    """First QWizard Page with initial input values."""

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
        self.label_font = QFont(self.system_font, 12)
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
        # self.step_b_lbl.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
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

        self.setLayout(self.layout)
        self.setTitle("Setup")

    def initializePage(self):
        # Flag for tracking page completion and allowing the next button
        # to be re-enabled.
        self.is_complete = False
        self.complete_signal.connect(self.completeChanged)

    def parse_values(self):
        """Parse the input values and check their validity."""

        limits = ["input_v", "input_i", "supply_2v"]
        values = []
        try:
            values.append(float(self.step_b_input.text()))
            values.append(float(self.step_c_input.text()))
            values.append(float(self.step_d_input.text()))
        except ValueError:
            QMessageBox.warning(self, "Warning", "Bad input value!")
            return
        for limit, value in zip(limits, values):
            if(self.model.compare_to_limit(limit, value)):
                self.report.write_data(limit, value, "PASS")
            else:
                self.report.write_data(limit, value, "FAIL")

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
        self.is_complete = True
        self.complete_signal.emit()

    def isComplete(self):
        return self.is_complete
