import sys

from laser import Laser

HOST = "192.168.55.1"


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else HOST
    laser = Laser(host=host)

    with laser:
        print("=== Informations ===")
        print("Série     :", laser.serial)
        print("Firmware  :", laser.firmware)
        print("Label     :", laser.label)
        print("Santé     :", laser.health)
        print("Interlock :", "OUVERT" if laser.interlock_open else "fermé")
        input("> Entrée pour continuer...")

        print("\n=== Courant : consigne 101 mA ===")
        laser.set_current(101)
        print("consigne (set) :", laser.get('laser1:dl:cc:current-set'), "mA")
        input("> Entrée pour continuer...")

        print("\n=== Température : consigne 20 °C ===")
        laser.set_temperature(20)
        print("température :", laser.get_temperature(), "°C")
        input("> Entrée pour continuer...")

        print("\n=== Stabilisation température ===")
        ok = laser.wait_temperature(timeout=60)
        print("stabilisée :", ok)
        input("> Entrée pour continuer...")

        print("\n=== Piezo : consigne 50 V ===")
        laser.set_piezo(50)
        print("piezo :", laser.get_piezo(), "V")
        input("> Entrée pour continuer...")

        print("\n=== Émission ON ===")
        laser.on()
        print("is_on        :", laser.is_on)
        print("courant réel :", laser.get_current(), "mA")
        input("> Entrée pour continuer...")

        print("\n=== Émission OFF ===")
        laser.off()
        print("is_on :", laser.is_on)
        input("> Entrée pour continuer...")

        print("\n=== Scan : offset 22 V, amplitude 50 V ===")
        laser.scan(frequency=10, amplitude=50, offset=22, enable=True)
        print("scan démarré")
        input("> Entrée pour continuer...")

        print("\n=== Scan OFF ===")
        laser.scan_off()
        print("scan arrêté")
        input("> Entrée pour continuer...")

        print("\n=== Lock (licence requise) ===")
        try:
            laser.lock_on()
            print("lock_state :", laser.lock_state)
            laser.lock_off()
        except Exception as e:
            print("lock indisponible :", e)
        input("> Entrée pour continuer...")

        print("\n=== Save / Load ===")
        laser.save()
        print("configuration sauvegardée")
        laser.load()
        print("configuration rechargée")
        input("> Entrée pour continuer...")

        print("\n=== Accès générique ===")
        print("get('laser1:dl:cc:current-set') :", laser.get('laser1:dl:cc:current-set'), "mA")
        print(laser.exec('system-messages:show-all', output_type=str))
        input("> Entrée pour continuer...")

        print("\n=== Shutdown ===")
        laser.shutdown()
        print("émission coupée, courant à 0")
        print("is_on :", laser.is_on)


if __name__ == "__main__":
    main()
