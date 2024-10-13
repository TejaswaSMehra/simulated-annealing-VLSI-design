#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from tkinter import *
from PIL import Image, ImageTk
import random as random
import tkinter.messagebox as messagebox

import math

# Function to parse the input data from input.txt


# Function to parse the input data from input.txt


import argparse
import math

# Function to parse the input data from input.txt
def parse_input(data):
    gates = {}
    pins = {}
    wires = []

    for line in data:
        tokens = line.split()

        if tokens[0].startswith('g'):
            # Parsing gate dimensions
            gate_name = tokens[0]
            width, height = int(tokens[1]), int(tokens[2])
            gates[gate_name] = {"width": width, "height": height}
        
        elif tokens[0] == "pins":
            # Parsing pin coordinates
            gate_name = tokens[1]
            pin_coords = [(int(tokens[i]), int(tokens[i+1])) for i in range(2, len(tokens), 2)]
            pins[gate_name] = pin_coords

        elif tokens[0] == "wire":
            # Parsing wire connections
            wire_from = tokens[1].split('.')
            wire_to = tokens[2].split('.')
            wires.append((wire_from, wire_to))
    
    return gates, pins, wires

# Function to parse the gate positions from output.txt
def parse_gate_positions(data):
    gate_positions = {}
    
    for line in data:
        tokens = line.split()

        if tokens[0].startswith('g'):
            gate_name = tokens[0]
            x, y = int(tokens[1]), int(tokens[2])
            gate_positions[gate_name] = (x, y)
    
    return gate_positions

# Function to calculate pin coordinates based on gate placement
def calculate_pin_coordinates(gate_positions, gates, pins):
    pin_positions = {}

    for gate, position in gate_positions.items():
        gate_x, gate_y = position
        pin_positions[gate] = [(gate_x + px, gate_y + py) for (px, py) in pins[gate]]

    return pin_positions

# Function to calculate Manhattan distance between two points
def calculate_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

# Function to compute a 2D matrix of distances between all pairs of pins
def calculate_all_pin_distances(pin_positions):
    all_pins = []  # To store all pins and their coordinates
    pin_names = []  # To keep track of which pin belongs to which gate and index
    gate_names = []  # To track which gate each pin belongs to

    # Flattening the pin_positions dictionary into a list of pins with their coordinates and names
    for gate, pin_list in pin_positions.items():
        for i, pin_coords in enumerate(pin_list):
            pin_name = f"{gate}.p{i+1}"
            all_pins.append(pin_coords)
            pin_names.append(pin_name)
            gate_names.append(gate)  # Keep track of which gate each pin belongs to
    
    # Create a 2D matrix for distances
    distance_matrix = [[0] * len(all_pins) for _ in range(len(all_pins))]

    # Calculate distances between all pairs of pins
    for i in range(len(all_pins)):
        for j in range(len(all_pins)):
            if i != j:
                if gate_names[i] == gate_names[j]:
                    # Pins belong to the same gate, set distance to infinity
                    distance_matrix[i][j] = math.inf
                else:
                    # Calculate Manhattan distance for pins from different gates
                    distance_matrix[i][j] = calculate_distance(all_pins[i], all_pins[j])
    
    return distance_matrix, pin_names, gate_names

# Function to compute a 2D matrix of True/False for connected pins or same gate pins
def calculate_connection_matrix(pin_positions, pin_names, gate_names, wires):
    connection_matrix = [[False] * len(pin_names) for _ in range(len(pin_names))]

    # Explicitly mark False for pins belonging to the same gate
    for i in range(len(pin_names)):
        for j in range(len(pin_names)):
            if gate_names[i] == gate_names[j]:
                connection_matrix[i][j] = False  # Pins of the same gate must have False

    # Mark True for connected pins based on the wire connections
    for wire in wires:
        gate1, pin1 = wire[0]
        gate2, pin2 = wire[1]
        pin1_idx = int(pin1[1:]) - 1
        pin2_idx = int(pin2[1:]) - 1
        pin1_full = f"{gate1}.p{pin1_idx + 1}"
        pin2_full = f"{gate2}.p{pin2_idx + 1}"

        if pin1_full in pin_names and pin2_full in pin_names:
            idx1 = pin_names.index(pin1_full)
            idx2 = pin_names.index(pin2_full)
            connection_matrix[idx1][idx2] = True
            
    
    return connection_matrix

