"""Entry point: simple connection test to the DLC pro laser.

Usage:
    uv run python test_allumage.py [IP]
"""
import sys
import time

from laser import Laser

HOST = "192.168.55.1"


def main() -> None:
    host = sys.argv[1] if len(sys.argv) > 1 else HOST

    print(f"Connecting to laser ({host}) ...")

    laser = Laser(host=host)

    try:
        with laser:
            print("✅ Connected!")
            print("  Serial    :", laser.serial)
            print("  Firmware  :", laser.firmware)
            print("  Label     :", laser.label)
            print("  Health    :", laser.health)
            print("  Interlock :", "OPEN (laser blocked)" if laser.interlock_open else "closed (OK)")

            print("\n--- Emission test ---")

            if laser.is_on:
                print("Laser is on → turning off.")
                laser.off()
            else:
                print("Laser is already off.")

            print("Waiting 2 s ...")
            time.sleep(2)

            print("Turning on laser ...")
            laser.on()
            print("  emission:", laser.is_on)

            print("Waiting 2 s ...")
            time.sleep(2)

            print("Turning off laser ...")
            laser.off()
            print("  emission:", laser.is_on)
            print("Done.")

    except Exception as exc:
        print(f"❌ Connection failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
