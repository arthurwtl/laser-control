import sys

from laser import Laser

HOST = "192.168.55.1"


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else HOST
    laser = Laser(host=host)

    with laser:
        print("=== Slew rate (vitesse max de variation des consignes) ===")
        print("Courant :")
        print("  slew-rate          :", laser.get('laser1:dl:cc:output-filter:slew-rate'), "mA/s")
        print("  limite active      :", laser.get('laser1:dl:cc:output-filter:slew-rate-enabled'))
        print("  actuellement limité:", laser.get('laser1:dl:cc:output-filter:slew-rate-limited'))
        print("Piezo :")
        print("  slew-rate          :", laser.get('laser1:dl:pc:output-filter:slew-rate'), "V/s")
        print("  limite active      :", laser.get('laser1:dl:pc:output-filter:slew-rate-enabled'))
        print("  actuellement limité:", laser.get('laser1:dl:pc:output-filter:slew-rate-limited'))


if __name__ == "__main__":
    main()
