class Net:
    def __init__(self, pin1, pin2):
        """
        Initialize a net connecting two pins.
        :param pin1: Pin object representing the first pin.
        :param pin2: Pin object representing the second pin.
        """
        self.pin1 = pin1
        self.pin2 = pin2

    def wirelength(self, gates):
        """
        Calculate the wirelength (Manhattan distance) between the two pins.
        :param gates: Dictionary of gate names to Gate objects for retrieving pin positions.
        :return: Manhattan distance between the pins.
        """
        gate1 = gates[self.pin1.gate_name]
        gate2 = gates[self.pin2.gate_name]

        pos1 = gate1.get_absolute_pin_positions()[0]  # Assuming pin1 is at index 0 of the pins list
        pos2 = gate2.get_absolute_pin_positions()[1]  # Assuming pin2 is at index 1 of the pins list

        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def __repr__(self):
        return f"Net({self.pin1}, {self.pin2})"