import math
import random
import copy
from circuit import Circuit
from gate import Gate
from net import Net
from pin import Pin
from inputparsing import InputParser
from simulated_annealing import SimulatedAnnealing
from simulated_annealing2 import SimulatedAnnealing2
from visualizer import visualize_circuit
from visualization import visualize_gates
import time
random.seed(0)  # For reproducibility
import sys
sys.setrecursionlimit(10**6)

def output_results(circuit, best_solution, best_cost, output_file="output.txt"):
    # Calculate bounding box for the entire circuit
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')

    for gate in best_solution.gates.values():
        min_x = min(min_x, gate.x)
        min_y = min(min_y, gate.y)
        max_x = max(max_x, gate.x + gate.width)
        max_y = max(max_y, gate.y + gate.height)

    bounding_box_width = max_x - min_x
    bounding_box_height = max_y - min_y

    with open(output_file, 'w') as f:
        # Output bounding box dimensions
        f.write(f"bounding_box {bounding_box_width} {bounding_box_height}\n")

        # Adjust gate positions to set the bottom-left corner to (0, 0)
        print(min_x, min_y)
        s=''
        for gate_name, gate in best_solution.gates.items():
            adjusted_x = gate.x - min_x  # Adjust x position
            adjusted_y = gate.y - min_y  # Adjust y position
            s+=(f"{gate_name} {adjusted_x} {adjusted_y}\n")
        s.strip('\n')
        f.write(s)
        # Output total wire length (semi-perimeter cost)
        f.write(f"wire_length {best_cost}\n")

if __name__ == "__main__":
    # Step 1: Parse input
    input_file = "input.txt"  # Example input file path
    parser = InputParser(input_file)
    parser.parse()
    circuit = parser.get_circuit()

    # Initialize gates far from each other
    spacing = 10  # Adjust the spacing as needed
    for i, gate in enumerate(circuit.gates.values()):
        gate.set_position(i * spacing, i * spacing)  # Spread out gates diagonally

    # Step 2: Run simulated annealing
    if len(circuit.gates) < 0:
        start = time.perf_counter()
        sa = SimulatedAnnealing(circuit)
        best_solution, best_cost = sa.run()
        end = time.perf_counter()
        wire_cost = best_solution.total_wire_cost()
        # Step 3: Output results in the required format
        output_results(circuit, best_solution, best_cost, output_file="output.txt")
        print("Execution time:", end - start, "seconds")
        print("Total wire cost: ", wire_cost)
        visualize_circuit(circuit, best_solution, best_cost)
        # visualize_gates("output.txt", input_file, (10, 10))
        # visualize_gates(input_file, "output.txt", (100, 100))  # Visualize the output
    else:
        # Step 2: Run simulated annealing
        start = time.perf_counter()
        sa = SimulatedAnnealing2(circuit, initial_temperature=100_000, cooling_rate=0.999, max_iterations=100_000)
        best_solution, best_cost = sa.run()
        end = time.perf_counter()
        wire_cost = best_solution.total_wire_cost()
        # Step 3: Output results in the required format
        output_results(circuit, best_solution, best_cost, output_file="output.txt")
        print("Execution time:", end - start, "seconds")
        print("Total wire cost: ", wire_cost)
        # visualize_circuit(circuit, best_solution, best_cost)
        # visualize_gates("output.txt", input_file, (10, 10))
        # visualize_gates(input_file, "output.txt", (100, 100))  # Visualize the output