import re


class InvalidLimit(Exception):
    pass


class ValueNotSet(Exception):
    pass


class Model:
    """The model class for storing test limits and other relevant data and 
    checking recorded values against the limits.

    Instance variables:
    limits        --  Test variable ranges and limits.
    tac           --  Tac Ids, lead length and other values.
    internal_5v   --  Internally measured 5 V supply voltage.
    input_v       --  Externally measured supply voltage.

    Instance methods:
    compare_to_limit   --  Compare value against limits and return result.
    """

    def __init__(self):
        self.limits = {
            "v_input_min": 5.0,
            "v_input_max": 7.0,
            "i_input_min": 0.5,
            "i_input_max": 80.0,
            "2v_min": 1.90,
            "2v_max": 2.10,
            "5v_min": 4.85,
            "5v_max": 5.15,
            "5v_uart_tolerance": 0.03,
            "5v_uart_off": 0.35,
            "bat_v_tolerance": 0.10,
            "deep_sleep_min": 30,
            "deep_sleep_max": 85,
            "solar_i_min": 40,
            "solar_v_min": 6,
            "solar_v_max": 7
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
        self.internal_5v = None
        self.input_v = None

    def compare_to_limit(self, limit, value):
        """Compare input value against limit and return the result as a bool."""

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

        elif limit == "solar_i_min":
            return (value >= self.limits["solar_i_min"])

        else:
            raise InvalidLimit
