import math
import sys
import time

from laser import Laser

HOST = "192.168.55.1"

FREQ = 100.0      # Hz
OFFSET = 75.0   # mA (sine center)
AMP = 10.0      # mA (amplitude)
POINTS = 80      # points per period


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else HOST
    dt = 1.0 / (FREQ * POINTS)      # interval between two points (s)

    with Laser(host=host) as laser:
        print("Connected:", laser.serial)

        laser.on()   # emission ON so the current actually flows

        try:
            t0 = time.monotonic()
            i = 0
            while True:
                t = i * dt
                mA = OFFSET + AMP * math.sin(2 * math.pi * FREQ * t)
                laser.set_current(mA)
                print(f"t = {t:.3f} s   current = {mA:.2f} mA")
                i += 1
                time.sleep(max(0.0, t0 + i * dt - time.monotonic()))
        except KeyboardInterrupt:
            print("\nStop requested (Ctrl+C).")
        # finally:
        #     laser.off()
        #     laser.set_current(0)


if __name__ == "__main__":
    main()
