import time
import serial
import serial.tools.list_ports
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot


class SerialManager(QObject):
    data_ready = pyqtSignal(str)
    no_port_sel = pyqtSignal()
    sleep_finished = pyqtSignal()
    line_written = pyqtSignal()
    flash_test_failed = pyqtSignal()
    flash_test_succeeded = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ser = serial.Serial(None, 115200, timeout=30,
                                 parity=serial.PARITY_NONE, rtscts=False,
                                 xonxoff=False, dsrdtr=False)
        self.end = b"\r\n>"

    def scan_ports():
        return serial.tools.list_ports.comports()

    @pyqtSlot(str)
    def send_command(self, command):
        if self.ser.is_open:
            try:
                self.flush_buffers()
                command = (command + "\r\n").encode()
                self.ser.write(command)
                data = self.ser.read_until(self.end).decode()
                self.data_ready.emit(data)
            except serial.serialutil.SerialException:
                self.no_port_sel.emit()
        else:
            self.no_port_sel.emit()

    @pyqtSlot()
    def one_wire_test(self):
        if self.ser.is_open:
            try:
                self.ser.write("1-wire-test\r".encode())
                time.sleep(1)
                self.ser.write(" ".encode())
                time.sleep(0.3)
                self.ser.write(".".encode())
                data = self.ser.read_until(self.end).decode()
                self.data_ready.emit(data)
            except serial.serialutil.SerialException:
                self.no_port_sel.emit()
        else:
            self.no_port_sel.emit()

    @pyqtSlot()
    def reprogram_one_wire(self):
        if self.ser.is_open:
            try:
                self.ser.write("reprogram-1-wire-master\r\n".encode())
                # Wait for serial buffer to fill
                time.sleep(5)
                num_bytes = self.ser.in_waiting
                data = self.ser.read(num_bytes).decode()
                self.data_ready.emit(data)
            except serial.serialutil.SerialException:
                self.no_port_sel.emit()
        else:
            self.no_port_sel.emit()

    @pyqtSlot(str)
    def write_hex_file(self, file_path):
        if self.ser.is_open:
            try:
                with open(file_path, "rb") as f:
                    for line in f:
                        self.ser.write(line)
                        self.line_written.emit()
                        # minimum of 50 ms delay required after each line
                        time.sleep(0.060)
            except serial.serialutil.SerialException:
                self.no_port_sel.emit()

            time.sleep(3)
            data = self.ser.read_until(self.end).decode()
            self.data_ready.emit(data)
        else:
            self.no_port_sel.emit()

    @pyqtSlot()
    def iridium_command(self):
        if self.ser.is_open:
            try:
                self.ser.write(b"iridium\r\n")
                time.sleep(2)
                num_bytes = self.ser.in_waiting
                self.ser.read(num_bytes)
                self.ser.write(b"at+gsn\r\n")
                time.sleep(2)
                num_bytes = self.ser.in_waiting
                data = self.ser.read(num_bytes).decode()
                self.ser.write(b".\r\n")
                time.sleep(2)
                self.ser.read_until(self.end)
                self.data_ready.emit(data)
            except serial.serialutil.SerialException:
                self.no_port_sel.emit()
        else:
            self.no_port_sel.emit()

    @pyqtSlot()
    def flash_test(self):
        if self.ser.is_open:
            try:
                # Make sure there are no logs to start with
                self.ser.write(b"clear\r\n")
                self.ser.read_until(b"[Y/N]")
                self.ser.write(b"Y")
                self.ser.read_until(self.end)

                self.ser.write(b"flash-fill 1 3 1 1 1 1\r\n")
                self.ser.read_until(self.end)

                self.ser.write(b"data\r\n")
                data = self.ser.read_until(self.end)
                if b"... 3 records" not in data:
                    self.flash_test_failed.emit()
                    return

                self.ser.write(b"psoc-log-usage\r\n")
                data = self.ser.read_until(self.end)
                if b"used: 3" not in data:
                    self.flash_test_failed.emit()
                    return

                self.ser.write(b"clear\r\n")
                self.ser.read_until(b"[Y/N]")
                self.ser.write(b"Y")
                self.ser.read_until(self.end)

                self.ser.write(b"data\r\n")
                data = self.ser.read_until(self.end)
                if b"No data!" not in data:
                    self.flash_test_failed.emit()
                    return

                self.ser.write(b"psoc-log-usage\r\n")
                data = self.ser.read_until(self.end)
                if b"used: 0" not in data:
                    self.flash_test_failed.emit()
                    return
                self.flash_test_succeeded.emit()

            except serial.serialutil.SerialException:
                self.no_port_sel.emit()
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
