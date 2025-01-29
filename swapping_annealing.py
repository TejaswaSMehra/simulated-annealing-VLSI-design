import math
import random
import copy
from circuit import Circuit
from time import perf_counter

class SwappingAnnealing:
    def __init__(self, circuit, initial_temperature=10**8, cooling_rate=0.999, max_iterations=1000):
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
        self.best_cost = self.circuit.cost_function()[0]

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
        new_cost = self.circuit.cost_function()[0]
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
        current_cost = self.circuit.cost_function()[0]
        start_time = perf_counter()
        for i in range(self.max_iterations):
            elapsed_time = perf_counter() - start_time  # Calculate elapsed time
        
            if elapsed_time > 900:  # If more than 900 seconds have passed, terminate
               print(f"Terminating after {elapsed_time:.2f} seconds.")
               break
            
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
                print(f"Iteration {i}: Current Cost = {current_cost} , Elapsed Time (Annealing) = {elapsed_time:.2f} seconds")
            
            # Cool down the system
            temperature *= self.cooling_rate

        # Deep copy the circuit to preserve the original state
        vertical_copy = copy.deepcopy(self.circuit)
        horizontal_copy = copy.deepcopy(self.circuit)
        self.best_solution = self.circuit
        # Try vertical packing on the deep copy
        pack_gates_vertically(vertical_copy)
        vertical_cost = vertical_copy.cost_function()[0]

        # Try horizontal packing on another deep copy
        pack_gates_horizontally(horizontal_copy)
        horizontal_cost = horizontal_copy.cost_function()[0]

        # Choose the packing strategy with the lowest cost
        if vertical_cost < self.best_cost:
            # print("Choosing vertical packing with cost:", vertical_cost)
            print("CHOOSING VERTICAL")
            self.best_solution = vertical_copy
            self.best_cost = vertical_cost
        elif horizontal_cost < self.best_cost:
            # print("Choosing horizontal packing with cost:", horizontal_cost)
            print("CHOOSING HORIZONTAL")
            self.best_solution = horizontal_copy
            self.best_cost = horizontal_cost
        
    
        return self.best_solution, self.best_cost

def pack_gates_horizontally(circuit):
    """
    Align gates horizontally within their respective rows in the given circuit.
    Ensures no horizontal gaps between gates.
    """
    sorted_gates = sorted(circuit.gates.values(), key=lambda gate: gate.y)

    current_row = []
    current_y = None
    set_y = 0
    for gate in sorted_gates:
        if current_y is None or current_y != gate.y:
            if current_row:
                align_gates_in_row(current_row, set_y)
                set_y = max((gate.y+gate.height) for gate in current_row)

            current_row = [gate]
            current_y = gate.y
        else:
            current_row.append(gate)
    
    if current_row:
        align_gates_in_row(current_row, set_y)

def align_gates_in_row(row_gates, set_y):
    """
    Align gates in a single row, starting from the left and packing horizontally.
    """
    current_x = 0 
    for gate in row_gates:
        gate.x = current_x
        gate.y = set_y
        current_x += gate.width

def pack_gates_vertically(circuit):
    """
    Align gates vertically within their respective columns in the given circuit.
    Ensures no vertical gaps between gates.
    """
    sorted_gates = sorted(circuit.gates.values(), key=lambda gate: gate.x) 

    current_column = []
    current_x = None
    set_x = 0
    for gate in sorted_gates:
        if current_x is None or current_x != gate.x:
            if current_column:
                align_gates_in_column(current_column, set_x)
                set_x = max((gate.x+gate.width) for gate in current_column)

            current_column = [gate]
            current_x = gate.x
        else:
            current_column.append(gate)
    
    if current_column:
        align_gates_in_column(current_column, set_x)

def align_gates_in_column(column_gates, set_x):
    """
    Align gates in a single column, starting from the bottom and packing vertically.
    """
    current_y = 0
    for gate in column_gates:
        gate.y = current_y
        gate.x = set_x
        current_y += gate.height

