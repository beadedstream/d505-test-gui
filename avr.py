import os
from subprocess import check_output
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot


class FlashD505(QObject):
    command_succeeded = pyqtSignal(str)
    command_failed = pyqtSignal(str)
    flash_finished = pyqtSignal()

    def __init__(self, install_files_path):
        super().__init__()
        os.chdir(install_files_path)
        chip_erase = "atprogram -t avrispmk2 -i pdi -d atxmega256a3 chiperase"
        prog_boot = ("atprogram -t avrispmk2 -i pdi -d atxmega256a3 program"
                     " --flash -f boot-section.hex --format hex --verify")
        prog_app = ("atprogram -t avrispmk2 -i pdi -d atxmega256a3 program"
                     " --flash -f  app-section.hex --format hex --verify")
        prog_main = ("atprogram -t avrispmk2 -i pdi -d atxmega256a3 program"
                    " --flash -f  main-app.hex --format hex --verify")
        write_fuses = ("atprogram -t avrispmk2 -i pdi -d atxmega256a3  write"
                       " --fuses --values FF00BDFFFEDE")
        write_lockbits = ("atprogram -t avrispmk2 -i pdi -d atxmega256a3  write"
                          " --lockbits --values FC")

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
                status = check_output(cmd, shell=True).decode()

                if "Firmware check OK" in status:
                    self.command_succeeded.emit(cmd_text)
                else:
                    self.command_failed.emit(cmd_text)
                    break

            except ValueError:
                self.command_failed.emit(cmd_text)
                break

        self.flash_finished.emit()
