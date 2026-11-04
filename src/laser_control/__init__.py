"""Contrôle minimal du laser TOPTICA DLC pro : test courant diode + piezo.

Utilisation :
    uv run laser-control 192.168.1.100
    # ou sans argument (IP par défaut = HOST ci-dessous)

NOTE DE SÉCURITÉ : ce script ne fait QUE changer les consignes (courant, piezo).
Il n'active PAS l'émission laser (`laser1:emission`). Le courant de consigne ne
circule dans la diode que lorsque l'émission est active.
"""

import sys
import time

from toptica.lasersdk.client import Client, NetworkConnection

# Adresse IP du DLC pro (adapter si besoin). Peut aussi être un nom
# DNS ou le n° de série / label si vous êtes sur le même réseau.
HOST = "192.168.1.100"


def main() -> None:
    host = sys.argv[1] if len(sys.argv) > 1 else HOST
    print(f"Connexion au DLC pro : {host} ...")

    with Client(NetworkConnection(host)) as c:
        # --- Informations ---
        print("N° de série :", c.get("serial-number"))
        print("Firmware    :", c.get("fw-ver"))
        print("Santé       :", c.get("system-health-txt"))
        interlock = c.get("interlock-open")
        print("Interlock   :", "OUVERT (laser bloqué !)" if interlock else "fermé (OK)")

        # --- Test courant diode (CC) ---
        print("\n--- Test courant diode ---")
        print("Courant réel actuel     :", c.get("laser1:dl:cc:current-act"), "mA")
        c.set("laser1:dl:cc:current-set", 80.0)   # consigne 80 mA
        time.sleep(0.2)
        print("Consigne écrite (set)   :", c.get("laser1:dl:cc:current-set"), "mA")
        print("Courant réel (act)      :", c.get("laser1:dl:cc:current-act"), "mA")

        # --- Test piezo (PC) ---
        print("\n--- Test piezo ---")
        print("Tension piezo actuelle  :", c.get("laser1:dl:pc:voltage-act"), "V")
        c.set("laser1:dl:pc:voltage-set", 30.0)   # consigne 30 V
        time.sleep(0.2)
        print("Consigne écrite (set)   :", c.get("laser1:dl:pc:voltage-set"), "V")
        print("Tension piezo réelle    :", c.get("laser1:dl:pc:voltage-act"), "V")

        print("\nTerminé.")


if __name__ == "__main__":
    main()
