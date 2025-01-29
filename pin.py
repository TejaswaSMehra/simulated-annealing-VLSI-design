class Pin:
    def __init__(self, gate_name, pin_number, x, y):
        self.gate_name = gate_name
        self.pin_index = pin_number
        self.pin_name = f"{gate_name}.p{pin_number}"  # Assign pin name like p1.g1, p2.g1, etc.
        self.x = x
        self.y = y