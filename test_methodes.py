import sys

from laser import Laser

HOST = "192.168.55.1"


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else HOST
    laser = Laser(host=host)

    with laser:
        print("=== Information ===")
        print("Serial    :", laser.serial)
        print("Firmware  :", laser.firmware)
        print("Label     :", laser.label)
        print("Health    :", laser.health)
        print("Interlock :", "OPEN" if laser.interlock_open else "closed")
        input("> Press Enter to continue...")

        print("\n=== Current: setpoint 101 mA ===")
        laser.set_current(101)
        print("setpoint:", laser.get('laser1:dl:cc:current-set'), "mA")
        input("> Press Enter to continue...")

        print("\n=== Temperature: setpoint 20 °C ===")
        laser.set_temperature(20)
        print("temperature:", laser.get_temperature(), "°C")
        input("> Press Enter to continue...")

        print("\n=== Temperature stabilization ===")
        ok = laser.wait_temperature(timeout=60)
        print("stabilized:", ok)
        input("> Press Enter to continue...")

        print("\n=== Piezo: setpoint 50 V ===")
        laser.set_offset(50)
        print("piezo:", laser.get_offset(), "V")
        input("> Press Enter to continue...")

        print("\n=== Emission ON ===")
        laser.on()
        print("is_on         :", laser.is_on)
        print("actual current:", laser.get_current(), "mA")
        input("> Press Enter to continue...")

        print("\n=== Emission OFF ===")
        laser.off()
        print("is_on:", laser.is_on)
        input("> Press Enter to continue...")

        print("\n=== Scan: offset 22 V, amplitude 50 V ===")
        laser.scan(frequency=10, amplitude=50, offset=22, enable=True)
        print("scan started")
        input("> Press Enter to continue...")

        print("\n=== Scan OFF ===")
        laser.scan_off()
        print("scan stopped")
        input("> Press Enter to continue...")

        print("\n=== Lock (license required) ===")
        try:
            laser.lock_on()
            print("lock_state:", laser.lock_state)
            laser.lock_off()
        except Exception as e:
            print("lock unavailable:", e)
        input("> Press Enter to continue...")

        print("\n=== Save / Load ===")
        laser.save()
        print("configuration saved")
        laser.load()
        print("configuration reloaded")
        input("> Press Enter to continue...")

        print("\n=== Generic access ===")
        print("get('laser1:dl:cc:current-set') :", laser.get('laser1:dl:cc:current-set'), "mA")
        print(laser.exec('system-messages:show-all', output_type=str))
        input("> Press Enter to continue...")

        print("\n=== Shutdown ===")
        laser.shutdown()
        print("emission off, current set to 0")
        print("is_on:", laser.is_on)


if __name__ == "__main__":
    main()
