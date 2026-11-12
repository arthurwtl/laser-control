# laser-control

> ⚠️ **Ce dépôt a été généré avec l'aide d'une IA** (assistant de codage). Le code a été
> testé sur le matériel réel (laser TOPTICA DLC pro + Red Pitaya), mais vérifiez-le avant
> tout usage critique.

Contrôle d'un laser **TOPTICA DLC pro** et acquisition sur **Red Pitaya** en Python —
pour la spectroscopie d'absorption (Rb, Cs) et la cartographie des sauts de mode.

## Matériel

- Laser **TOPTICA DLC pro** (DL pro) — Ethernet ou USB
- Carte **Red Pitaya STEMlab 125-14** — contrôle SCPI via Ethernet
- Photodiode **Thorlabs DET10A/M**

## Installation

```bash
cd laser-control
uv sync
```

> `redpitaya_scpi.py` est la bibliothèque SCPI officielle Red Pitaya (vendue dans le dépôt
> car elle n'est pas sur PyPI).

## Scripts

| Script | Rôle |
|---|---|
| `cli.py` | CLI interactive du laser (`on`, `set current 80`, `status`, `info`…) |
| `acquire.py` | Acquisition temps réel sur la Red Pitaya (suit la fréquence de scan) |
| `mode_map.py` | Carte des sauts de mode (courant × piezo) |
| `test_redpitaya.py` | Test connexion + acquisition (~3 périodes) |
| `test_sinus_courant.py` | Exemple : sinus sur le courant |
| `template.py` / `template_redpitaya.py` | Squelettes de départ |
| `setup_laser_net.sh` | Configure l'IP de l'adaptateur réseau du laser |

## Fichiers principaux

- `laser.py` — classe `Laser` (contrôle du DLC pro)
- `redpitaya.py` — classe `RedPitaya` (acquisition)
- `redpitaya_scpi.py` — bibliothèque SCPI officielle (vendored)

## Utilisation

```bash
# CLI laser interactive
uv run python cli.py

# Acquisition temps réel sur la Red Pitaya
uv run python acquire.py 169.254.140.238 192.168.55.1

# Carte des sauts de mode
uv run python mode_map.py 192.168.55.1 169.254.140.238
```

Les adresses IP sont des valeurs par défaut, modifiables en argument ou en tête de script.

## Documentation

La documentation complète (API Python, sauts de mode, cavités et finesse) se trouve dans
le dossier `doc laser/` fourni avec le projet.
