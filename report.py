import csv
from os import path
from datetime import datetime as dt


class Report:
    def __init__(self):
        today = dt.now()
        self.timestamp = None
        self.date = f"{today.day:02d}-{today.month:02d}-{today.year}"
        # Data format: key | [value, units, test-passed]
        self.data = {
            # key : ["Name", value, PASS/FAIL]
            "result": ["Test Result", None, "PASS"],
            "timestamp": ["Timestamp", None, "PASS"],
            "pcba_sn": ["PCBA PN", None, None],
            "pcba_pn": ["PCBA SN", None, None],
            "tester_id": ["Tester ID", None, None],
            "input_v": ["Input Voltage (V)", None, None],
            "input_i": ["Input Current (mA)", None, None],
            "supply_2v": ["2V Supply (V)", None, None],
            "supply_5v": ["5V Supply (V)", None, None],
            "uart_5v": ["UART 5V (V)", None, None],
            "off_5v": ["5V Off (V)", None, None],
            "xmega_bootloader": ["Xmega Bootloader Version", None, None],
            "xmega_app": ["Xmega App Version", None, None],
            "onewire_ver": ["1WireMaster Version", None, None],
            "ble_ver": ["BLE Version", None, "", None],
            "bat_v": ["Battery Voltage (V)", None, None],
            "serial_match": ["Serial Number Match", None, None],
            "iridium_match": ["Iridium Connected", None, None],
            "board_id": ["Board ID", None, None],
            "tac_connected": ["TAC Port Connected", None, None],
            "flash_comms": ["Flash Communication", None, None],
            "rtc_alarm": ["RTC Alarm", None, "PASS"],
            "gps_comms": ["GPS Connected", None, None],
            "sonic_connected": ["Sonic Device Connected (cm)", None, None],
            "solar_v": ["Solar Charge Voltage (V)", None, None],
            "solar_i": ["Solar Charge Current (mA)", None, None],
            "deep_sleep_i": ["Deep Sleep Current (uA)", None, None],
            "uart_comms": ["UART Communication w/o Battery", None, None],
            "led_test": ["LED Test", None, None]
        }
        self.file_path = ""

    def write_data(self, data_key, data_value, status):
        """Updates the data model with the received value and a bool
        indicating if the test passed or not. If the test failed and isn't
        already in the list of data, include it.
        """
        if (status == "FAIL"):
            self.data["result"][2] = "FAIL"

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

        # If the test failed, add "_FAIL" to the file name.s
        if self.data["result"][2] == "FAIL":
            name = name[:-4] + "_FAIL.csv"

        f = open(name, "w", newline='')
        csvwriter = csv.writer(f)

        csvwriter.writerow(["Name", "Value", "Pass/Fail"])

        for _, test in self.data.items():
            csvwriter.writerow([test[0], test[1], test[2]])
        f.close()

        # Reset the report status
        self.data["result"][2] = "PASS"
