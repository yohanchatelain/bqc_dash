# bqc_dash

A Dash-based application for Brain-QC visualization and quality control.

## Features
- Visualize brain imaging data (PNG, GIF)
- Directory and checkpoint management
- Image navigation and zoom controls

## Requirements
- Python 3.8+
- [Dash](https://dash.plotly.com/)
- [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/)
- [Dash Extensions](https://github.com/thedirtyfew/dash-extensions)
- [Hatch](https://hatch.pypa.io/) (for building/packaging)

## Installation

1. Clone this repository or copy the `bqc_dash` directory into your project.
2. Install dependencies:
   ```bash
   pip install .
   ```

## Usage

To run the Dash app:

```bash
python -m bqc_dash
```

Or, if you have an entrypoint script:

```bash
python bqc_dash/__init__.py
```

The app will be available at [http://localhost:8050](http://localhost:8050).

## Command-Line Arguments

You can run the application with various command-line arguments to customize its behavior. Common arguments include:

- `--input-dir <path>`: Path to the input directory containing the data (see structure above).
- `--checkpoint <file>`: Path to a checkpoint file to load or save progress.
- `--port <port>`: Port to run the Dash server (default: 8050).
- `--host <host>`: Host address for the server (default: 0.0.0.0).
- `--debug`: Enable debug mode for development.

Example usage:

```bash
python -m bqc_dash --input-dir my_data --checkpoint my_checkpoint.json --port 8050 --debug
```

Refer to the code or help output (`python -m bqc_dash --help`) for a full list of available arguments and options.

## Project Structure

- `layout.py` - Main layout and UI components
- `bqc_dash/` - Core package modules
- `pyproject.toml` - Project metadata and dependencies


## Development

- Format code with Black:
  ```bash
  black .
  ```
- Lint code with Flake8:
  ```bash
  flake8 .
  ```
- Run tests:
  ```bash
  pytest
  ```

## Input Directory Structure

The application expects the following input directory structure:

```
<input_dir>/
├── <subject>.gif
└── png/
    └── <subject>/
        ├── <subject>_1.png
        └── <subject>_<repetition>.png
```

- `<input_dir>`: The root directory you select as input.
- `<subject>`: The subject identifier (e.g., subject ID or name).
- `<repetition>`: The repetition or session number for the subject.

Example:
```
my_data/
├── 12345.gif
├── 67890.gif
└── png/
    ├── 12345/
    │   ├── 12345_1.png
    │   └── 12345_2.png
    └── 67890/
        └── 67890_1.png
```

You can use `scripts/make_gifs.py` from [bqc-generator](https://github.com/yohanchatelain/bqc-generator) to generate that directory.
