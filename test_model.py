import model

m = model.Model()

tac_ids = {
    "tac1": "aaa1 1234 bbbb 5c6d 7e8f",
    "tac2": "aaa2 1234 bbbb 5c6d 7e8f",
    "tac3": "aaa3 1234 bbbb 5c6d 7e8f",
    "tac4": "aaa4 1234 bbbb 5c6d 7e8f",
}

good_vi_values = {
    "v_input": 6.0,
    "i_input": 4.0,
    "2v": 2.00,
    "5v": 5.05,
    "5v_internal": 5.04,
    "5v_uart_off": 0.1
}

bad_vi_values = {
    "v_input": 4.0,
    "i_input": 6.0,
    "2v": 2.11,
    "5v": 4.89,
    "5v_uart_off": 0.34
}


def test_snow_depth():
    assert m.snow_depth("21 cm")
    assert m.snow_depth("0004 cm")
    assert m.snow_depth("07 cm")
    assert not m.snow_depth("07")
    assert not m.snow_depth("999999 cm")


def test_tac_ids():
    for tac_num, tac_id in tac_ids.items():
        m.set_tac_id(tac_num, tac_id)
        assert m.tac[tac_num] == tac_id


def test_limits():
    for key, value in good_vi_values.items():
        assert m.compare_to_limit(key, value)

    for key, value in bad_vi_values.items():
        assert not m.compare_to_limit(key, value)
