import math
import random
import copy
from circuit import Circuit
from gate import Gate
from net import Net
from pin import Pin
from inputparsing import InputParser
from swapping_annealing import SwappingAnnealing
from visualizer import visualize_circuit
from visualization import visualize_gates
from time import perf_counter

import matplotlib.pyplot as plt  # For plotting the graph
random.seed(0)  # For reproducibility
import sys
sys.setrecursionlimit(10**6)

def output_results(best_solution, wire_cost, output_file="output.txt",formatted_path=None):
    
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
        f.write(f"critical_path {' '.join(formatted_path)}\n")
        f.write(f"critical_path_delay {wire_cost}\n")
        s=''
        for gate_name, gate in best_solution.gates.items():
            adjusted_x = gate.x - min_x  # Adjust x position
            adjusted_y = gate.y - min_y  # Adjust y position
            s+=(f"{gate_name} {adjusted_x} {adjusted_y}\n")
        s.strip('\n')
        f.write(s)
        # Output total wire length (semi-perimeter cost)



def plot_time_vs_gates(num_gates, sa_times, nlogn_times):
    plt.figure(figsize=(10, 6))
    
    # Plot the actual time taken for simulated annealing
    plt.plot(num_gates, sa_times, marker='o', linestyle='-', color='b', label="Simulated Annealing Time (s)")
    
    # Plot the O(2 * 10^6 + n log n) curve for the benchmark
    plt.plot(num_gates, nlogn_times, marker='x', linestyle='--', color='r', label="O(2 * 10^6*n + n log n) Time (s)")
    
    plt.title('Number of Gates vs. Time Taken for Simulated Annealing and O(2 * 10^6 + n log n)')
    plt.xlabel('Number of Gates')
    plt.ylabel('Time Taken (seconds)')
    plt.grid(True)
    plt.legend()
    plt.show()



if __name__ == "__main__":
    input_file = "input.txt"
    parser = InputParser(input_file)
    parser.parse()
    circuit = parser.get_circuit()

    # Initialize gates far from each other
    spacing = 10  # Adjust the spacing as needed
    for i, gate in enumerate(circuit.gates.values()):
        gate.x, gate.y = (i * spacing, i * spacing)  # Spread out gates diagonally
    
    # Step 2: Run simulated annealing
    start = perf_counter()
    sa = SwappingAnnealing(circuit, initial_temperature=10*8, cooling_rate=0.9999, max_iterations=1000000)
    best_solution, best_cost = sa.run()
    
    end = perf_counter()
    wire_cost,inp,out = best_solution.cost_function()
    # Step 3: Output results in the required format
    formatted_path,delay = circuit.path_finder(inp, out)
    output_results(best_solution, wire_cost, output_file="output.txt",formatted_path=formatted_path)
    print("Execution time:", end - start, "seconds")
    
    # wire_cost,inp,out = circuit.read_gate_positions_and_calculate_delay("output.txt")
    

    # Print the result
    print(f"Critical path delay: {wire_cost} ns")
    print(f"Primary input gate: {inp}")
    print(f"Primary output gate: {out}")



    visualize_circuit(circuit, best_solution, wire_cost)
 