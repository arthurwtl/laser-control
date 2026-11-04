# laser-control

Contrôle du laser **TOPTICA DLC pro** en Python.

## Installation (une seule fois, avec accès réseau)

```bash
cd laser-control
uv sync
```

## Utilisation

```bash
uv run python test_allumage.py            # test émission on/off
uv run python test_methodes.py            # test de toutes les méthodes (avec pauses)
uv run python template.py                 # modèle vide pour ton code
```

Chaque script se connecte à l'IP par défaut (`HOST` dans le fichier) ou à celle passée en argument :

```bash
uv run python test_allumage.py 192.168.55.1
```

## Fichiers

- `laser.py` — classe `Laser` (contrôle du DLC pro)
- `test_allumage.py` — test connexion + émission on/off
- `test_methodes.py` — test pas-à-pas de toutes les méthodes
- `template.py` — squelette pour écrire ton code
