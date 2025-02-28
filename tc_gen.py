import random

# Generate gates with random dimensions and pin coordinates
def generate_gates(num_gates, max_width, max_height, max_pins_per_gate):
    gates = []
    
    for i in range(1, num_gates + 1):
        # Generate random width and height for the gate
        width = random.randint(1, max_width)
        height = random.randint(1, max_height)
        delay = random.randint(1, 100)
        # Ensure at least 2 pins, and pins should be on the sides (relative to width/height)
        num_pins = random.randint(2, max_pins_per_gate)
        pins = []

        # Generate random pins, pins will be located on the sides (relative coordinates)
        for j in range(num_pins):
            side = random.choice(['left', 'right'])
            if side == 'left':
                # Pin on the left side (x=0), random y-coordinate
                pins.append((0, random.randint(0, height)))
            else:
                # Pin on the right side (x=width), random y-coordinate
                pins.append((width, random.randint(0, height)))

        gates.append((i, width, height, pins, delay))
    
    return gates

# Generate wire connections between gates
def generate_connections(gates, num_wires):
    connections = []
    num_gates = len(gates)
    
    # Ensure at least 1 wire per gate
    for gate in gates:
        g1 = gate[0]
        if g1==num_gates:
            continue
        g2 = random.randint(g1+1, num_gates)
        if g1 != g2:
            p1 = random.randint(0, len(gate[3]) - 1)  # Random pin on gate 1
            while gate[3][p1][0] == 0:
                p1 = random.randint(0, len(gate[3]) - 1)
            g2_pins = next(g[3] for g in gates if g[0] == g2)
            p2 = random.randint(0, len(g2_pins) - 1)  # Random pin on gate 2
            while g2_pins[p2][0] != 0:
                p2 = random.randint(0, len(g2_pins) - 1)
            connections.append((g1, p1, g2, p2))
    
    # Additional random wires
    for _ in range(0,num_wires - num_gates):  # Already ensured 1 wire per gate
        g1 = random.randint(1, num_gates-1)
        g2 = random.randint(g1+1, num_gates)
        if g1 != g2:
            p1 = random.randint(0, len(next(g[3] for g in gates if g[0] == g1)) - 1)
            p2 = random.randint(0, len(next(g[3] for g in gates if g[0] == g2)) - 1)
            connections.append((g1, p1, g2, p2))

    return connections

# Generate the test case file in the specified format
def generate_test_case_file(num_gates, max_width, max_height, max_pins_per_gate, max_wires, output_file):
    gates = generate_gates(num_gates, max_width, max_height, max_pins_per_gate)
    connections = generate_connections(gates, max_wires)

    with open(output_file, 'w') as f:
        # Write gates with their pins
        for gate in gates:
            f.write(f"g{gate[0]} {gate[1]} {gate[2]} {gate[4]}\n")
            f.write(f"pins g{gate[0]} " + ' '.join(f"{p[0]} {p[1]}" for p in gate[3]) + '\n')

        # Write wire connections
        wire_delay = random.randint(1, 100)
        f.write(f"wire_delay {wire_delay}\n")
        for conn in connections:
            f.write(f"wire g{conn[0]}.p{conn[1] + 1} g{conn[2]}.p{conn[3] + 1}\n")

# Configuration for the test case
if __name__ == "__main__":
    num_gates = 10
    max_width = 100  # Maximum width of each gate
    max_height = 100  # Maximum height of each gate
    max_pins_per_gate = 40  # Maximum number of pins per gate
    max_wires = 50  # Maximum number of wire connection s (as total pins ≤ 40,000)
    output_file = 'input.txt'

    # Generate the test case and save it to a file
    generate_test_case_file(num_gates, max_width, max_height, max_pins_per_gate, max_wires, output_file)

    print(f"Test case with {num_gates} gates has been generated and saved to {output_file}")

