"""Point d'entrée : test simple de connexion au laser DLC pro.

Usage :
    uv run laser-control 192.168.1.100     # IP du laser en argument
    uv run laser-control                   # IP par défaut (HOST ci-dessous)
"""
import sys
import time

from laser import Laser

# Adresse IP du DLC pro (adapter si besoin).
HOST = "192.168.55.1"


def main() -> None:
    # Récupère l'IP depuis la ligne de commande, sinon utilise la valeur par défaut.
    host = sys.argv[1] if len(sys.argv) > 1 else HOST

    print(f"Connexion au laser ({host}) ...")

    # On crée l'objet de contrôle du laser, nommé `laser`.
    laser = Laser(host=host)

    try:
        # `with` ouvre la connexion (__enter__) et la refermera (__exit__).
        with laser:
            print("✅ Connecté !")
            print("  N° de série :", laser.serial)
            print("  Firmware    :", laser.firmware)
            print("  Label       :", laser.label)
            print("  Santé       :", laser.health)
            print("  Interlock   :", "OUVERT (laser bloqué)" if laser.interlock_open else "fermé (OK)")

            # --- Test émission : éteindre → attendre 2 s → allumer → attendre 2 s → éteindre ---
            print("\n--- Test émission ---")

            if laser.is_on:
                print("Le laser est allumé → extinction.")
                laser.off()
            else:
                print("Le laser est déjà éteint.")

            print("Attente 2 s ...")
            time.sleep(2)

            print("Allumage du laser ...")
            laser.on()
            print("  émission :", laser.is_on)

            print("Attente 2 s ...")
            time.sleep(2)

            print("Extinction du laser ...")
            laser.off()
            print("  émission :", laser.is_on)
            print("Terminé.")

    except Exception as exc:
        print(f"❌ Échec de connexion : {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
