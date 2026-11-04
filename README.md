# laser-control

Contrôle minimal du laser **TOPTICA DLC pro** en Python : test du courant diode et du piezo.

## Installation (sur ta machine, avec accès réseau)

```bash
cd laser-control
uv sync          # installe les dépendances et crée l'environnement .venv
```

## Utilisation

```bash
uv run laser-control 192.168.1.100     # IP de ton DLC pro
uv run laser-control                   # utilise l'IP par défaut (voir __init__.py)
```

> ⚠️ Le script ne fait que changer les **consignes** (courant, piezo). Il **n'active pas**
> l'émission laser. Pour plus de fonctions (émission, température, scan, lock…),
> voir `../doc laser/README.md`.

## Dépendances

- `toptica-lasersdk` : SDK officiel TOPTICA (contrôle du DLC pro)
- `numpy` : traitement numérique (prêt pour l'acquisition Red Pitaya)
