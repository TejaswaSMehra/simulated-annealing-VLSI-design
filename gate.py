from pin import Pin

class Gate:
    def __init__(self, name, width, height, pins, delay):
        self.name = name
        self.width = width
        self.height = height
        self.pins = pins  # A list of Pin objects
        self.x = None  # x-coordinate of the gate's bottom-left corner
        self.y = None  # y-coordinate of the gate's bottom-left corner
        self.gate_delay = delay
        
    def get_absolute_pin_positions(self):
        """
        Get the absolute positions of the pins after the gate is placed.
        :return: A list of (x, y) tuples representing absolute pin positions.
        """
        return [(self.x + pin.x, self.y + pin.y) for pin in self.pins]