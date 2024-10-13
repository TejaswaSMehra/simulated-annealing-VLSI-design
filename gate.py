from pin import Pin

class Gate:
    def __init__(self, name, width, height, pins):
        """
        Initialize a gate.
        :param name: Name of the gate.
        :param width: Width of the gate.
        :param height: Height of the gate.
        :param pins: List of Pin objects representing the pins on the gate.
        """
        self.name = name
        self.width = width
        self.height = height
        self.pins = pins  # A list of Pin objects
        self.x = None  # x-coordinate of the gate's bottom-left corner
        self.y = None  # y-coordinate of the gate's bottom-left corner

    def set_position(self, x, y):
        """
        Set the position of the gate's bottom-left corner.
        :param x: x-coordinate
        :param y: y-coordinate
        """
        self.x = x
        self.y = y

    def get_absolute_pin_positions(self):
        """
        Get the absolute positions of the pins after the gate is placed.
        :return: A list of (x, y) tuples representing absolute pin positions.
        """
        return [(self.x + pin.x, self.y + pin.y) for pin in self.pins]

    def __repr__(self):
        return f"Gate({self.name}, {self.width}, {self.height}, Pins={self.pins})"