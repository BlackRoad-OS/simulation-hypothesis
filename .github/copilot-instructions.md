# Copilot Instructions for simulation-hypothesis

## Repository Overview

This is a static research repository containing a paper and supporting code exploring the "Simulation Hypothesis" — the computational argument that reality is self-referential. It is authored by Alexa Louise Amundson at BlackRoad OS, Inc.

## Repository Structure

- `PAPER.md` — The main research paper (21 sections)
- `DECLARATION.md`, `ORIGIN.md` — Supporting declarations
- `README.md` — Overview, abstract, and evidence index
- `code/` — Python 3 demonstration scripts (no external dependencies except `matplotlib` for `lorenz.py`)
- `evidence/` — Evidence index with references
- `index.html`, `vr.html`, `qr.html` — Static web app pages
- `manifest.json`, `icon.svg` — PWA manifest assets
- `LICENSE` — BlackRoad OS proprietary license

## Languages & Runtimes

- **Python 3** for all scripts in `code/`
- **HTML/CSS/JS** for the web app (`index.html`, `vr.html`, `qr.html`)
- No build system, no package manager, no compilation step

## Running the Code

```bash
cd code
python3 hashchain.py          # no external deps
python3 riemann_zeros.py      # no external deps
python3 lorenz.py             # requires: pip install matplotlib
python3 magic_square.py       # no external deps
python3 dna_encoding.py       # no external deps
python3 roadchain.py          # no external deps
```

## Validation

There are no automated tests. To validate changes to Python scripts, run them directly and confirm they produce expected output without errors. There are no linting configs or CI pipelines defined in this repository.

## Pull Request Guidelines

- Python code changes should be validated by running the affected script
- Documentation changes do not require code execution
- Keep changes minimal and focused on the stated task
