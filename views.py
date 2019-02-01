import re
import D505Procedure
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QPushButton, QVBoxLayout, QApplication, QLabel,
    QLineEdit, QComboBox, QGridLayout, QGroupBox, QHBoxLayout,
    QMessageBox, QAction, QFileDialog, QDialog
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QSettings


VERSION_NUM = "v0.1"

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 750

ABOUT_TEXT = f"""
             PCB assembly test utility. Copyright Beaded Streams, 2018.
             {VERSION_NUM}
             """


class TestUtility(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("BeadedStream", "PCBTestUtility")

        settings_defaults = {
            "port1_tac_id": "",
            "port2_tac_id": "",
            "port3_tac_id": "",
            "port4_tac_id": "",
            "iridium_imei": "300434063218220",
            "lat_start": "48 01 N",
            "lat_stop": "48 04 N",
            "lon_start": "123 02 W",
            "lon_stop": "123 05 W",
            "hex_file_path": "/path/to/hex/file",
            "report_file_path": "/path/to/report/folder"
        }

        for key in settings_defaults:
            if not self.settings.value(key):
                self.settings.setValue(key, settings_defaults[key])

        # Create program actions.
        self.config = QAction("Settings", self)
        self.config.setShortcut("Ctrl+E")
        self.config.setStatusTip("Program Settings")
        self.config.triggered.connect(self.configuration)

        self.quit = QAction("Quit", self)
        self.quit.setShortcut("Ctrl+Q")
        self.quit.setStatusTip("Exit Program")
        self.quit.triggered.connect(self.close)

        self.about_tu = QAction("About Test Utility", self)
        self.about_tu.setShortcut("Ctrl+U")
        self.about_tu.setStatusTip("About Program")
        self.about_tu.triggered.connect(self.about_program)

        self.aboutqt = QAction("About Qt", self)
        self.aboutqt.setShortcut("Ctrl+I")
        self.aboutqt.setStatusTip("About Qt")
        self.aboutqt.triggered.connect(self.about_qt)

        self.port = QAction("Port", self)
        self.port.setShortcut("Ctrl+P")
        self.port.setStatusTip("Select serial port")
        self.port.triggered.connect(self.scan_ports)

        # Create menubar
        self.menubar = self.menuBar()
        self.file_menu = self.menubar.addMenu("&File")
        self.file_menu.addAction(self.config)
        self.file_menu.addAction(self.quit)
        self.serial_menu = self.menubar.addMenu("&Serial")
        self.serial_menu.addAction(self.port)
        self.help_menu = self.menubar.addMenu("&Help")
        self.help_menu.addAction(self.about_tu)
        self.help_menu.addAction(self.aboutqt)

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

    def about_qt(self):
        QMessageBox.aboutQt(self, "About Qt")

    def scan_ports(self):
        print("Scanning serial port")

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

        self.settings_widget = QDialog(self)

        port1_lbl = QLabel("Port 1 TAC ID:")
        self.port1_tac_id = QLineEdit(self.settings.value("port1_tac_id"))
        port2_lbl = QLabel("Port 2 TAC ID:")
        self.port2_tac_id = QLineEdit(self.settings.value("port2_tac_id"))
        port3_lbl = QLabel("Port 3 TAC ID:")
        self.port3_tac_id = QLineEdit(self.settings.value("port3_tac_id"))
        port4_lbl = QLabel("Port 4 TAC ID:")
        self.port4_tac_id = QLineEdit(self.settings.value("port4_tac_id"))

        port_layout = QGridLayout()
        port_layout.addWidget(port1_lbl, 0, 0)
        port_layout.addWidget(self.port1_tac_id, 0, 1)
        port_layout.addWidget(port2_lbl, 1, 0)
        port_layout.addWidget(self.port2_tac_id, 1, 1)
        port_layout.addWidget(port3_lbl, 2, 0)
        port_layout.addWidget(self.port3_tac_id, 2, 1)
        port_layout.addWidget(port4_lbl, 3, 0)
        port_layout.addWidget(self.port4_tac_id, 3, 1)

        port_group = QGroupBox("TAC IDs")
        port_group.setLayout(port_layout)

        self.iridium_imei = QLineEdit()
        self.iridium_imei.setText(self.settings.value("iridium_imei"))

        iridium_layout = QVBoxLayout()
        iridium_layout.addWidget(self.iridium_imei)

        iridium_group = QGroupBox("Iridium IMEI")
        iridium_group.setLayout(iridium_layout)

        self.lat_start = QLineEdit(self.settings.value("lat_start"))
        lat_lbl = QLabel("to")
        self.lat_stop = QLineEdit(self.settings.value("lat_stop"))
        self.lon_start = QLineEdit(self.settings.value("lon_start"))
        lon_lbl = QLabel("to")
        self.lon_stop = QLineEdit(self.settings.value("lon_stop"))

        lat_layout = QHBoxLayout()
        lat_layout.addWidget(self.lat_start)
        lat_layout.addWidget(lat_lbl)
        lat_layout.addWidget(self.lat_stop)

        lon_layout = QHBoxLayout()
        lon_layout.addWidget(self.lon_start)
        lon_layout.addWidget(lon_lbl)
        lon_layout.addWidget(self.lon_stop)

        location_layout = QVBoxLayout()
        location_layout.addLayout(lat_layout)
        location_layout.addLayout(lon_layout)

        location_limits_group = QGroupBox("Location Limits")
        location_limits_group.setLayout(location_layout)

        self.hex_btn = QPushButton("[...]")
        self.hex_btn.setFixedWidth(FILE_BTN_WIDTH)
        self.hex_btn.clicked.connect(self.choose_hex_file)
        self.hex_lbl = QLabel("Choose hex file: ")
        self.hex_path_lbl = QLabel(self.settings.value("hex_file_path"))

        self.report_btn = QPushButton("[...]")
        self.report_btn.setFixedWidth(FILE_BTN_WIDTH)
        self.report_btn.clicked.connect(self.set_report_location)
        self.report_lbl = QLabel("Set report save location: ")
        self.report_path_lbl = QLabel(self.settings.value("report_file_path"))

        save_loc_layout = QGridLayout()
        save_loc_layout.addWidget(self.hex_lbl, 0, 0)
        save_loc_layout.addWidget(self.hex_btn, 0, 1)
        save_loc_layout.addWidget(self.hex_path_lbl, 1, 0)
        save_loc_layout.addWidget(self.report_lbl, 2, 0)
        save_loc_layout.addWidget(self.report_btn, 2, 1)
        save_loc_layout.addWidget(self.report_path_lbl, 3, 0)

        save_loc_group = QGroupBox("Save Locations")
        save_loc_group.setLayout(save_loc_layout)

        # self.theme_group = QGroupBox("Color Themes")

        # self.default = QRadioButton("Default")
        # self.dark = QRadioButton("Dark")
        # self.light = QRadioButton("Light")

        # self.default.setChecked(True)

        # self.theme_layout = QVBoxLayout()
        # self.theme_layout.addWidget(self.default)
        # self.theme_layout.addWidget(self.dark)
        # self.theme_layout.addWidget(self.light)

        # self.theme_group.setLayout(self.theme_layout)

        apply_btn = QPushButton("Apply Settings")
        apply_btn.clicked.connect(self.apply_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.cancel_settings)

        button_layout = QHBoxLayout()
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(apply_btn)

        hbox_top = QHBoxLayout()
        hbox_top.addWidget(port_group)
        hbox_top.addWidget(iridium_group)
        hbox_top.addWidget(location_limits_group)

        hbox_bottom = QHBoxLayout()
        hbox_bottom.addStretch()
        hbox_bottom.addWidget(save_loc_group)
        hbox_bottom.addStretch()

        grid = QGridLayout()
        grid.addLayout(hbox_top, 0, 0)
        grid.addLayout(hbox_bottom, 1, 0)
        # grid.addWidget(self.theme_group, 1, 1)
        grid.addLayout(button_layout, 2, 0)
        grid.setHorizontalSpacing(100)

        self.settings_widget.setLayout(grid)
        self.settings_widget.setWindowTitle("D505 Configuration Settings")
        self.settings_widget.show()
        self.settings_widget.resize(800, 200)

    def choose_hex_file(self):
        hex_file_path = QFileDialog.getOpenFileName(
            self,
            "Select hex file",
            "",
            "Hex File (*.hex)"
        )[0]
        self.hex_path_lbl.setText(hex_file_path)

    def set_report_location(self):
        report_dir = QFileDialog.getExistingDirectory(
            self,
            "Select report save location"
        )
        self.report_path_lbl.setText(report_dir)

    def cancel_settings(self):
        self.settings_widget.close()

    def apply_settings(self):
        ports = {
            "port1_tac_id": self.port1_tac_id,
            "port2_tac_id": self.port2_tac_id,
            "port3_tac_id": self.port3_tac_id,
            "port4_tac_id": self.port4_tac_id
        }

        for key, port in ports.items():
            p = r"([a-fA-F0-9][a-fA-F0-9]\s+){5}([a-fA-F0-9][a-fA-F0-9]\s*){1}"
            if (re.fullmatch(p, port.text())):
                self.settings.setValue(key, port.text())

            else:
                QMessageBox.warning(self.settings_widget,
                                    "Warning!",
                                    f"Bad TAC ID on Port {key[4]}!")
                return

        self.settings.setValue("iridium_imei", self.iridium_imei.text())
        self.settings.setValue("lat_start", self.lat_start.text())
        self.settings.setValue("lat_stop", self.lat_stop.text())
        self.settings.setValue("lon_start", self.lon_start.text())
        self.settings.setValue("lon_stop", self.lon_stop.text())
        self.settings.setValue("hex_file_path", self.hex_path_lbl.text())
        self.settings.setValue("report_file_path", self.report_path_lbl.text())

        QMessageBox.information(self.settings_widget, "Information",
                                "Settings applied!")
        self.settings_widget.close()

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
