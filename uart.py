import serial.tools.list_ports


class Uart:
    def __init__(self):
        pass

    def scan_ports():
        return serial.tools.list_ports.comports()

    def send_command(self, command):
        pass

    def open_port(self, port):
        pass

    def close_port(self, port):
        pass


if __name__ == "__main__":
    ports = Uart.scan_ports()
    for port in ports:
        print(port)
        print(port.device)
        print(port.name)
        print(port.hwid)
        print(port.product)
        print(port.manufacturer)
        print(port.vid)
        print(port.pid)
        print(port.serial_number)
        print(port.interface)
