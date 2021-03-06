import csv
from os import path
from datetime import datetime as dt


class Report:
    """Test Report class. Tracks status of tests and creates test report.
    
    Instance Variables
    timestamp   -- Used to store the current timestamp for naming the report.
    date        -- Stores date in dd--mm--yy format.
    test_result -- Boolean storing success or failure of the sum of the tests.
    data        -- Dictionary of test variables and their results and values.

    Instance Methods
    write_data          -- Updates data model.
    set_file_location   -- Sets file path for report location.
    generate_report     -- Generates report and saves to path location.
    """

    def __init__(self):
        today = dt.now()
        self.timestamp = None
        self.date = f"{today.day:02d}-{today.month:02d}-{today.year}"
        self.test_result = None
        # Data format: key | [value, units, test-passed]
        self.data = {
            # key : ["Name", value, PASS/FAIL]
            "timestamp": ["Timestamp", None, "PASS"],
            "pcba_pn": ["PCBA PN", None, None],
            "pcba_sn": ["PCBA SN", None, None],
            "tester_id": ["Tester ID", None, None],
            "input_v": ["Input Voltage (V)", None, None],
            "input_i": ["Input Current (mA)", None, None],
            "supply_2v": ["2V Supply (V)", None, None],
            "coin_cell_v": ["Coin Cell Voltage (V)", None, None],
            "supply_5v": ["5V Supply (V)", None, None],
            "uart_5v": ["UART 5V (V)", None, None],
            "off_5v": ["5V Off (V)", None, None],
            "xmega_bootloader": ["Xmega Bootloader Version", None, None],
            "xmega_app": ["Xmega App Version", None, None],
            "onewire_ver": ["1WireMaster Version", None, None],
            "ble_prog": ["Cypress BLE Programming", "", None],
            "bt_comms": ["Bluetooth Comms to 505", "", None],
            "ble_ver": ["BLE Version", None, "", None],
            "bat_v": ["Battery Voltage (V)", None, None],
            "iridium_match": ["Iridium Connected", None, None],
            "board_id": ["Board ID", None, None],
            "tac_connected_1": ["TAC Port 1 Connected", None, None],
            "tac_connected_2": ["TAC Port 2 Connected", None, None],
            "tac_connected_3": ["TAC Port 3 Connected", None, None],
            "tac_connected_4": ["TAC Port 4 Connected", None, None],
            "flash_comms": ["Flash Communication", None, None],
            "rtc_alarm": ["RTC Alarm", None, "PASS"],
            "gps_comms": ["GPS Connected", None, None],
            "sonic_connected": ["Sonic Device Connected (cm)", None, None],
            "hall_effect": ["Hall Effect Sensor", None, None],
            "solar_v": ["Solar Charge Voltage (V)", None, None],
            "solar_i": ["Solar Charge Current (mA)", None, None],
            "deep_sleep_i": ["Deep Sleep Current (uA)", None, None],
            "uart_comms": ["UART Power", None, None],
            "g_led_test": ["Green LED Test", None, None],
            "b_led_test": ["Blue LED Test", None, None],
            "r_led_test": ["Red LED Test", None, None]
        }
        self.file_path = ""

    def write_data(self, data_key, data_value, status):
        """Updates the data model with the received value and a bool
        indicating if the test passed or not. If the test failed and isn't
        already in the list of data, include it.
        """
        self.data[data_key][1] = data_value
        self.data[data_key][2] = status

    def set_file_location(self, file_path):
        """Sets the file path for the report's save location."""
        self.file_path = file_path

    def generate_report(self):
        """Writes all data in the data dictionary to an output file."""
        # Get the time again for a more accurate report timestamp.
        today = dt.now()
        self.timestamp = (
            f"{today.year}-{today.month:02d}-{today.day:02d}"
            f" {today.hour:02d}:{today.minute:02d}"
            f":{today.second}"
        )
        self.data["timestamp"][1] = self.timestamp
        # Filename-friendly timestamp
        ts = self.timestamp.replace(":", "-")
        sn = self.data["pcba_sn"][1]
        id = self.data["tester_id"][1]

        name = path.join(self.file_path, f"{sn}_{ts}-ID-{id}.csv")

        # Check for any tests that failed.
        for _, test in self.data.items():
            if test[2] == "FAIL":
                self.test_result = "FAIL"
                name = name[:-4] + "_FAIL.csv"
                break
            self.test_result = "PASS"

        f = open(name, "w", newline='')
        csvwriter = csv.writer(f)

        csvwriter.writerow(["Name", "Value", "Pass/Fail"])
        csvwriter.writerow(["Test Result", "", self.test_result])
        for _, test in self.data.items():
            csvwriter.writerow([test[0], test[1], test[2]])
        f.close()
