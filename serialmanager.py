import time
import serial
import serial.tools.list_ports


class SerialManager:
    def __init__(self):
        self.ser = serial.Serial(None, 115200, timeout=90,
                                 parity=serial.PARITY_NONE, rtscts=False,
                                 xonxoff=False, dsrdtr=False)

    def scan_ports():
        return serial.tools.list_ports.comports()

    def send_command(self, command):
        self.ser.write((command + "\r").encode())
        return self.ser.read_until(b"\r\n>")

    def is_connected(self, port):
        return self.ser.port == port and self.ser.is_open

    def open_port(self, port):
        self.ser.close()
        self.ser.port = port
        self.ser.open()

    def close_port(self):
        self.ser.close()


if __name__ == "__main__":
    sm = SerialManager()
    sm.open_port("COM4")
    print(sm.send_command("psoc-version"))
    print(sm.send_command("spot-read"))
    print(sm.send_command("watchdog"))
    sm.close_port()
