import sys

from laser import Laser

HOST = "192.168.55.1"


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else HOST
    laser = Laser(host=host)

    with laser:
        print("=== Slew rate (max rate of change of setpoints) ===")
        print("Current:")
        print("  slew-rate      :", laser.get('laser1:dl:cc:output-filter:slew-rate'), "mA/s")
        print("  limit enabled  :", laser.get('laser1:dl:cc:output-filter:slew-rate-enabled'))
        print("  currently limited:", laser.get('laser1:dl:cc:output-filter:slew-rate-limited'))
        print("Piezo:")
        print("  slew-rate      :", laser.get('laser1:dl:pc:output-filter:slew-rate'), "V/s")
        print("  limit enabled  :", laser.get('laser1:dl:pc:output-filter:slew-rate-enabled'))
        print("  currently limited:", laser.get('laser1:dl:pc:output-filter:slew-rate-limited'))


if __name__ == "__main__":
    main()
