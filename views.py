import B505Procedure
from datetime import datetime
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QVBoxLayout, \
    QApplication, QLabel, QLineEdit, QComboBox, QGridLayout, QSpacerItem, \
    QGroupBox, QCheckBox, QHBoxLayout, QMessageBox, QAction, QFileDialog
from PyQt5.QtGui import QPixmap, QFont
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
        self.initUI()

    def initUI(self):
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

        self.central_widget = QWidget()

        utility_version_lbl = QLabel(f"Utility Version: {VERSION_NUM}")
        large_arial_font = QFont("Arial", 20)
        utility_version_lbl.setFont(large_arial_font)
        date = datetime.today()

        date_formatted = f"Date: {date.year}-{date.month:02}-{date.day:02}"

        date_time_lbl = QLabel(date_formatted)

        date_time_lbl.setFont(large_arial_font)

        self.tester_id_lbl = QLabel("Please enter tester ID: ")
        self.pcba_pn_lbl = QLabel("Please select PCBA part number from drop"
                                  " down menu: ")
        self.pcba_sn_lbl = QLabel("Please enter or scan"
                                  " (using bar code scanner)"
                                  " DUT serial number: ")

        self.tester_id_input = QLineEdit()
        self.pcba_sn_input = QLineEdit()

        self.pcba_pn_input = QComboBox()
        self.pcba_pn_input.addItem("B505")

        config_btn = QPushButton("Setup Menu")
        config_btn.clicked.connect(self.configuration)
        start_btn = QPushButton("Start")
        start_btn.clicked.connect(self.start_procedure)

        self.logo_img = QPixmap("Images/h_logo.png")
        self.logo_img = self.logo_img.scaledToWidth(600)
        self.logo = QLabel()
        self.logo.setPixmap(self.logo_img)

        hbox_btns = QHBoxLayout()
        hbox_btns.addWidget(config_btn)
        hbox_btns.addWidget(start_btn)

        vbox_left = QVBoxLayout()
        vbox_left.addSpacing(50)
        vbox_left.addWidget(utility_version_lbl)
        vbox_left.addSpacing(25)
        vbox_left.addWidget(date_time_lbl)
        vbox_left.addSpacing(50)
        vbox_left.addWidget(self.tester_id_lbl)
        vbox_left.addWidget(self.tester_id_input)
        vbox_left.addSpacing(50)
        vbox_left.addWidget(self.pcba_pn_lbl)
        vbox_left.addWidget(self.pcba_pn_input)
        vbox_left.addSpacing(50)
        vbox_left.addWidget(self.pcba_sn_lbl)
        vbox_left.addWidget(self.pcba_sn_input)
        vbox_left.addSpacing(50)
        vbox_left.addLayout(hbox_btns)
        vbox_left.addStretch()

        vbox_right = QVBoxLayout()
        vbox_right.addStretch()
        vbox_right.addWidget(self.logo)
        vbox_right.addSpacing(50)
        vbox_right.addStretch()

        grid = QGridLayout()
        grid.addLayout(vbox_left, 0, 0)
        grid.addLayout(vbox_right, 0, 1)
        grid.setHorizontalSpacing(100)

        # Create program actions.
        quit = QAction("Quit", self)
        quit.setShortcut("Ctrl+Q")
        quit.setStatusTip("Exit Program")
        quit.triggered.connect(self.close)

        about = QAction("About", self)
        about.setShortcut("Ctrl+A")
        about.setStatusTip("About Program")
        about.triggered.connect(self.about_program)

        save = QAction("Save As. . .", self)
        save.setShortcut("Ctrl+S")
        save.setStatusTip("Set report save location")
        save.triggered.connect(self.save_location)

        # Create menubar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(quit)
        file_menu.addAction(save)
        about_menu = menubar.addMenu("&About")
        about_menu.addAction(about)

        # Put an initial message on the statusbar.
        self.statusBar().showMessage("Set configuration settings!")

        self.central_widget.setLayout(grid)
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

        procedure = B505Procedure.B505Procedure()

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
        central_widget = QWidget()

        hex_file_btn = QPushButton("Set hex file")
        hex_file_path = QLabel(self.settings.value("hex_file_path"))
        report_save_loc_btn = QPushButton("Set report save location")
        report_save_loc_path = QLabel(self.settings.value("report_file_path"))
        config_file_btn = QPushButton("Set configuration file location")
        config_file_path = QLabel(self.settings.value("config_file_path"))

        save_loc_layout = QVBoxLayout()
        save_loc_layout.addWidget(hex_file_btn)
        save_loc_layout.addWidget(hex_file_path)
        save_loc_layout.addWidget(report_save_loc_btn)
        save_loc_layout.addWidget(report_save_loc_path)
        save_loc_layout.addWidget(config_file_btn)
        save_loc_layout.addWidget(config_file_path)

        save_loc_group = QGroupBox("Save Locations")
        save_loc_group.setLayout(save_loc_layout)

        iridium_imei = QLineEdit()
        iridium_imei.setText(self.settings.value("iridium_imei"))
        iridium_imei.setReadOnly(True)
        iridium_imei_btn = QPushButton("Change IMEI")

        iridium_layout = QVBoxLayout()
        iridium_layout.addWidget(iridium_imei)
        iridium_layout.addWidget(iridium_imei_btn)

        iridium_group = QGroupBox("Iridium IMEI")
        iridium_group.setLayout(iridium_layout)

        lat_start = QLineEdit(self.settings.value("lat_start"))
        lat_start.setReadOnly(True)
        lat_lbl = QLabel("to")
        lat_stop = QLineEdit(self.settings.value("lat_stop"))
        lat_stop.setReadOnly(True)
        lon_start = QLineEdit(self.settings.value("lon_start"))
        lon_start.setReadOnly(True)
        lon_lbl = QLabel("to")
        lon_stop = QLineEdit(self.settings.value("lon_stop"))
        lon_stop.setReadOnly(True)
        location_limits_btn = QPushButton("Change Limits")

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
        location_layout.addWidget(location_limits_btn)

        location_limits_group = QGroupBox("Location Limits")
        location_limits_group.setLayout(location_layout)

        save_btn = QPushButton("Save Settings")

        vbox_left = QVBoxLayout()
        vbox_left.addWidget(save_loc_group)
        vbox_left.addSpacing(25)
        vbox_left.addWidget(iridium_group)
        vbox_left.addSpacing(25)
        vbox_left.addWidget(location_limits_group)
        vbox_left.addSpacing(25)
        vbox_left.addWidget(save_btn)

        vbox_right = QVBoxLayout()
        vbox_right.addStretch()
        vbox_right.addWidget(self.logo)
        vbox_right.addSpacing(50)
        vbox_right.addStretch()

        grid = QGridLayout()
        grid.addLayout(vbox_left, 0, 0)
        grid.addLayout(vbox_right, 0, 1)
        grid.setHorizontalSpacing(100)

        central_widget.setLayout(grid)
        self.setCentralWidget(central_widget)

    def save_settings(self):
        pass

if __name__ == "__main__":
    app = QApplication([])
    window = TestUtility()
    window.show()
    app.exit(app.exec_())
