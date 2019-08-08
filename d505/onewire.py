from d505 import *


class OneWireMaster(QWizardPage):
    """Third QWizard page. Handles OneWire Master programming."""
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
        self.one_wire_master_file = None
        self.hex_files_dir = None

        self.system_font = QApplication.font().family()
        self.label_font = QFont(self.system_font, 12)

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

        self.hex_files_dir = self.tu.settings.value("hex_files_path")

        (self.one_wire_master_file, _) = D505.get_latest_version(
            Path(self.hex_files_dir), "one-wire")

        if self.one_wire_master_file:
            self.program()
        else:
            QMessageBox.warning(self, "Error!", "Missing one-wire-master file!")

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
            self.one_wire_lbl.setText("Programming 1-wire master. . .")
            self.file_write_signal.emit(self.one_wire_master_file)
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
        pattern = r"([0-9]+\.[0-9a-zA-Z]+)"
        onewire_version = re.search(pattern, data)
        if (onewire_version):
            onewire_version_val = onewire_version.group()
            self.report.write_data("onewire_ver", onewire_version_val, "PASS")
            self.one_wire_lbl.setText("Version recorded.")
            self.tu.one_wire_prog_status.setText("1-Wire Programming: PASS")
            self.tu.one_wire_prog_status.setStyleSheet(D505.status_style_pass)
        else:
            self.report.write_data("onewire_ver", "N/A", "FAIL")
            self.tu.one_wire_prog_status.setText("Xmega Programming: FAIL")
            self.tu.one_wire_prog_status.setStyleSheet(D505.status_style_fail)
            QMessageBox.warning(self, "XMega3", "Bad command response.")

        self.is_complete = True
        self.complete_signal.emit()
