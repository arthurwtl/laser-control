# laser-control

> This repository was generated with the help of an AI coding assistant.

Control of a **TOPTICA DLC pro** laser and acquisition with a **Red Pitaya**, in Python —
for absorption spectroscopy (Rb, Cs) and mode-hop mapping.

## Hardware

- **TOPTICA DLC pro** (DL pro) — Ethernet or USB
- **Red Pitaya STEMlab 125-14** — SCPI over Ethernet
- **Thorlabs DET10A/M** photodiode

## Installation

```bash
cd laser-control
uv sync
```

`redpitaya_scpi.py` is the official Red Pitaya SCPI library (vendored, not on PyPI).

## Scripts

| Script | Purpose |
|---|---|
| `cli.py` | Interactive laser CLI (`on`, `set current 80`, `status`, `info`…) |
| `acquire.py` | Real-time acquisition on the Red Pitaya (follows the scan frequency) |
| `mode_map.py` | Mode-hop map (current × piezo) |
| `test_redpitaya.py` | Connection + acquisition test |
| `test_sinus_courant.py` | Example: sine on the current |
| `template.py` / `template_redpitaya.py` | Starter templates |
| `setup_laser_net.sh` | Configures the laser network adapter IP |

## Core modules

- `laser.py` — `Laser` class (DLC pro control)
- `redpitaya.py` — `RedPitaya` class (acquisition)

## Usage

```bash
uv run python cli.py
uv run python acquire.py 169.254.140.238 192.168.55.1
uv run python mode_map.py 192.168.55.1 169.254.140.238
```

IP addresses are defaults; override them as arguments or at the top of each script.
