import time
import serial
import serial.tools.list_ports


class Uart:
    def __init__(self):
        self.ser = None

    def scan_ports():
        return serial.tools.list_ports.comports()

    def send_command(self, command):
        self.ser.write((command + "\r").encode())
        return self.ser.read_until(b"\r\n>")

    # def watchdog(self):
    #     self.ser.write(b"watchdog\r")
    #     # Number of bytes to read the results of the watchdog command
    #     return self.ser.read(172).decode().strip("\r\n")

    def open_port(self, port):
        try:
            self.ser = serial.Serial(port, 115200, timeout=90,
                                     parity=serial.PARITY_NONE, rtscts=False,
                                     xonxoff=False, dsrdtr=False)
            return True
        except serial.SerialException:
            return False

    def close_port(self):
        try:
            self.ser.close()
            return True
        except serial.SerialException:
            return False


if __name__ == "__main__":
    uart = Uart()
    uart.open_port("COM4")
    print(uart.send_command("psoc-version"))
    print(uart.send_command("spot-read"))
    print(uart.send_command("watchdog"))
    uart.close_port()
