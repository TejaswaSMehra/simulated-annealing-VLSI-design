class deque:
    def __init__(self, iterable=None):
        self.stack1 = list(iterable)  # Stack for enqueue operations
        self.stack2 = []  # Stack for dequeue operations

    def append(self, item):
        # Push the item onto stack1 (enqueue is always done here)
        self.stack1.append(item)

    def popleft(self):
        # If stack2 is empty, transfer all items from stack1 to stack2
        if not self.stack2:
            while self.stack1:
                self.stack2.append(self.stack1.pop())  # Move items from stack1 to stack2
        
        # If stack2 is still empty, the queue is empty
        if not self.stack2:
            raise IndexError("Dequeue from an empty queue.")

        # Pop the item from stack2 (this simulates the front of the queue)
        return self.stack2.pop()

    def is_empty(self):
        # The queue is empty only if both stacks are empty
        return not self.stack1 and not self.stack2


class Circuit:
    def __init__(self):
        self.gates = {}
        self.nets = []
        self.pin_lookup = {}  # Dictionary to map pin names to pins
        self.connected_components = None
        self.a_to_bs = {}  # Dictionary to map each "a" to its "b"s
        self.pin_to_output_delay = {}  # Dictionary to map each "a" to its "b"s
        self.made_to_list = False
        self.wire_delay = 0

    def add_gate(self, gate):
        self.gates[gate.name] = gate
        for pin in gate.pins:
            pin_name = f"{gate.name}.p{pin.pin_index}"
            self.pin_lookup[pin_name] = pin

    def add_net(self, net):
        self.nets.append(net)
        # Ensure "a" to "b" mapping for wire cost function
        a_pin_name = net.pin1.pin_name
        if a_pin_name not in self.a_to_bs:
            self.a_to_bs[a_pin_name] = {net.pin1}
        self.a_to_bs[a_pin_name].add(net.pin2)

    def bounding_box(self, component):
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        for pin in component:
            gate = self.gates[pin.gate_name]
            absolute_x = gate.x + pin.x
            absolute_y = gate.y + pin.y
            min_x = min(min_x, absolute_x)
            min_y = min(min_y, absolute_y)
            max_x = max(max_x, absolute_x)
            max_y = max(max_y, absolute_y)
        return min_x, min_y, max_x, max_y

    def semi_perimeter(self, bounding_box):
        min_x, min_y, max_x, max_y = bounding_box
        width = max_x - min_x
        height = max_y - min_y
        return width + height
    
    def calculate_wire_delay(self, output_pin):
        wire_delay_cost = 0
        if not self.made_to_list:
            for a_pin, b_pins in self.a_to_bs.items():
                # Calculate bounding box of a and its corresponding b's
                self.a_to_bs[a_pin] = tuple(b_pins)
            self.made_to_list = True

        b_pins = self.a_to_bs[output_pin]
        bounding_box = self.bounding_box(b_pins)
        wire_delay_cost += self.semi_perimeter(bounding_box)
        wire_delay_cost *= self.wire_delay
        self.pin_to_output_delay[output_pin] = wire_delay_cost+self.gates[output_pin.split('.')[0]].gate_delay
        return wire_delay_cost


    def cost_function(self):        
        # Step 1: Build the graph representation
        self.connections_of_gate = dict()  # Initialize graph
        in_degree = {gate_name: 0 for gate_name in self.gates}  # Initialize in-degrees
        previous_gate = {gate_name: None for gate_name in self.gates}  # Track the previous gate for longest path

        for a in self.a_to_bs:
            self.calculate_wire_delay(a)

        # Build the graph from nets and calculate edge weights
        for net in self.nets:
            if net.pin1.gate_name not in self.connections_of_gate:
                self.connections_of_gate[net.pin1.gate_name] = []
            self.connections_of_gate[net.pin1.gate_name].append(net)
            in_degree[net.pin2.gate_name] += 1  # Increment in-degree for b_gate

        # Step 2: Topological sorting using Kahn's algorithm
        queue = deque([gate_name for gate_name in self.gates if in_degree[gate_name] == 0])
        primary_input_gates = [gate_name for gate_name in self.gates if in_degree[gate_name] == 0]
        gates_ordered = []

        while queue.is_empty() == False:
            current_gate = queue.popleft()
            gates_ordered.append(current_gate)
            if current_gate not in self.connections_of_gate:
                self.connections_of_gate[current_gate] = []
            for net in self.connections_of_gate[current_gate]:
                connected_pin = net.pin2
                in_degree[connected_pin.gate_name] -= 1
                if in_degree[connected_pin.gate_name] == 0:
                    queue.append(connected_pin.gate_name)

        # Step 3: Initialize distances for longest path calculation
        distances = {gate_name: float('-inf') for gate_name in self.gates}
        # Track the primary input gate for the longest path
        primary_input_gate_for_longest_path = None

        # Initialize distances from all primary input gates
        for gate_name in primary_input_gates:
            distances[gate_name] = 0  # Start distance at 0 for primary inputs

        if len(self.gates) != len(gates_ordered):
            raise Exception("Loop found.")
        
        # Step 4: Relax edges to find the longest path
        for u in gates_ordered:
            if distances[u] != float('-inf'):  # Only consider reachable nodes
                if u not in self.connections_of_gate:
                    self.connections_of_gate[u] = []
                for net in self.connections_of_gate[u]:
                    v = net.pin2.gate_name
                    weight = self.pin_to_output_delay[net.pin1.pin_name]
                    if distances[v] < distances[u] + weight:
                        distances[v] = distances[u] + weight
                        previous_gate[v] = u  # Track the previous gate

        # Step 5: Get the longest path length and the primary output gate
        longest_path_length = float('-inf')
        primary_output_gate_for_longest_path = None

        # Track the primary output gate for the longest path
        for v in distances:
            if distances[v] >= 0:
                distances[v] += self.gates[v].gate_delay
                if distances[v] > longest_path_length:
                    longest_path_length = distances[v]
                    primary_output_gate_for_longest_path = v  # Track the gate at the end of the longest path

        # Reconstruct the path from the primary input to primary output
        current_gate = primary_output_gate_for_longest_path
        longest_path = []

        while previous_gate[current_gate] is not None:
            longest_path.append(current_gate)
            current_gate = previous_gate[current_gate]

        longest_path.append(current_gate)  # Add the starting primary input gate
        longest_path.reverse()  # Reverse the path to get the correct order from input to output

        primary_input_gate_for_longest_path = longest_path[0]  # The first gate in the path

        return longest_path_length, primary_input_gate_for_longest_path, primary_output_gate_for_longest_path




    def read_gate_positions_and_calculate_delay(self, filename):
        """
        Reads the gate positions from output.txt, updates the positions in self.gates,
        and returns the critical path delay calculated using self.cost_function().
        """
        try:
            with open(filename, 'r') as file:
                for line in file:
                    print(f"Reading line: {line.strip()}")  # Debugging: Print raw line
                    
                    tokens = line.strip().split()

                    # Skip empty lines
                    if not tokens:
                        continue

                    # Handle bounding box (this may not be necessary for the delay calculation)
                    if tokens[0] == "bounding_box":
                        bounding_box_width = float(tokens[1])
                        bounding_box_height = float(tokens[2])
                        print(f"Bounding box: {bounding_box_width} x {bounding_box_height}")
                    
                    # Handle gate positions
                    elif tokens[0].startswith('g'):  # Assuming gate IDs start with 'g'
                        if len(tokens) != 3:
                            print(f"Malformed line for gate: {line.strip()}")
                            continue

                        gate_id = tokens[0]
                        try:
                            real_x = float(tokens[1])
                            real_y = float(tokens[2])

                            # Update the gate's position in self.gates
                            if gate_id in self.gates:
                                gate = self.gates[gate_id]
                                gate.x = real_x
                                gate.y = real_y
                                print(f"Updated Gate {gate_id}: Position ({real_x}, {real_y})")
                            else:
                                print(f"Warning: Gate {gate_id} not found in self.gates.")
                        except ValueError:
                            print(f"Error parsing coordinates for {gate_id}: {tokens[1]}, {tokens[2]}")
                    
                    # Handle wire length (not used in the delay calculation but parsed)
                    elif tokens[0] == "critical_path_delay":
                        try:
                            total_wire_length = float(tokens[1])
                            print(f"Critical path delay: {total_wire_length}")
                        except ValueError:
                            print(f"Error parsing wire length: {tokens[1]}")

            # After updating the gate positions, calculate and return the critical delay
            print("Gate positions updated. Now calculating critical path delay...")
            for gate in self.gates.values():
                print(f"Gate {gate.name}: Position ({gate.x}, {gate.y})")
            return self.cost_function()  # Call the cost function to compute the critical path delay

        except FileNotFoundError:
            print(f"Error: File {filename} not found.")
        # except Exception as e:
        #     print(f"An error occurred: {e}")
        #     return None  # Return None in case of an error
        
    def path_finder(self, primary_input_gate, primary_output_gate):
        """
        Find the path with the longest delay from a specific primary input gate to a specific primary output gate.
        Return the path with both gates and pins involved in the longest path, including the primary input and output.
        """
        import random

        # Step 1: Build the graph representation (include pins)
        self.connections_of_gate = dict()  # Initialize graph
        in_degree = {gate_name: 0 for gate_name in self.gates}  # Initialize in-degrees
        previous_gate_pin = {gate_name: None for gate_name in self.gates}  # Track previous gate and pin

        # Calculate wire delays (Ensure wire connections are captured properly)
        for a in self.a_to_bs:
            self.calculate_wire_delay(a)  # Calculate wire delay for each output pin

        # Build the graph from nets and track both gate and pin connections (Ensure wires are captured)
        for net in self.nets:
            if net.pin1.gate_name not in self.connections_of_gate:
                self.connections_of_gate[net.pin1.gate_name] = []
            self.connections_of_gate[net.pin1.gate_name].append(net)
            in_degree[net.pin2.gate_name] += 1  # Increment in-degree for destination gate

        # Step 2: Topological sorting using Kahn's algorithm
        queue = deque([gate_name for gate_name in self.gates if in_degree[gate_name] == 0])
        gates_sorted = []

        while queue.is_empty() == False:
            current_gate = queue.popleft()
            gates_sorted.append(current_gate)
            if current_gate not in self.connections_of_gate:
                self.connections_of_gate[current_gate] = []
            for net in self.connections_of_gate[current_gate]:
                connected_pin = net.pin2
                in_degree[connected_pin.gate_name] -= 1
                if in_degree[connected_pin.gate_name] == 0:
                    queue.append(connected_pin.gate_name)

        # Step 3: Initialize distances for longest path calculation
        distances = {gate_name: float('-inf') for gate_name in self.gates}
        distances[primary_input_gate] = 0  # Start distance at 0 for the given primary input

        # Step 4: Relax edges to find the longest path and track previous gates and pins
        for u in gates_sorted:
            if distances[u] != float('-inf'):  # Only consider reachable nodes
                if u not in self.connections_of_gate:
                    self.connections_of_gate[u] = []
                for net in self.connections_of_gate[u]:
                    v = net.pin2.gate_name
                    weight = self.pin_to_output_delay[net.pin1.pin_name]
                    if distances[v] < distances[u] + weight:
                        distances[v] = distances[u] + weight
                        previous_gate_pin[v] = (u, net.pin1.pin_name, net.pin2.pin_name)  # Track previous gate and pins

        # Step 5: Get the longest path length for the specific primary output gate
        longest_path_length = float('-inf')
        primary_output_gate_for_longest_path = None

        # Identify the primary output gate with the longest path
        for v in distances:
            if distances[v] >= 0:
                distances[v] += self.gates[v].gate_delay  # Add the gate delay for the final gate
                if distances[v] > longest_path_length:
                    longest_path_length = distances[v]
                    primary_output_gate_for_longest_path = v  # Track the gate at the end of the longest path

        # Step 6: Reconstruct the path from the primary input to primary output, including pins
        path = []
        current_gate = primary_output_gate_for_longest_path

        while current_gate is not None and previous_gate_pin[current_gate] is not None:
            prev_gate, pin1_name, pin2_name = previous_gate_pin[current_gate]
            path.append((prev_gate, pin1_name, current_gate, pin2_name))  # Append the gates and pins to the path
            current_gate = prev_gate

        path.reverse()  # Reverse the path to get the correct order from input to output

        # Step 7: Select a left-side input pin from the primary input gate (x = 0)
        left_side_pins = [pin.pin_index for pin in self.gates[primary_input_gate].pins if pin.x == 0]  # Left-side pins
        if left_side_pins:
            primary_input_pin = f"p{random.choice(left_side_pins)}"
        else:
            raise ValueError(f"No left-side pin found for gate {primary_input_gate}")

        # Step 8: Select any output pin from the primary output gate
        output_pins = [pin.pin_index for pin in self.gates[primary_output_gate].pins if pin.x != 0]  # Output pins (not x = 0)
        if output_pins:
            primary_output_pin = f"p{random.choice(output_pins)}"
        else:
            raise ValueError(f"No output pin found for gate {primary_output_gate}")

        # Step 9: Print the critical path in the required format without duplicating pins
        formatted_path = []

        # Insert the primary input pin at the start of the formatted path (not the path itself)
        formatted_path.append(f"{primary_input_gate}.{primary_input_pin}")

        # Add all gates and pins from the path (including the first gate after the primary input)
        for prev_gate, prev_pin, curr_gate, curr_pin in path:
            prev_pin_formatted = prev_pin.split(".")[1] if "." in prev_pin else prev_pin
            curr_pin_formatted = curr_pin.split(".")[1] if "." in curr_pin else curr_pin
            formatted_path.append(f"{prev_gate}.{prev_pin_formatted} {curr_gate}.{curr_pin_formatted}")

        # Append the primary output pin at the end of the formatted path
        formatted_path.append(f"{primary_output_gate}.{primary_output_pin}")

        # Print the final critical path
        print(f"Critical Path: {' '.join(formatted_path)}")

        return formatted_path, longest_path_length  # Return raw path and longest path delay
