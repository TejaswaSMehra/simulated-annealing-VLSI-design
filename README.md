# Gate Placement and Wirelength Optimization

This repository implements a simulated annealing algorithm for optimizing the placement of gates in VLSI design. The primary goal is to minimize wirelength while preventing overlaps between gates.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [File Descriptions](#file-descriptions)
- [Simulated Annealing Approaches](#simulated-annealing-approaches)
- [Test Cases](#test-cases)
- [Contributing](#contributing)

## Usage

1. **Input Generation**: Use `tc_gen.py` to generate a test case in the `input.txt` format.
2. **Run Optimization**: Execute `main.py` to run the simulated annealing algorithm on the generated circuit.
3. **Output**: The results, including the optimized gate positions and total wirelength, will be saved in `output.txt`.

## File Descriptions

- **`main.py`**: The main script that parses the input file, runs the simulated annealing optimization, and outputs results.
- **`simulated_annealing.py`**: Contains the `SimulatedAnnealing` class, which employs a basic simulated annealing technique to minimize wirelength by perturbing gate positions.
- **`simulated_annealing2.py`**: Implements the `SimulatedAnnealing2` class, which introduces enhancements like grid-based packing and allows for more structured optimization by employing envelope management to prevent overlaps.
- **`circuit.py`**: Defines the `Circuit` class, which manages gates, nets, and pin configurations.
- **`gate.py`**: Defines the `Gate` class, representing individual gates with their properties and methods.
- **`net.py`**: Defines the `Net` class, representing connections between gate pins.
- **`pin.py`**: Defines the `Pin` class, representing the pins of each gate.
- **`inputparsing.py`**: Contains the `InputParser` class for reading and parsing the input file.
- **`visualizer.py`**: Provides functions for visualizing the circuit and its layout.
- **`tc_gen.py`**: Generates random test cases for circuit configurations.

## Simulated Annealing Approaches

1. **SimulatedAnnealing**: This implementation uses basic perturbation techniques to explore the solution space. It randomly moves gates and accepts or rejects new configurations based on a probability function that considers cost differences.

2. **SimulatedAnnealing2**: This enhanced version incorporates a grid-based packing strategy, organizing gates within envelopes to avoid overlaps. It allows for both vertical and horizontal packing, selecting the configuration that minimizes wirelength effectively.

## Test Cases

The algorithm has been tested with various circuit configurations, including small, medium, and large circuits. You can find detailed test cases and their results in the respective functions within `tc_gen.py`.

## Contributing

Feel free to contribute by forking the repository and submitting pull requests. For any issues or feature requests, please open an issue in the GitHub repository.

```
