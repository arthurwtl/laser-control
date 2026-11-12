"""mode_map.py — mode-hop map (current x piezo).

For each current (Y axis), scans the piezo (X axis) and records the
photodiode intensity (Red Pitaya). Displays the map and saves it to
mode_map.npy (overwrites the previous map).

Usage:
    uv run python mode_map.py [IP_laser] [IP_redpitaya]
"""
import math
import sys
import time

import matplotlib.pyplot as plt
import numpy as np

from laser import Laser
from redpitaya import RedPitaya

LASER_HOST = "192.168.55.1"
RP_HOST = "169.254.140.238"

CURRENTS = np.arange(70, 110, 1)   # mA — Y axis (1 mA step)
SCAN_FREQ = 20.0                   # Hz — piezo scan rate
SCAN_AMP = 20.0                    # V — piezo amplitude (peak-to-peak)
SCAN_OFFSET = 50.0                 # V — piezo center
SETTLE = 0.1                       # s — current settling

# decimation (power of 2) for ~1 scan period
_target = RedPitaya.ADC_RATE / (RedPitaya.BUFFER * SCAN_FREQ)
DEC = max(1, min(65536, 2 ** int(round(math.log2(_target)))))


def main():
    laser_host = sys.argv[1] if len(sys.argv) > 1 else LASER_HOST
    rp_host = sys.argv[2] if len(sys.argv) > 2 else RP_HOST

    with Laser(host=laser_host) as laser, RedPitaya(rp_host) as rp:
        laser.set_scan_output(50)   # scan -> piezo
        laser.scan(frequency=SCAN_FREQ, amplitude=SCAN_AMP, offset=SCAN_OFFSET, enable=True)

        t = rp.time_axis(DEC) * 1e3  # ms (same for all rows)

        rows = []
        for mA in CURRENTS:
            laser.set_current(mA)
            time.sleep(SETTLE)
            v = rp.acquire(dec=DEC)
            rows.append(v)
            print(f"current {mA:6.1f} mA   mean {v.mean():.3f} V   std {v.std():.3f} V")

        laser.scan_off()

        data = np.array(rows)
        np.save("mode_map.npy", data)   # overwrites the previous map

        plt.imshow(data, aspect="auto", origin="lower",
                   extent=[t[0], t[-1], CURRENTS[0], CURRENTS[-1]], cmap="viridis")
        plt.colorbar(label="intensity (V)")
        plt.xlabel("piezo scan (time, ms)")
        plt.ylabel("current (mA)")
        plt.title(f"mode-hop map @ {SCAN_FREQ} Hz")
        plt.show()

        print("saved -> mode_map.npy")


if __name__ == "__main__":
    main()
