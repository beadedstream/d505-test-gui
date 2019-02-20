import time
import serial
import serial.tools.list_ports
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot


class SerialManager(QObject):
    data_ready = pyqtSignal(str)
    no_port_sel = pyqtSignal()
    sleep_finished = pyqtSignal()
    line_written = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ser = serial.Serial(None, 115200, timeout=30,
                                 parity=serial.PARITY_NONE, rtscts=False,
                                 xonxoff=False, dsrdtr=False)

    def scan_ports():
        return serial.tools.list_ports.comports()

    @pyqtSlot(str)
    def send_command(self, command):
        if self.ser.is_open:
            self.flush_buffers()
            command = (command + "\r\n").encode()
            self.ser.write(command)
            data = self.ser.read_until(b"\r\n> ").decode()
            self.data_ready.emit(data)
        else:
            self.no_port_sel.emit()

    @pyqtSlot()
    def one_wire_test(self):
        if self.ser.is_open:
            self.ser.write("1-wire-test\r".encode())
            time.sleep(1)
            self.ser.write(" ".encode())
            time.sleep(0.3)
            self.ser.write(".".encode())
            # self.ser.read(self.ser.in_waiting)
            data = self.ser.read_until(b"\r\n> ").decode()
            self.data_ready.emit(data)
        else:
            self.no_port_sel.emit()

    @pyqtSlot()
    def reprogram_one_wire(self):
        if self.ser.is_open:
            self.ser.write("reprogram-1-wire-master\r\n".encode())
            # Wait for serial buffer to fill
            time.sleep(5)
            num_bytes = self.ser.in_waiting
            data = self.ser.read(num_bytes).decode()
            self.data_ready.emit(data)
        else:
            self.no_port_sel.emit()

    @pyqtSlot(str)
    def write_hex_file(self, file_path):
        if self.ser.is_open:
            try:
                with open(file_path, "rb") as f:
                    for line in f:
                        # hex_data = bytes.fromhex(line.strip("\n").strip(":"))
                        # print(hex_data)
                        self.ser.write(line)
                        self.line_written.emit()
                        # 50 ms delay required after each line
                        time.sleep(0.060)
            except SyntaxError:
                print("Syntax Error")

            time.sleep(3)
            data = self.ser.read_until(b"\r\n> ").decode()
            # num_bytes = self.ser.in_waiting
            # print(num_bytes)
            # data = self.ser.read(num_bytes).decode()
            self.data_ready.emit(data)
        else:
            self.no_port_sel.emit()

    @pyqtSlot(int)
    def sleep(self, interval):
        time.sleep(interval)
        self.sleep_finished.emit()

    def is_connected(self, port):
        try:
            self.ser.write(b"\r\n")
        except serial.serialutil.SerialException:
            return False
        return self.ser.port == port and self.ser.is_open

    def open_port(self, port):
        self.ser.close()
        self.ser = serial.Serial(port, 115200, timeout=45,
                                 parity=serial.PARITY_NONE, rtscts=False,
                                 xonxoff=False, dsrdtr=False)

    def flush_buffers(self):
        self.ser.write("\r\n".encode())
        time.sleep(1)
        self.ser.read(self.ser.in_waiting)
        self.ser.reset_output_buffer()
        self.ser.reset_input_buffer()

    def close_port(self):
        self.ser.close()
