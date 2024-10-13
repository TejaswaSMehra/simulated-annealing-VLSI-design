import math
import random
import copy
from circuit import Circuit

class SimulatedAnnealing:
    def __init__(self, circuit, initial_temperature=10**8, cooling_rate=0.999, max_iterations=10**6):
        self.circuit = circuit
        self.initial_temperature = initial_temperature
        self.cooling_rate = cooling_rate
        self.max_iterations = max_iterations

        # Calculate bounding box from the circuit object
        self.bounding_box = self.calculate_bounding_box()

    def calculate_bounding_box(self):
        """
        Calculate the bounding box based on the positions and dimensions of all gates.
        :return: A tuple (min_x, min_y, max_x, max_y)
        """
        sum_x = 0
        sum_y = 0
        for gate in self.circuit.gates.values():
            sum_x += gate.width
            sum_y += gate.height
        return (0, 0, sum_x, sum_y)

    def run(self):
        """
        Runs the simulated annealing algorithm to minimize the wire cost.
        """
        current_solution = copy.deepcopy(self.circuit)
        current_cost = current_solution.total_wire_cost()
        best_solution = copy.deepcopy(current_solution)
        best_cost = current_cost
        temperature = self.initial_temperature
        print("here")
        for i in range(self.max_iterations):
            # Generate a neighboring solution by perturbing the current solution
            neighbor_solution = self.perturb(current_solution)
            if neighbor_solution is None:
                continue  # Skip this iteration if no valid neighbor was found
            neighbor_cost = neighbor_solution.total_wire_cost()

            # Calculate the cost difference
            cost_difference = neighbor_cost - current_cost

            # Accept the new solution if it's better or with a probability if worse
            if cost_difference < 0 or random.uniform(0, 1) < math.exp(-cost_difference / temperature):
                current_solution = neighbor_solution
                current_cost = neighbor_cost

                if neighbor_cost < best_cost:
                    best_solution = copy.deepcopy(neighbor_solution)
                    best_cost = neighbor_cost

            # Cool down the temperature
            temperature *= self.cooling_rate

            # Print the progress for debugging
            # if (i % 10 == 0):
            print(f"Iteration {i}: Current Cost = {current_cost}, Best Cost = {best_cost}")

            # Stop if temperature is sufficiently low
            if temperature < 1e-6:
                break

        return best_solution, best_cost

    def perturb(self, circuit):
        """
        Generate a neighboring solution by randomly moving gates within a bounding box,
        ensuring no overlap.
        """
        new_circuit = copy.deepcopy(circuit)

        # Select a random gate to move
        gate_names = list(new_circuit.gates.keys())
        selected_gate_name = random.choice(gate_names)
        selected_gate = new_circuit.gates[selected_gate_name]

        # Get bounding box limits
        min_x, min_y, max_x, max_y = self.bounding_box

        # Move the selected gate to a new random position within the bounding box
        for _ in range(100):  # Limit attempts to avoid infinite loops
            new_x = random.randint(min_x, max_x - selected_gate.width)
            new_y = random.randint(min_y, max_y - selected_gate.height)

            # Set the new position
            selected_gate.set_position(new_x, new_y)

            # Check for overlaps with other gates
            if not self.check_overlap(new_circuit):
                return new_circuit  # Return valid neighboring solution

        return None  # Return None if no valid perturbation was found

    def check_overlap(self, circuit):
        """
        Check for overlaps between gates in the circuit.
        :param circuit: Circuit object to check for overlaps.
        :return: True if there is an overlap, False otherwise.
        """
        for gate1 in circuit.gates.values():
            for gate2 in circuit.gates.values():
                if gate1.name != gate2.name:  # Compare different gates
                    if (gate1.x < gate2.x + gate2.width and
                        gate1.x + gate1.width > gate2.x and
                        gate1.y < gate2.y + gate2.height and
                        gate1.y + gate1.height > gate2.y):
                        return True  # Overlap detected
        return False