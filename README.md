# AI Plans Red Team Pipeline

This project uses [mise](https://mise.jdx.dev/) for managing Python virtual environments and dependencies.

## Setup

### Prerequisites

- [mise](https://mise.jdx.dev/) installed on your system
- Git access to the AISafetyLab repository

### Installation

1. **Set up Python environment with mise:**
   ```bash
   mise use python@3.11
   ```

2. **Install Python dependencies:**
   ```bash
   mise exec python@3.11 -- pip install -r requirements.txt
   ```

3. **Install AISafetyLab dependency:**
   ```bash
   # The dependency is already installed in the deps/ directory
   # It was installed using: pip install -e .
   ```

## Project Structure

```
.
├── .mise.toml              # Mise configuration
├── requirements.txt         # Python dependencies
├── deps/                   # External dependencies
│   └── AISafetyLab/       # AISafetyLab repository (installed in editable mode)
├── scripts/                # Utility scripts
│   └── install_aisafetylab.sh  # Installation script for AISafetyLab
└── main.py                 # Main application file
```

## Available Tasks

Use `mise tasks` to see available tasks:

- `mise run setup` - Set up the project environment and dependencies
- `mise run install-aisafetylab` - Install AISafetyLab dependency
- `mise run dev` - Start development environment

## Dependencies

### Core Dependencies
- Python 3.11
- requests>=2.31.0
- numpy>=1.24.0
- pandas>=2.0.0

### Development Dependencies
- pytest>=7.4.0
- black>=23.0.0
- flake8>=6.0.0

### External Dependencies
- **AISafetyLab**: Installed from `git@github.com:thu-coai/AISafetyLab.git` in editable mode
  - Location: `deps/AISafetyLab/`
  - Installation: `pip install -e .`
