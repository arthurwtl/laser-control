import sys

from laser import Laser

HOST = "192.168.55.1"


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else HOST
    laser = Laser(host=host)

    with laser:
        print("Connected:", laser.serial)
        print("Firmware :", laser.firmware)
        print("Health   :", laser.health)
        print("Interlock:", "OPEN" if laser.interlock_open else "closed")

        # coder ici


if __name__ == "__main__":
    main()
