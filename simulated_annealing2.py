import math
import random
import copy
from circuit import Circuit
import time

class SimulatedAnnealing2:
    def __init__(self, circuit, initial_temperature=1000, cooling_rate=0.99, max_iterations=1000):
        self.circuit = circuit  # Circuit object with gates and nets
        self.initial_temperature = initial_temperature
        self.cooling_rate = cooling_rate
        self.min_temperature = 1e-6
        self.max_iterations = max_iterations
        
        # Initialize envelope dimensions (based on largest gate dimensions)
        self.max_width = max(gate.width for gate in self.circuit.gates.values())
        self.max_height = max(gate.height for gate in self.circuit.gates.values())

        # Initialize gate positions within the grid
        self.gate_positions = self.initialize_gate_positions()

        # Store the origin of each gate's envelope
        self.envelope_origins = self.initialize_envelope_origins()

        # Connections (nets) between gates
        self.connections = self.circuit.nets

        # Track the best solution
        self.best_solution = copy.deepcopy(self.gate_positions)
        self.best_cost = self.circuit.total_wire_cost()

    def initialize_gate_positions(self):
        """Initialize the gate positions in a grid based on max_width and max_height."""
        grid_size = int(math.ceil(math.sqrt(len(self.circuit.gates))))
        gate_positions = {}
        
        # Assign initial positions to gates in a grid layout
        for idx, gate in enumerate(self.circuit.gates.values()):
            row = idx // grid_size
            col = idx % grid_size
            gate_positions[gate] = (col * self.max_width, row * self.max_height)
            gate.x = col * self.max_width
            gate.y = row * self.max_height
        
        return gate_positions

    def initialize_envelope_origins(self):
        """Store the origin for each gate's envelope."""
        origins = {}
        for idx, gate in enumerate(self.circuit.gates.values()):
            grid_size = int(math.ceil(math.sqrt(len(self.circuit.gates))))
            row = idx // grid_size
            col = idx % grid_size
            origins[gate] = (col * self.max_width, row * self.max_height)
        return origins

    def is_accepted(self, current_cost, new_cost, temperature):
        """Check if the new solution is accepted."""
        if new_cost < current_cost:
            return True
        delta_cost = new_cost - current_cost
        probability = math.exp(-delta_cost / temperature)
        return random.random() <= probability

    def swap_gates(self, temperature, current_cost):
        """Randomly swap the positions of two gates."""
        gate1, gate2 = random.sample(list(self.circuit.gates.values()), 2)

        original_position1 = (gate1.x, gate1.y)
        original_position2 = (gate2.x, gate2.y)
        
        # Swap their positions in the gate_positions map
        # Swap the envelope origins as well
        self.envelope_origins[gate1], self.envelope_origins[gate2] = self.envelope_origins[gate2], self.envelope_origins[gate1]
        self.gate_positions[gate1], self.gate_positions[gate2] = self.envelope_origins[gate2], self.envelope_origins[gate1]
        gate1.x, gate1.y = self.envelope_origins[gate1]  # Reset position to envelope origin
        gate2.x, gate2.y = self.envelope_origins[gate2]  # Reset position to envelope origin


        # Recalculate the cost after swapping
        new_cost = self.circuit.total_wire_cost()
        # If the swap is not accepted, revert the swap
        if not self.is_accepted(current_cost, new_cost, temperature):
            self.envelope_origins[gate1], self.envelope_origins[gate2] = self.envelope_origins[gate2], self.envelope_origins[gate1]
            self.gate_positions[gate1], self.gate_positions[gate2] = original_position1, original_position2
            gate1.x, gate1.y = original_position1  # Revert in the circuit as well
            gate2.x, gate2.y = original_position2
            return current_cost

        return new_cost


    def run(self):
        """Run the simulated annealing algorithm."""
        temperature = self.initial_temperature
        current_cost = self.circuit.total_wire_cost()

        for i in range(self.max_iterations):
            if temperature < self.min_temperature:
                break

            # Swap gates
            current_cost = self.swap_gates(temperature, current_cost)
            
            # Track the best solution
            if current_cost < self.best_cost:
                self.best_cost = current_cost
                self.best_solution = copy.deepcopy(self.gate_positions)

            # Print the progress for debugging
            if (i % 10 == 0):
                print(f"Iteration {i}: Current Cost = {current_cost}")
            
            # Cool down the system
            temperature *= self.cooling_rate

        # Deep copy the circuit to preserve the original state
        vertical_copy = copy.deepcopy(self.circuit)
        horizontal_copy = copy.deepcopy(self.circuit)

        # Try vertical packing on the deep copy
        pack_gates_vertically(vertical_copy)
        vertical_cost = vertical_copy.total_wire_cost()

        # Try horizontal packing on another deep copy
        pack_gates_horizontally(horizontal_copy)
        horizontal_cost = horizontal_copy.total_wire_cost()

        # Choose the packing strategy with the lowest cost
        if vertical_cost < horizontal_cost:
            print("Choosing vertical packing with cost:", vertical_cost)
            self.best_solution = vertical_copy
            self.best_cost = vertical_cost
        else:
            print("Choosing horizontal packing with cost:", horizontal_cost)
            self.best_solution = horizontal_copy
            self.best_cost = horizontal_cost

        return self.best_solution, self.best_cost

def pack_gates_horizontally(circuit):
    """
    Align gates horizontally within their respective rows in the given circuit.
    Ensures no horizontal gaps between gates.
    """
    # Sort the gates by their y-coordinate to group them into rows
    sorted_gates = sorted(circuit.gates.values(), key=lambda gate: gate.y)  # Sort by y-position

    current_row = []
    current_y = None

    # Process each gate and align horizontally
    for gate in sorted_gates:
        if current_y is None or current_y != gate.y:
            # Process the current row if it's not empty
            if current_row:
                align_gates_in_row(current_row)

            # Start a new row
            current_row = [gate]
            current_y = gate.y
        else:
            # Continue adding gates to the current row
            current_row.append(gate)
    
    # Align the last row
    if current_row:
        align_gates_in_row(current_row)

def align_gates_in_row(row_gates):
    """
    Align gates in a single row, starting from the left and packing horizontally.
    """
    current_x = 0  # Start stacking from the left (x = 0)

    for gate in row_gates:
        # Place the gate at the current_x and update its position
        gate.x = current_x
        current_x += gate.width

def pack_gates_vertically(circuit):
    """
    Align gates vertically within their respective columns in the given circuit.
    Ensures no vertical gaps between gates.
    """
    # Sort the gates by their x-coordinate to group them into columns
    sorted_gates = sorted(circuit.gates.values(), key=lambda gate: gate.x)  # Sort by x-position

    current_column = []
    current_x = None

    # Process each gate and align vertically
    for gate in sorted_gates:
        if current_x is None or current_x != gate.x:
            # Process the current column if it's not empty
            if current_column:
                align_gates_in_column(current_column)

            # Start a new column
            current_column = [gate]
            current_x = gate.x
        else:
            # Continue adding gates to the current column
            current_column.append(gate)
    
    # Align the last column
    if current_column:
        align_gates_in_column(current_column)

def align_gates_in_column(column_gates):
    """
    Align gates in a single column, starting from the bottom and packing vertically.
    """
    current_y = 0  # Start stacking from the bottom (y = 0)

    for gate in column_gates:
        # Place the gate at the current_y and update its position
        gate.y = current_y
        current_y += gate.height

