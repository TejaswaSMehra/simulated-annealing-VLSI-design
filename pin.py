class Pin:
    def __init__(self, gate_name, pin_number, x, y):
        """
        Initialize a pin.
        :param gate_name: Name of the gate the pin belongs to.
        :param pin_number: The index number of the pin (e.g., p1, p2).
        :param x: x-coordinate of the pin (relative to the gate).
        :param y: y-coordinate of the pin (relative to the gate).
        """
        self.gate_name = gate_name
        self.pin_index = pin_number
        self.pin_name = f"{gate_name}p{pin_number}"  # Assign pin name like p1.g1, p2.g1, etc.
        self.output = True if x > 0 else False  # Set as output if x > 0
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Pin({self.pin_name}, {self.x}, {self.y}, Output={self.output})"