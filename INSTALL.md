# Installation and Setup Instructions

## Quick Setup for Jupyter Notebook Environment

If you are using this repository in a Jupyter Notebook environment, follow these steps:

### 1. Clone the Repository

```bash
git clone https://github.com/jxta/bias_with_claude.git
cd bias_with_claude
```

### 2. Set Execute Permissions

```bash
chmod +x run_scripts.sh
```

### 3. Verify Installation

```bash
# Check system information
./run_scripts.sh info

# Verify required files exist
ls -la src/
```

### 4. Run a Quick Test

```bash
# Small-scale test (10^5 primes, ~2-3 minutes)
./run_scripts.sh test
```

### 5. For Jupyter Notebook Users

Open `demo.ipynb` and run the cells step by step to see the demonstration.

## Command Reference

- `./run_scripts.sh all` - Run all cases (10^6 primes, ~10-15 minutes)
- `./run_scripts.sh test` - Quick test (10^5 primes, ~2-3 minutes)
- `./run_scripts.sh case 1` - Run specific case only
- `./run_scripts.sh check` - Check existing data files
- `./run_scripts.sh info` - Show system information

## Direct SageMath Usage

```bash
# All cases
sage src/main_runner.py --all

# Specific case
sage src/main_runner.py --case 1 --all

# Custom prime range
sage src/main_runner.py --all --max-prime 500000

# Custom process count
sage src/main_runner.py --all --processes 4
```

## Requirements

- SageMath 9.5+
- Python 3.9+
- matplotlib, numpy
- Multi-core system (recommended)
- 8GB+ RAM (for 10^6 primes)

## Troubleshooting

If you encounter permission errors, make sure to run:
```bash
chmod +x run_scripts.sh
```

If SageMath is not found, install it or use the appropriate command for your system.