# New function to return a sequential list of pin coordinates
def get_pin_coordinates_in_order(pin_positions):
    ordered_pin_coordinates = []
    for gate, pin_list in pin_positions.items():
        ordered_pin_coordinates.extend(pin_list)  # Flatten the coordinates into a single list
    return ordered_pin_coordinates



class draw_gate_packing(Tk):
    def create_rectangle(self, x1, y1, x2, y2, **kwargs):
        if "alpha" in kwargs:
            alpha = int(kwargs.pop("alpha") * 255)
            fill = kwargs.pop("fill")
            fill = fill + (alpha,)
            image = Image.new("RGBA", (x2 - x1, y2 - y1), fill)
            self.images.append(ImageTk.PhotoImage(image))
            self.canvas.create_image(x1, y1, image=self.images[-1], anchor="nw")
        self.canvas.create_rectangle(x1, y1, x2, y2, **kwargs)

    def draw_grid(self, canvas, width, height, grid_size):
        """Draws the grid lines on the canvas."""
        for i in range(0, width, grid_size):
            self.canvas.create_line([(i, 0), (i, height)], tag="grid_line", fill="lightgray")
        for i in range(0, height, grid_size):
            self.canvas.create_line([(0, i), (width, i)], tag="grid_line", fill="lightgray")

    def check_overlap(self, rect1, rect2):
        """Check if two rectangles overlap."""
        x1, y1, x2, y2 = rect1
        x3, y3, x4, y4 = rect2
        return not (x2 <= x3 or x4 <= x1 or y2 <= y3 or y4 <= y1)

    def __init__(self, input_f, output_f, pin_data, grid_dimensions):
        self.scale = 0
        self.shift = 0
        super(draw_gate_packing, self).__init__()
        self.images = []
        self.title("Gate Placement Visualization")

        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Set the canvas size based on the screen size
        canvas_width = int(screen_width * 0.9)
        canvas_height = int(screen_height * 0.9)

        row_size, column_size = grid_dimensions
        grid_size_x = canvas_width // column_size
        grid_size_y = canvas_height // row_size
        grid_size = min(grid_size_x, grid_size_y)
        self.scale = grid_size

        gates_rects = []
        overlap_detected = False

        for g, sz in output_f.items():
            if g == "bounding_box":
                self.shift = self.scale * (sz[1])
                self.canvas = Canvas(self, width=canvas_width, height=canvas_height, bg="white")
                self.draw_grid(self, canvas_width, canvas_height, grid_size)
                self.create_rectangle(0, 0, self.scale * sz[0], self.scale * sz[1], outline="black", width=5)
            else:
                de = random.randint(0, 255)
                re = random.randint(0, 255)
                we = random.randint(0, 255)
                color = (de, re, we)
                x1 = self.scale * sz[0]
                y1 = self.shift - self.scale * input_f[g][1] - self.scale * sz[1]
                x2 = self.scale * sz[0] + self.scale * input_f[g][0]
                y2 = self.shift - self.scale * sz[1]

                # Check for overlap with previously drawn gates
                current_rect = (x1, y1, x2, y2)
                for gate_rect in gates_rects:
                    if self.check_overlap(current_rect, gate_rect):
                        overlap_detected = True
                        break

                self.create_rectangle(x1, y1, x2, y2, outline="black", fill=color, width=1, alpha=0.5)
                self.canvas.create_text(x1 + (x2 - x1) / 2, y1 + (y2 - y1) / 2, font=("Arial", grid_size), text=g)

                # Add current gate rectangle to list
                gates_rects.append(current_rect)

                # Draw the pins for this gate
                if g in pin_data:
                    for pin in pin_data[g]:
                        px = x1+ self.scale * pin[0]
                        py = y2- self.scale * pin[1]
                        self.canvas.create_oval(px - 5, py - 5, px + 5, py + 5, fill="black")  # Draw bold pin point

        self.canvas.pack()

        if overlap_detected:
            messagebox.showinfo("Overlap Detected", "Overlap detected!!")


