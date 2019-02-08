import time
import serial
import serial.tools.list_ports
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot


class SerialManager(QObject):
    data_ready = pyqtSignal(str)
    no_port_sel = pyqtSignal()
    sleep_finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ser = serial.Serial(None, 115200, timeout=90,
                                 parity=serial.PARITY_NONE, rtscts=False,
                                 xonxoff=False, dsrdtr=False)

    def scan_ports():
        return serial.tools.list_ports.comports()

    @pyqtSlot(str)
    def send_command(self, command):
        if self.ser.is_open:
            self.ser.write((command + "\r").encode())
            data = self.ser.read_until(b"\r\n>").decode()
            self.data_ready.emit(data)
        else:
            self.no_port_sel.emit()

    @pyqtSlot(int)
    def sleep(self, interval):
        time.sleep(interval)
        self.sleep_finished.emit()

    def is_connected(self, port):
        return self.ser.port == port and self.ser.is_open

    def open_port(self, port):
        self.ser.close()
        self.ser = serial.Serial(port, 115200, timeout=90,
                                 parity=serial.PARITY_NONE, rtscts=False,
                                 xonxoff=False, dsrdtr=False)

        # self.ser.open()

    def close_port(self):
        self.ser.close()


if __name__ == "__main__":
    sm = SerialManager()
    sm.open_port("COM4")
    print(sm.send_command("psoc-version"))
    print(sm.send_command("spot-read"))
    print(sm.send_command("watchdog"))
    sm.close_port()
