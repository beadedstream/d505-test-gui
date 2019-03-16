from pathlib import Path
import subprocess
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot


class FlashD505(QObject):
    command_succeeded = pyqtSignal(str)
    command_failed = pyqtSignal(str)
    flash_finished = pyqtSignal()
    process_error_signal = pyqtSignal()

    def __init__(self, atprogram_path, hex_files_path):
        super().__init__()

        boot_file = str(Path.joinpath(hex_files_path, "boot-section.hex"))
        app_file = str(Path.joinpath(hex_files_path, "app-section.hex"))
        main_file = str(Path.joinpath(hex_files_path, "main-app.hex"))

        chip_erase = [atprogram_path,
                      "-t", "avrispmk2",
                      "-i", "pdi",
                      "-d", "atxmega256a3",
                      "chiperase"]
        prog_boot = [atprogram_path,
                     "-t", "avrispmk2",
                     "-i", "pdi",
                     "-d", "atxmega256a3",
                     "program",
                     "--flash", "-f", boot_file,
                     "--format", "hex",
                     "--verify"]
        prog_app = [atprogram_path,
                    "-t", "avrispmk2",
                    "-i", "pdi",
                    "-d", "atxmega256a3",
                    "program",
                    "--flash", "-f", app_file,
                    "--format", "hex",
                    "--verify"]
        prog_main = [atprogram_path,
                     "-t", "avrispmk2",
                     "-i", "pdi",
                     "-d", "atxmega256a3",
                     "program",
                     "--flash", "-f", main_file,
                     "--format", "hex",
                     "--verify"]
        write_fuses = [atprogram_path,
                       "-t", "avrispmk2",
                       "-i", "pdi",
                       "-d", "atxmega256a3",
                       "write",
                       "--fuses", "--values", "FF00BDFFFEDE"]
        write_lockbits = [atprogram_path,
                          "-t", "avrispmk2",
                          "-i", "pdi",
                          "-d", "atxmega256a3",
                          "write",
                          "--lockbits", "--values", "FC"]

        # Command status is for the subsequent step
        self.commands = {"chip_erase": chip_erase,
                         "prog_boot": prog_boot,
                         "prog_app": prog_app,
                         "prog_main": prog_main,
                         "write_fuses": write_fuses,
                         "write_lockbits": write_lockbits}

    @pyqtSlot()
    def flash(self):

        for cmd_text, cmd in self.commands.items():
            try:
                status = subprocess.check_output(cmd).decode()

                if "Firmware check OK" in status:
                    self.command_succeeded.emit(cmd_text)
                else:
                    self.command_failed.emit(cmd_text)
                    break

            except ValueError:
                self.command_failed.emit(cmd_text)
                break
            except subprocess.CalledProcessError:
                self.process_error_signal.emit()
                break

        self.flash_finished.emit()
