import D505Procedure
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QPushButton, QVBoxLayout, QApplication, QLabel,
    QLineEdit, QComboBox, QGridLayout, QGroupBox, QCheckBox, QHBoxLayout,
    QMessageBox, QAction, QFileDialog, QDialog
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QSettings


VERSION_NUM = "v0.1"

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 750

ABOUT_TEXT = """
             PCB assembly test utility. Copyright Beaded Streams, 2018.
             """


class TestUtility(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("BeadedStream", "PCBTestUtility")

        settings_defaults = {
             "hex_file_path": "/path/to/hex/file",
             "report_file_path": "/path/to/report/folder",
             "config_file_path": "/path/to/config/file",
             "iridium_imei": "300434063218220",
             "lat_start": "48 01 N",
             "lat_stop": "48 04 N",
             "lon_start": "123 02 W",
             "lon_stop": "123 05 W",
             "test": "value"
             }

        for key in settings_defaults:
            if not self.settings.value(key):
                self.settings.setValue(key, settings_defaults[key])

        # Create program actions.
        self.save = QAction("Save As. . .", self)
        self.save.setShortcut("Ctrl+S")
        self.save.setStatusTip("Set report save location")
        self.save.triggered.connect(self.save_location)

        self.config = QAction("Settings", self)
        self.config.setShortcut("Ctrl+E")
        self.config.setStatusTip("Program Settings")
        self.config.triggered.connect(self.configuration)

        self.quit = QAction("Quit", self)
        self.quit.setShortcut("Ctrl+Q")
        self.quit.setStatusTip("Exit Program")
        self.quit.triggered.connect(self.close)

        self.about = QAction("About", self)
        self.about.setShortcut("Ctrl+A")
        self.about.setStatusTip("About Program")
        self.about.triggered.connect(self.about_program)

        # Create menubar
        self.menubar = self.menuBar()
        self.file_menu = self.menubar.addMenu("&File")
        self.file_menu.addAction(self.save)
        self.file_menu.addAction(self.config)
        self.file_menu.addAction(self.quit)
        self.serial_menu = self.menubar.addMenu("&Serial")
        self.about_menu = self.menubar.addMenu("&About")
        self.about_menu.addAction(self.about)

        self.initUI()

    def initUI(self):
        RIGHT_SPACING = 350
        LINE_EDIT_WIDTH = 200
        self.central_widget = QWidget()

        self.tester_id_lbl = QLabel("Please enter tester ID: ")
        self.pcba_pn_lbl = QLabel("Please select PCBA part number: ")
        self.pcba_sn_lbl = QLabel("Please enter or scan DUT serial number: ")

        self.tester_id_input = QLineEdit()
        self.pcba_sn_input = QLineEdit()
        self.tester_id_input.setFixedWidth(LINE_EDIT_WIDTH)
        self.pcba_sn_input.setFixedWidth(LINE_EDIT_WIDTH)

        self.pcba_pn_input = QComboBox()
        self.pcba_pn_input.addItem("D505")
        self.pcba_pn_input.setFixedWidth(LINE_EDIT_WIDTH)

        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.start_procedure)
        self.start_btn.setFixedWidth(200)

        self.logo_img = QPixmap("Images/h_logo.png")
        self.logo_img = self.logo_img.scaledToWidth(600)
        self.logo = QLabel()
        self.logo.setPixmap(self.logo_img)

        hbox_logo = QHBoxLayout()
        hbox_logo.addStretch()
        hbox_logo.addWidget(self.logo)
        hbox_logo.addStretch()

        hbox_test_id = QHBoxLayout()
        hbox_test_id.addStretch()
        hbox_test_id.addWidget(self.tester_id_lbl)
        hbox_test_id.addWidget(self.tester_id_input)
        hbox_test_id.addSpacing(RIGHT_SPACING)

        hbox_pn = QHBoxLayout()
        hbox_pn.addStretch()
        hbox_pn.addWidget(self.pcba_pn_lbl)
        hbox_pn.addWidget(self.pcba_pn_input)
        hbox_pn.addSpacing(RIGHT_SPACING)

        hbox_sn = QHBoxLayout()
        hbox_sn.addStretch()
        hbox_sn.addWidget(self.pcba_sn_lbl)
        hbox_sn.addWidget(self.pcba_sn_input)
        hbox_sn.addSpacing(RIGHT_SPACING)

        hbox_start_btn = QHBoxLayout()
        hbox_start_btn.addStretch()
        hbox_start_btn.addWidget(self.start_btn)
        hbox_start_btn.addSpacing(RIGHT_SPACING)

        vbox = QVBoxLayout()
        vbox.addSpacing(50)
        vbox.addLayout(hbox_logo)
        vbox.addSpacing(50)
        vbox.addLayout(hbox_test_id)
        vbox.addSpacing(50)
        vbox.addLayout(hbox_pn)
        vbox.addSpacing(50)
        vbox.addLayout(hbox_sn)
        vbox.addSpacing(50)
        vbox.addLayout(hbox_start_btn)
        vbox.addSpacing(50)

        # Put an initial message on the statusbar.
        self.statusBar().showMessage("Set configuration settings!")

        self.central_widget.setLayout(vbox)
        self.setCentralWidget(self.central_widget)

        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowTitle("BeadedStream Manufacturing TestUtility")

    def about_program(self):
        QMessageBox.about(self, "About TestUtility", ABOUT_TEXT)

    def save_location(self):
        self.report_file_path = QFileDialog.getSaveFileName(
                                                            self,
                                                            "Choose save "
                                                            "location",
                                                            None)[0]

    def start_procedure(self):
        central_widget = QWidget()

        # _____User Inputted Values_____
        self.tester_id = self.tester_id_input.text()
        self.pcba_pn = self.pcba_pn_input.currentText()
        self.pcba_sn = self.pcba_sn_input.text()

        status_lbl_stylesheet = ("QLabel {border: 2px solid grey;"
                                 "color: black; font-size: 20px}")

        # ______Labels______
        self.tester_id_status = QLabel(f"Tester ID: {self.tester_id}")
        self.pcba_pn_status = QLabel(f"PCBA PN: {self.pcba_pn}")
        self.pcba_sn_status = QLabel(f"PCBA SN: {self.pcba_sn}")
        self.input_v_status = QLabel("Input Voltage:_____V")
        self.input_i_status = QLabel("Input Current:_____mA")
        self.supply_2v_status = QLabel("2V Supply_____V")
        self.supply_5v_status = QLabel("5V Supply_____V")
        self.xmega_prog_status = QLabel("Xmega Programming:_____")
        self.hall_effect_status = QLabel("Hall Effect Sensor Test:_____")
        self.ble_prog_status = QLabel("BLE Programming:_____")
        self.bluetooth_test_status = QLabel("Bluetooth Test:_____")
        self.led_test_status = QLabel("LED Test:_____")
        self.solar_charge_v_status = QLabel("Solar Charge Voltage:_____V")
        self.solar_charge_i_status = QLabel("Solar Charge Current:_____mA")
        self.deep_sleep_i_status = QLabel("Deep Sleep Current:_____uA")

        self.tester_id_status.setStyleSheet(status_lbl_stylesheet)
        self.pcba_pn_status.setStyleSheet(status_lbl_stylesheet)
        self.pcba_sn_status.setStyleSheet(status_lbl_stylesheet)
        self.input_v_status.setStyleSheet(status_lbl_stylesheet)
        self.input_i_status.setStyleSheet(status_lbl_stylesheet)
        self.supply_2v_status.setStyleSheet(status_lbl_stylesheet)
        self.supply_5v_status.setStyleSheet(status_lbl_stylesheet)
        self.xmega_prog_status.setStyleSheet(status_lbl_stylesheet)
        self.hall_effect_status.setStyleSheet(status_lbl_stylesheet)
        self.ble_prog_status.setStyleSheet(status_lbl_stylesheet)
        self.bluetooth_test_status.setStyleSheet(status_lbl_stylesheet)
        self.led_test_status.setStyleSheet(status_lbl_stylesheet)
        self.solar_charge_v_status.setStyleSheet(status_lbl_stylesheet)
        self.solar_charge_i_status.setStyleSheet(status_lbl_stylesheet)
        self.deep_sleep_i_status.setStyleSheet(status_lbl_stylesheet)

        # ______Layout______
        status_vbox1 = QVBoxLayout()
        status_vbox1.setSpacing(25)
        status_vbox1.addWidget(self.tester_id_status)
        status_vbox1.addWidget(self.pcba_pn_status)
        status_vbox1.addWidget(self.pcba_sn_status)
        status_vbox1.addWidget(self.input_v_status)
        status_vbox1.addWidget(self.input_i_status)
        status_vbox1.addWidget(self.supply_2v_status)
        status_vbox1.addWidget(self.supply_5v_status)
        status_vbox1.addWidget(self.xmega_prog_status)
        status_vbox1.addWidget(self.hall_effect_status)
        status_vbox1.addWidget(self.ble_prog_status)
        status_vbox1.addWidget(self.bluetooth_test_status)
        status_vbox1.addWidget(self.led_test_status)
        status_vbox1.addWidget(self.solar_charge_v_status)
        status_vbox1.addWidget(self.solar_charge_i_status)
        status_vbox1.addWidget(self.deep_sleep_i_status)
        status_vbox1.addStretch()

        status_group = QGroupBox("Test Statuses")
        status_group.setLayout(status_vbox1)

        procedure = D505Procedure.D505Procedure(self)

        grid = QGridLayout()
        grid.setColumnStretch(0, 5)
        grid.setColumnStretch(1, 15)
        grid.addWidget(status_group, 0, 0)
        grid.addWidget(procedure, 0, 1)

        central_widget.setLayout(grid)

        self.setCentralWidget(central_widget)

    def update_label(self):
        voltage = 4.2
        self.input_v_status.setText(f"Input Voltage: {voltage} V")

    def configuration(self):
        FILE_BTN_WIDTH = 30

        settings_widget = QDialog(self)

        hex_file_btn = QPushButton("[...]")
        hex_file_btn.setFixedWidth(FILE_BTN_WIDTH)
        hex_file_path = QLabel(self.settings.value("hex_file_path"))
        report_file_btn = QPushButton("[...]")
        report_file_btn.setFixedWidth(FILE_BTN_WIDTH)
        report_file_path = QLabel(self.settings.value("report_file_path"))
        config_file_btn = QPushButton("[...]")
        config_file_btn.setFixedWidth(FILE_BTN_WIDTH)
        config_file_path = QLabel(self.settings.value("config_file_path"))

        hex_file_layout = QHBoxLayout()
        hex_file_layout.addWidget(hex_file_path)
        hex_file_layout.addStretch()
        hex_file_layout.addWidget(hex_file_btn)

        report_file_layout = QHBoxLayout()
        report_file_layout.addWidget(report_file_path)
        report_file_layout.addStretch()
        report_file_layout.addWidget(report_file_btn)

        config_file_layout = QHBoxLayout()
        config_file_layout.addWidget(config_file_path)
        config_file_layout.addStretch()
        config_file_layout.addWidget(config_file_btn)

        save_loc_layout = QVBoxLayout()
        save_loc_layout.addLayout(hex_file_layout)
        save_loc_layout.addLayout(report_file_layout)
        save_loc_layout.addLayout(config_file_layout)

        save_loc_group = QGroupBox("Save Locations")
        save_loc_group.setLayout(save_loc_layout)

        iridium_imei = QLineEdit()
        iridium_imei.setText(self.settings.value("iridium_imei"))

        iridium_layout = QVBoxLayout()
        iridium_layout.addWidget(iridium_imei)

        iridium_group = QGroupBox("Iridium IMEI")
        iridium_group.setLayout(iridium_layout)

        lat_start = QLineEdit(self.settings.value("lat_start"))
        lat_lbl = QLabel("to")
        lat_stop = QLineEdit(self.settings.value("lat_stop"))
        lon_start = QLineEdit(self.settings.value("lon_start"))
        lon_lbl = QLabel("to")
        lon_stop = QLineEdit(self.settings.value("lon_stop"))

        lat_layout = QHBoxLayout()
        lat_layout.addWidget(lat_start)
        lat_layout.addWidget(lat_lbl)
        lat_layout.addWidget(lat_stop)

        lon_layout = QHBoxLayout()
        lon_layout.addWidget(lon_start)
        lon_layout.addWidget(lon_lbl)
        lon_layout.addWidget(lon_stop)

        location_layout = QVBoxLayout()
        location_layout.addLayout(lat_layout)
        location_layout.addLayout(lon_layout)

        location_limits_group = QGroupBox("Location Limits")
        location_limits_group.setLayout(location_layout)

        port1_lbl = QLabel("Port 1 TAC ID:")
        port1_tac_id = QLineEdit()
        port2_lbl = QLabel("Port 2 TAC ID:")
        port2_tac_id = QLineEdit()
        port3_lbl = QLabel("Port 3 TAC ID:")
        port3_tac_id = QLineEdit()
        port4_lbl = QLabel("Port 4 TAC ID:")
        port4_tac_id = QLineEdit()

        port_layout = QGridLayout()
        port_layout.addWidget(port1_lbl, 0, 0)
        port_layout.addWidget(port1_tac_id, 0, 1)
        port_layout.addWidget(port2_lbl, 1, 0)
        port_layout.addWidget(port2_tac_id, 1, 1)
        port_layout.addWidget(port3_lbl, 2, 0)
        port_layout.addWidget(port3_tac_id, 2, 1)
        port_layout.addWidget(port4_lbl, 3, 0)
        port_layout.addWidget(port4_tac_id, 3, 1)

        port_group = QGroupBox("TAC IDs")
        port_group.setLayout(port_layout)

        apply_btn = QPushButton("Apply Settings")
        cancel_btn = QPushButton("Cancel")

        button_layout = QHBoxLayout()
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(apply_btn)

        hbox_top = QHBoxLayout()
        hbox_top.addWidget(save_loc_group)
        hbox_top.addWidget(iridium_group)
        hbox_top.addWidget(location_limits_group)

        hbox_bottom = QHBoxLayout()
        hbox_bottom.addStretch()
        hbox_bottom.addWidget(port_group)
        hbox_bottom.addStretch()

        grid = QGridLayout()
        grid.addLayout(hbox_top, 0, 0)
        grid.addLayout(hbox_bottom, 1, 0)
        grid.addLayout(button_layout, 2, 0)
        grid.setHorizontalSpacing(100)

        settings_widget.setLayout(grid)
        settings_widget.setWindowTitle("D505 Configuration Settings")
        settings_widget.show()
        settings_widget.resize(800, 200)

    def save_settings(self):
        pass

    def closeEvent(self, event):
        event.accept()

        quit_msg = "Are you sure you want to exit the program?"
        confirmation = QMessageBox.question(self, 'Message',
                                            quit_msg, QMessageBox.Yes,
                                            QMessageBox.No)

        if confirmation == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication([])
    window = TestUtility()
    window.show()
    app.exit(app.exec_())
