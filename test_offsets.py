import sys

from laser import Laser

HOST = "192.168.55.1"


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else HOST
    laser = Laser(host=host)

    with laser:
        print("Connected:", laser.serial)
        print()
        print("piezo DC (voltage-set) :", laser.get('laser1:dl:pc:voltage-set'), "V")
        print("piezo actual (voltage-act):", laser.get_offset(), "V")
        print("scan offset            :", laser.get('laser1:scan:offset'), "V")
        print("scan amplitude         :", laser.get('laser1:scan:amplitude'), "V")


if __name__ == "__main__":
    main()
