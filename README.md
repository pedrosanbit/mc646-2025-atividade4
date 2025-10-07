# Activity 4

This repository contains a small utility to generate a control-flow graph (CFG) image from a Python script using `staticfg` and Graphviz and three different features in "src" package.

## Requirements

- Python 3.8+
- System Graphviz (```sudo apt install graphviz``` on Debian/Ubuntu)
- Python packages listed in `requirements.txt` (see below)

The Python dependencies in `requirements.txt` include:

- `pytest` 
- `staticfg`

## Setup

1. Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt

3. Install system Graphviz

On Debian/Ubuntu:

```bash
sudo apt update
sudo apt install graphviz
```

On Fedora/CentOS:

```bash
sudo dnf install graphviz
```

On macOS (Homebrew):

```bash
brew install graphviz
```


## Running `generate_graph.py`

The script generates a PNG image of the control-flow graph for a target Python script and places the image in the `cfg/` directory.

Usage:

```bash
python generate_graph.py -s path/to/target_script.py -n output_name
```

- `-s` / `--script`: Path to the Python script to analyze (required)
- `-n` / `--name`: Base name for the output image (optional, defaults to `cfg_output`)

Example:

```bash
python generate_graph.py -s src/energy/EnergyManagementSystem.py -n energy_cfg
```

This will create the rendered image at `cfg/energy_cfg.png` (the script uses `cfg.build_visual(f"cfg/{args.name}", "png")`).

## Generating Coverage Report

You can run the test suite with coverage reporting using `pytest` and the `--cov` plugin (because of the lib `pytest-cov`). For example, to measure coverage for the `SmartEnergyManagementSystem` class (module path `src.energy.EnergyManagementSystem`), run:

```bash
pytest --cov=src.energy.EnergyManagementSystem --cov-report=html:coverage_report --cov-branch
```

This command will:
- Run the tests with pytest
- Measure coverage for the specified module
- Generate an HTML coverage report in the `coverage_report/` directory. Feel free to change the name of the output directory by changing the value after `html:`.

You can open `coverage_report/index.html` in your browser to view the detailed coverage report.