def visualize_gates(coordinates_file, dimensions_file, grid_dimensions):
    """Visualizes gates and their grid cell coverage."""
    # Read the dimensions file
    gate_dimensions = {}
    pin_data = {}
    with open(dimensions_file, "r") as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            gate_info = line.split()
            if len(gate_info) == 3 and gate_info[0].startswith('g'):
                name = gate_info[0]
                width = int(gate_info[1])
                height = int(gate_info[2])
                gate_dimensions[name] = (width, height)
            elif gate_info[0] == "pins":
                gate_name = gate_info[1]
                pin_coords = [(int(gate_info[i]), int(gate_info[i + 1])) for i in range(2, len(gate_info), 2)]
                pin_data[gate_name] = pin_coords

    # Read the coordinates file
    gates = {}
    with open(coordinates_file, "r") as file:
        lines = file.readlines()
        for line in lines:
            gate_info = line.split()
            if len(gate_info) != 3:
                line.strip()
                continue
            name = gate_info[0]
            x = int(gate_info[1])
            y = int(gate_info[2])
            gates[name] = (x, y)

    # Draw gates and grid cells covered by the gates
    root = draw_gate_packing(gate_dimensions, gates, pin_data, tuple(grid_dimensions))

    root.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize gate placement on a grid.")
    parser.add_argument("coordinates_file", type=str, help="File containing gate coordinates.")
    parser.add_argument("dimensions_file", type=str, help="File containing gate dimensions and pins.")
    parser.add_argument("grid_dimensions", type=int, nargs=2, help="Grid dimensions as row_size column_size.")

    args = parser.parse_args()

    with open(args.dimensions_file, 'r') as f:
        input_data = f.readlines()

    # Reading gate positions from the output file
    with open(args.coordinates_file, 'r') as f:
        output_data = f.readlines()

    # Parse the input and output data
    gates, pins, wires = parse_input(input_data)
    gate_positions = parse_gate_positions(output_data)

    # Calculate pin coordinates based on gate positions
    pin_positions = calculate_pin_coordinates(gate_positions, gates, pins)

    # Calculate distances between all pairs of pins
    distance_matrix, pin_names, gate_names = calculate_all_pin_distances(pin_positions)

    # Calculate connection matrix (True/False for connected pins or same gate pins)
    connection_matrix = calculate_connection_matrix(pin_positions, pin_names, gate_names, wires)

    # Get the list of pin coordinates in sequential order
    ordered_pin_coordinates = get_pin_coordinates_in_order(pin_positions)

    total_wire_length=0    
    i=0
    j=0

    for i in range(0,len(connection_matrix)):
        temp=connection_matrix[i]

        if True in temp:
            bounding_x=list()
            bounding_y=list()
            bounding_x.append(ordered_pin_coordinates[i][0])
            bounding_y.append(ordered_pin_coordinates[i][1])



            for j in range(0,len(temp)):
                if connection_matrix[i][j]:
                    bounding_x.append(ordered_pin_coordinates[j][0])
                    bounding_y.append(ordered_pin_coordinates[j][1])
            
            xmin=min(bounding_x)
            xmax=max(bounding_x)
            ymin=min(bounding_y)
            ymax=max(bounding_y)

            total_wire_length=total_wire_length+xmax-xmin+ymax-ymin    
    
    print("total wire length is: ", total_wire_length)

    visualize_gates(args.coordinates_file, args.dimensions_file, args.grid_dimensions)