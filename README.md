# GameTheoryProject

Modelling real-world elections using **Strategic Voting**.

## Overview
This repository explores how strategic behavior can change election outcomes under different voting rules. The goal is to model real-world election settings and analyze incentives for voters to vote sincerely vs. strategically.

## What’s inside
Typical contents you may find in this project:
- **Election / voting rule implementations** (e.g., plurality, runoff, ranked-choice, etc.)
- **Voter preference generation** (synthetic electorates)
- **Strategic voting models** (best response / heuristics)
- **Simulations & experiments** to compare outcomes and welfare
- **Analysis outputs** (plots, tables, exported results)

> Note: The exact set of modules/scripts may evolve as the project develops.

## Requirements
- Python 3.9+ (recommended)

If a `requirements.txt` exists, install dependencies with:

```bash
pip install -r requirements.txt
```

Otherwise, you can create a virtual environment and install packages as you add them:

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows (PowerShell)
.venv\\Scripts\\Activate.ps1

pip install -U pip
```

## Running the code
Because repositories differ in structure, here are common ways to run Python projects:

### Run a script

```bash
python path/to/script.py
```

### Run a module

```bash
python -m package_or_module
```

### Run notebooks (if present)

```bash
pip install notebook
jupyter notebook
```

## Project goals / questions
Some questions this repo is intended to help answer:
- How often does strategic voting change the winner?
- Which voting rules are more resistant to manipulation?
- Under what information assumptions (polling, full preferences, etc.) does manipulation become easier?
- What trade-offs exist between representativeness, simplicity, and manipulability?

## Contributing
Contributions are welcome.

1. Fork the repo
2. Create a feature branch
3. Commit changes with clear messages
4. Open a pull request describing the motivation and approach

## License
No license file is currently specified. If you intend others to use, modify, or redistribute this work, consider adding a LICENSE file (e.g., MIT, Apache-2.0, GPL-3.0).
