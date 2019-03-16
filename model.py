import re


class InvalidLimit(Exception):
    pass


class ValueNotSet(Exception):
    pass


class Model:
    def __init__(self):
        self.limits = {
            "v_input_min": 5.0,
            "v_input_max": 7.0,
            "i_input_min": 0,
            "i_input_max": 6.0,
            "2v_min": 1.90,
            "2v_max": 2.10,
            "5v_min": 4.85,
            "5v_max": 5.15,
            "5v_uart_tolerance": 0.02,
            "5v_uart_off": 0.3,
            "bat_v_tolerance": 0.10,
            "deep_sleep_min": 30,
            "deep_sleep_max": 70,
            "solar_i": 40,
            "solar_v_min": 5,
            "solar_v_max": 8
        }
        self.tac = {
            "tac1": None,
            "tac2": None,
            "tac3": None,
            "tac4": None,
            "lead": 80,
            "1": 0.000,
            "2": 0.250,
            "3": 0.500
        }
        self.ser_port = None
        self.internal_5v = None
        self.input_v = None

    def snow_depth(self, s):
        p = r"([0-9]){1,4}(\scm)"
        if re.match(p, s):
            return True
        else:
            return False

    def set_tac_id(self, tac_num, tac_id):
        self.tac[tac_num] = tac_id

    def set_serial_port(self, port):
        self.ser_port = port

    def compare_to_limit(self, limit, value):
        if limit == "input_v":
            self.input_v = value
            return (value >= self.limits["v_input_min"] and
                    value <= self.limits["v_input_max"])

        elif limit == "input_i":
            return (value >= self.limits["i_input_min"] and
                    value < self.limits["i_input_max"])

        elif limit == "supply_2v":
            return (value >= self.limits["2v_min"] and
                    value <= self.limits["2v_max"])

        elif limit == "supply_5v":
            self.internal_5v = value
            if (value >= self.limits["5v_min"] and
                    value <= self.limits["5v_max"]):
                return True
            else:
                return False

        elif limit == "uart_5v":
            if (self.internal_5v):
                tolerance = self.limits["5v_uart_tolerance"]
                max_v = (1 + tolerance) * self.internal_5v
                min_v = (1 - tolerance) * self.internal_5v
                return (value < max_v and value > min_v)
            else:
                raise ValueNotSet

        elif limit == "off_5v":
            return (value < self.limits["5v_uart_off"])

        elif limit == "bat_v":
            if (self.input_v):
                tolerance = self.limits["bat_v_tolerance"]
                max_v = (1 + tolerance) * self.input_v
                min_v = (1 - tolerance) * self.input_v
                return (value <= max_v and value >= min_v)
            else:
                raise ValueNotSet

        elif limit == "deep_sleep_i":
            return (value >= self.limits["deep_sleep_min"] and
                    value <= self.limits["deep_sleep_max"])

        elif limit == "solar_v":
            return (value >= self.limits["solar_v_min"] and
                    value <= self.limits["solar_v_max"])

        elif limit == "solar_i":
            return (value >= self.limits["solar_i"])

        else:
            raise InvalidLimit
