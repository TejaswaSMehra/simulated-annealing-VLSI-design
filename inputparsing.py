from circuit import Circuit
from gate import Gate
from net import Net
from pin import Pin

class InputParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.circuit = Circuit()  # Initialize an empty circuit
        self.gate_definitions = {}  # To hold gate definitions temporarily

    def parse(self):
        """
        Parse the input file and initialize gates and nets in the circuit.
        """
        with open(self.file_path, 'r') as file:
            lines = file.readlines()

        index = 0
        while index < len(lines):
            line = lines[index].strip()

            if line.startswith("g"):  # Process gate information
                parts = line.split()
                gate_name = parts[0]  # e.g., "g1"
                width = int(parts[1])  # Gate width
                height = int(parts[2])  # Gate height
                self.gate_definitions[gate_name] = (width, height)
                index += 1

            elif line.startswith("pins"):  # Process pin information
                pin_parts = line.split()
                gate_name = pin_parts[1]

                if gate_name not in self.gate_definitions:
                    raise ValueError(f"Gate '{gate_name}' not defined before its pins.")

                width, height = self.gate_definitions[gate_name]
                pins = []

                for i in range(2, len(pin_parts), 2):
                    x = int(pin_parts[i])
                    y = int(pin_parts[i + 1])
                    pin_number = i // 2  # Pin numbering starts from 1
                    pins.append(Pin(gate_name, pin_number, x, y))

                gate = Gate(gate_name, width, height, pins)
                gate.set_position(0, 0)  # Initial position (adjust as needed)
                self.circuit.add_gate(gate)

                index += 1

            elif line.startswith("wire"):  # Process wire information
                parts = line.split()
                pin1_gate, pin1_pin = parts[1].split(".")
                pin2_gate, pin2_pin = parts[2].split(".")

                pin1 = self.find_pin(pin1_gate, int(pin1_pin[1:]) - 1)  # p1 -> index 0
                pin2 = self.find_pin(pin2_gate, int(pin2_pin[1:]) - 1)

                net = Net(pin1, pin2)
                self.circuit.add_net(net)

                index += 1

            elif not line:
                index += 1

    def find_pin(self, gate_name, pin_index):
        """
        Find a pin object by gate name and pin index.
        """
        return self.circuit.gates[gate_name].pins[pin_index]

    def get_circuit(self):
        """
        Return the parsed circuit.
        """
        return self.circuit
