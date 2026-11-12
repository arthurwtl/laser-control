"""mode_map.py — carte des sauts de mode (courant x piezo).

Pour chaque courant (axe Y), scanne le piezo (axe X) et enregistre
l'intensite de la photodiode (Red Pitaya). Affiche la carte et la
sauvegarde dans mode_map.npy (ecrase la carte precedente).

Usage :
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

CURRENTS = np.arange(70, 110, 1)   # mA — axe Y (pas de 1 mA)
SCAN_FREQ = 20.0                   # Hz — vitesse de scan piezo
SCAN_AMP = 20.0                    # V — amplitude piezo (peak-to-peak)
SCAN_OFFSET = 50.0                 # V — centre piezo
SETTLE = 0.1                       # s — stabilisation du courant

# décimation (puissance de 2) pour ~1 période de scan
_target = RedPitaya.ADC_RATE / (RedPitaya.BUFFER * SCAN_FREQ)
DEC = max(1, min(65536, 2 ** int(round(math.log2(_target)))))


def main():
    laser_host = sys.argv[1] if len(sys.argv) > 1 else LASER_HOST
    rp_host = sys.argv[2] if len(sys.argv) > 2 else RP_HOST

    with Laser(host=laser_host) as laser, RedPitaya(rp_host) as rp:
        laser.set_scan_output(50)   # scan -> piezo
        laser.scan(frequency=SCAN_FREQ, amplitude=SCAN_AMP, offset=SCAN_OFFSET, enable=True)

        t = rp.time_axis(DEC) * 1e3  # ms (identique pour toutes les lignes)

        rows = []
        for mA in CURRENTS:
            laser.set_current(mA)
            time.sleep(SETTLE)
            v = rp.acquire(dec=DEC)
            rows.append(v)
            print(f"current {mA:6.1f} mA   mean {v.mean():.3f} V   std {v.std():.3f} V")

        laser.scan_off()

        data = np.array(rows)
        np.save("mode_map.npy", data)   # écrase la carte précédente

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
