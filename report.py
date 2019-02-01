from os import path
from datetime import datetime as dt


class Report:
    def __init__(self):
        today = dt.now()
        self.date = f"{today.day:02d}-{today.month:02d}-{today.year}"
        self.data = {
            "Timestamp": None,
            "PCBA PN": None,
            "PCBA SN": None,
            "Date": self.date,
            "Tester ID": None,
            "Test Result": None,
            "Input Voltage": None,
            "Initial Current": None,
            "2V Supply": None,
            "5V Supply": None,
            "Xmega Bootloader Version": None,
            "Xmega App Version": None,
            "ATtiny Version": None,
            "BLE Version": None,
            "Temp ID": None,
            "Solar Charge Voltage": None,
            "Solar Charge Current": None,
            "Deep Sleep Current": None
        }
        self.file_path = ""

    def write_data(self, data_value):
        """Updates the data model with the received value."""
        if data_value[0] in self.data:
            self.data[data_value[0]] = data_value[1]
            return True
        return False

    def set_file_location(self, file_path):
        """Sets the file path for the report."""
        self.file_path = file_path

    def generate_report(self):
        """Writes all data in the data dictionary to an output file."""
        # Get the time again for a more accurate report timestamp.
        today = dt.now()
        self.data["Timestamp"] = (
            f"{today.year}-{today.month:02d}-{today.day:02d}"
            f" {today.hour:02d}:{today.minute:02d}"
            f":{today.second}"
        )
        name = path.join(self.file_path,
                         f"{self.date}-ID-{self.data['Tester ID']}.txt")
        f = open(name, "w")
        for key, val in self.data.items():
            f.write(f"{key}: {val}\n")
        f.close()


if __name__ == "__main__":
    report = Report()
    report.write_data(["Tester ID", 1234])
    report.write_data(["2V Supply", "2.31 V"])
    report.write_data(["Initial Current", "3.14 mA"])
    report.set_file_location("/home/samuel/Desktop/")
    report.generate_report()
