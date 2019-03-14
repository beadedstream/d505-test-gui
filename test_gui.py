import random
from pathlib import Path
from views import TestUtility
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWizard


def test_success(qtbot):
    gui = TestUtility()
    qtbot.addWidget(gui)
    gui.show()
    qtbot.wait_for_window_shown(gui)

    tester_id = str(random.randint(1, 100000))

    report_dir = Path(
        r"C:\Users\samuel\Documents\BeadedStream GUI\test_reports"
    )

    qtbot.mouseClick(gui.start_btn, Qt.LeftButton)
    qtbot.mouseClick(gui.err_msg.buttons()[0], Qt.LeftButton)
    assert gui.err_msg.informativeText() == "Missing value!"

    qtbot.keyClicks(gui.tester_id_input, tester_id)
    qtbot.mouseClick(gui.start_btn, Qt.LeftButton)
    qtbot.mouseClick(gui.err_msg.buttons()[0], Qt.LeftButton)
    assert gui.err_msg.informativeText() == "Missing value!"

    qtbot.keyClicks(gui.pcba_sn_input, "654321")
    qtbot.mouseClick(gui.start_btn, Qt.LeftButton)
    qtbot.mouseClick(gui.err_msg.buttons()[0], Qt.LeftButton)
    assert gui.err_msg.informativeText() == "Bad serial number!"

    # Manually populate serial ports since it's difficult to simulate clicking
    # on a menu widget
    gui.populate_ports()
    assert gui.ports_group.actions()[0].text()[0:4] == "COM4"

    # Trigger action so the port gets connected
    gui.ports_group.actions()[0].trigger()

    gui.pcba_sn_input.clear()
    qtbot.keyClicks(gui.pcba_sn_input, "D5050076")
    qtbot.mouseClick(gui.start_btn, Qt.LeftButton)

    # SETUP
    # gui.procedure.setup_page.step_a_chkbx.click()
    qtbot.wait(2000)
    qtbot.mouseClick(gui.procedure.setup_page.step_a_chkbx, Qt.LeftButton)
    qtbot.wait(5000)
    qtbot.keyClicks(gui.procedure.setup_page.step_b_input, "6.0")
    qtbot.keyClicks(gui.procedure.setup_page.step_c_input, "4.0")
    qtbot.keyClicks(gui.procedure.setup_page.step_d_input, "2.0")
    qtbot.wait(2000)

    qtbot.mouseClick(gui.procedure.setup_page.submit_button, Qt.LeftButton)

    qtbot.wait(2000)

    qtbot.mouseClick(gui.procedure.button(QWizard.NextButton),
                     Qt.LeftButton)
    qtbot.wait(2000)

    # WATCHDOG
    qtbot.mouseClick(gui.procedure.watchdog_page.batch_chkbx, Qt.LeftButton)
    qtbot.wait(25000)
    qtbot.mouseClick(gui.procedure.watchdog_page.xmega_disconnect_chkbx,
                     Qt.LeftButton)
    qtbot.wait(21000)
    qtbot.keyClicks(gui.procedure.watchdog_page.supply_5v_input, "5.0")
    qtbot.wait(2000)
    qtbot.mouseClick(gui.procedure.watchdog_page.supply_5v_input_btn,
                     Qt.LeftButton)
    qtbot.wait(25000)
    qtbot.mouseClick(gui.procedure.button(QWizard.NextButton),
                     Qt.LeftButton)

    # ONE WIRE PROGRAMMING
    qtbot.wait(45000)
    qtbot.mouseClick(gui.procedure.button(QWizard.NextButton),
                     Qt.LeftButton)

    qtbot.wait(2000)

    # BLE
    qtbot.mouseClick(gui.procedure.cypress_page.ble_btn_pass, Qt.LeftButton)
    gui.procedure.cypress_page.psoc_disconnect_chkbx.click()
    gui.procedure.cypress_page.pwr_cycle_chkbx.click()
    qtbot.mouseClick(gui.procedure.cypress_page.bt_comm_btn_pass,
                     Qt.LeftButton)
    qtbot.wait(3000)

    qtbot.mouseClick(gui.procedure.button(QWizard.NextButton),
                     Qt.LeftButton)

    # XMEGA INTERFACE TESTING
    qtbot.wait(80000)

    qtbot.mouseClick(gui.procedure.button(QWizard.NextButton),
                     Qt.LeftButton)

    qtbot.wait(2000)

    # UART
    gui.procedure.uart_page.uart_pwr_chkbx.click()
    qtbot.wait(3000)
    gui.procedure.uart_page.red_led_chkbx.click()
    qtbot.wait(1000)
    gui.procedure.uart_page.leds_chkbx.click()
    qtbot.wait(2000)

    qtbot.mouseClick(gui.procedure.button(QWizard.NextButton),
                     Qt.LeftButton)

    qtbot.wait(2000)

    # DEEP SLEEP / SOLAR
    gui.procedure.deep_sleep_page.ble_chkbx.click()
    qtbot.keyClicks(gui.procedure.deep_sleep_page.input_i_input, "63")
    gui.procedure.deep_sleep_page.solar_chkbx.click()
    qtbot.wait(1000)
    qtbot.keyClicks(gui.procedure.deep_sleep_page.solar_v_input, "6.0")
    qtbot.keyClicks(gui.procedure.deep_sleep_page.solar_i_input, "53")
    qtbot.wait(1000)
    qtbot.mouseClick(gui.procedure.deep_sleep_page.submit_button,
                     Qt.LeftButton)

    qtbot.wait(2000)
    qtbot.mouseClick(gui.procedure.button(QWizard.NextButton),
                     Qt.LeftButton)

    qtbot.wait(5000)

    qtbot.mouseClick(gui.procedure.button(QWizard.FinishButton), Qt.LeftButton)

    qtbot.wait(3000)

    qtbot.stopForInteraction()

    # Open generated report using randomly generated ID number
    file_list = list(report_dir.glob(f"*ID-{tester_id}.csv"))
    report_values = []
    with open(file_list[0], "r") as f:
        # Headers
        _ = f.readline()
        for line in f:
            report_values.append(line)

    for line in report_values:
        assert(parse_pass(line) == "PASS")

    assert parse_value(report_values[2]) == "D5050076"
    assert parse_value(report_values[3]) == "45321-03"
    assert parse_value(report_values[4]) == tester_id
    assert parse_value(report_values[5]) == "6.0"
    assert parse_value(report_values[6]) == "4.0"
    assert parse_value(report_values[7]) == "2.0"
    assert parse_value(report_values[8]) == "5.0"
    assert parse_value(report_values[11]) == "0.5e"
    assert parse_value(report_values[12]) == "0.5e"
    assert parse_value(report_values[13]) == "1.0d"
    assert parse_value(report_values[14]) == "1.2.0"
    assert parse_value(report_values[16]) == "D5050076"
    assert parse_value(report_values[24]) == "6.0"
    assert parse_value(report_values[25]) == "53.0"
    assert parse_value(report_values[26]) == "63.0"


def parse_value(line):
    values = line.split(",")
    return values[1].strip("\n").strip()


def parse_pass(line):
    values = line.split(",")
    return values[2].strip("\n").strip()
