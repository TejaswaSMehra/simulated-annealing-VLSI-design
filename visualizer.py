import matplotlib.pyplot as plt
import matplotlib.patches as patches

def visualize_circuit(circuit, best_solution, best_cost):
    """
    Visualizes the gates, their positions, pins, and wires.
    """
    fig, ax = plt.subplots()

    # Calculate the bounds for the plot based on gates' positions and dimensions
    min_x = min(gate.x for gate in best_solution.gates.values())
    min_y = min(gate.y for gate in best_solution.gates.values())
    max_x = max(gate.x + gate.width for gate in best_solution.gates.values())
    max_y = max(gate.y + gate.height for gate in best_solution.gates.values())

    ax.set_xlim(min_x - 5, max_x + 5)
    ax.set_ylim(min_y - 5, max_y + 5)

    # Plot each gate as a rectangle
    for gate_name, gate in best_solution.gates.items():
        rect = patches.Rectangle((gate.x, gate.y), gate.width, gate.height,
                                 linewidth=1, edgecolor='black', facecolor='lightblue')
        ax.add_patch(rect)
        ax.text(gate.x + gate.width / 2, gate.y + gate.height / 2,
                gate_name, ha='center', va='center', fontsize=10)

        # Visualize pins if available
        for pin in gate.pins:
            pin_x = gate.x + pin.x  # Absolute x-coordinate of the pin
            pin_y = gate.y + pin.y  # Absolute y-coordinate of the pin
            ax.plot(pin_x, pin_y, 'ro')  # Red circle for pins
            ax.text(pin_x, pin_y, f"{pin.pin_name}", fontsize=8, ha='right')

    # Draw wires
    for net in circuit.nets:
        pin1 = net.pin1
        pin2 = net.pin2
        gate1 = best_solution.gates[pin1.gate_name]
        gate2 = best_solution.gates[pin2.gate_name]

        # Get absolute positions of the pins
        pin1_x = gate1.x + pin1.x
        pin1_y = gate1.y + pin1.y
        pin2_x = gate2.x + pin2.x
        pin2_y = gate2.y + pin2.y

        # Draw a line between the two pins
        ax.plot([pin1_x, pin2_x], [pin1_y, pin2_y], 'g-', linewidth=1)  # Green line for wires

    # Set labels and title
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    plt.title(f"Gate and Pin Placement Visualization (Best Cost: {best_cost})")

    plt.gca().set_aspect('equal', adjustable='box')
    plt.grid(True)
    plt.show()

# Example usage:
# visualize_circuit(circuit, best_solution, best_cost)
