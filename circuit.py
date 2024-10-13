class Circuit:
    def __init__(self):
        self.gates = {}
        self.nets = []
        self.pin_lookup = {}  # Dictionary to map pin names to pins
        self.connected_components = None
    
    def add_gate(self, gate):
        self.gates[gate.name] = gate
        # Add pins of the gate to the pin_lookup dictionary
        for pin in gate.pins:
            pin_name = f"{gate.name}.p{pin.pin_index}"
            self.pin_lookup[pin_name] = pin

    def add_net(self, net):
        self.nets.append(net)

    def build_graph(self):
        graph = {}
        for gate in self.gates.values():
            for pin in gate.pins:
                pin_name = f"{gate.name}.p{pin.pin_index}"  # Use full pin name
                if pin_name not in graph:
                    graph[pin_name] = []
        
        for net in self.nets:
            pin1, pin2 = net.pin1, net.pin2
            pin1_name = f"{pin1.gate_name}.p{pin1.pin_index}"  # Full pin name
            pin2_name = f"{pin2.gate_name}.p{pin2.pin_index}"
            graph[pin1_name].append(pin2_name)
            graph[pin2_name].append(pin1_name)

        return graph

    def dfs(self, node, graph, visited, component):
        visited[node] = True
        component.append(node)
        for neighbor in graph[node]:
            if not visited[neighbor]:
                self.dfs(neighbor, graph, visited, component)

    def find_connected_components(self):
        graph = self.build_graph()
        visited = {node: False for node in graph}
        components = []
        for node in graph:
            if not visited[node]:
                component = []
                self.dfs(node, graph, visited, component)
                components.append(component)
        return components

    def bounding_box(self, component):
        """
        Calculate the bounding box for a connected component of pins using the pin_lookup.
        :param component: List of pin names in the component.
        :return: Bounding box as (min_x, min_y, max_x, max_y).
        """
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')

        for pin_name in component:
            pin = self.pin_lookup[pin_name]
            gate = self.gates[pin.gate_name]
            absolute_x = gate.x + pin.x  # Get absolute x-coordinate of the pin
            absolute_y = gate.y + pin.y  # Get absolute y-coordinate of the pin

            min_x = min(min_x, absolute_x)
            min_y = min(min_y, absolute_y)
            max_x = max(max_x, absolute_x)
            max_y = max(max_y, absolute_y)

        return min_x, min_y, max_x, max_y

    def semi_perimeter(self, bounding_box):
        """
        Calculate the semi-perimeter of a bounding box.
        :param bounding_box: (min_x, min_y, max_x, max_y)
        :return: Semi-perimeter of the bounding box.
        """
        min_x, min_y, max_x, max_y = bounding_box
        width = max_x - min_x
        height = max_y - min_y
        return width + height

    def total_wire_cost(self):
        """
        Calculate the total wire cost as the sum of the semi-perimeters of all connected components.
        :return: Total wire cost.
        """
        if not self.connected_components:
            self.connected_components = self.find_connected_components()
            print('Calculated connected components')
        
        components = self.connected_components  # Find all connected components
        total_cost = 0
        for component in components:
            bounding_box = self.bounding_box(component)  # Get the bounding box for the component
            total_cost += self.semi_perimeter(bounding_box)  # Add the semi-perimeter to the total cost
        return total_cost
