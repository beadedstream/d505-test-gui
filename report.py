from os import path
from datetime import datetime as dt


class Report:
    def __init__(self):
        today = dt.now()
        self.timestamp = None
        self.date = f"{today.day:02d}-{today.month:02d}-{today.year}"
        # Data format: key | [value, units, test-passed]
        self.data = {
            "Timestamp": [None, "", True],
            "PCBA PN": [None, "", False],
            "PCBA SN": [None, "", False],
            "Tester ID": [None, "", False],
            "Test Result": [None, "", False],
            "Input Voltage": [None, "V", False],
            "Input Current": [None, "mA", False],
            "2V Supply": [None, "V", False],
            "5V Supply": [None, "V", False],
            "Xmega Bootloader Version": [None, "", False],
            "Xmega App Version": [None, "", False],
            "ATtiny Version": [None, "", False],
            "BLE Version": [None, "", False],
            "Temp ID": [None, "", False],
            "Solar Charge Voltage": [None, "V", False],
            "Solar Charge Current": [None, "mA", False],
            "Deep Sleep Current": [None, "uA", False]
        }
        self.file_path = ""

    def write_data(self, data_key, data_value, passed):
        """Updates the data model with the received value and a bool
        indicating if the test passed or not.
        """
        if data_key in self.data:
            self.data[data_key][0] = data_value
            self.data[data_key][2] = passed
            return True
        return False

    def set_file_location(self, file_path):
        """Sets the file path for the report."""
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
        self.data["Timestamp"][0] = self.timestamp
        # Filename-friendly timestamp
        ts = self.timestamp.replace(":", "-")
        name = path.join(
            self.file_path,
            f"{ts}-ID-{self.data['Tester ID'][0]}.txt")
        f = open(name, "w")
        for key, value in self.data.items():
            v = str(value[0]) + " " + value[1]
            if value[2]:
                f.write(f"{key:<25}: {v:<20}\n")
            else:
                f.write(f"{key:<25}: {v:<20} -- {'FAIL':<10}\n")

        f.close()
