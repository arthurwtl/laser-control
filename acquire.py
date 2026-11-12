"""acquire.py — acquisition temps réel sur la Red Pitaya.

Lance-le, puis modifie librement le laser (fréquence de scan, etc.).
Le script relit la fréquence de scan toutes les ~2 s et adapte la
fenêtre pour afficher ~2 périodes, en temps réel.

Usage :
    uv run python acquire.py [IP_redpitaya] [IP_laser]
"""
import math
import sys
import time

import matplotlib.pyplot as plt

from laser import Laser
from redpitaya import RedPitaya

RP_HOST = "169.254.140.238"
LASER_HOST = "192.168.55.1"
FREQ_REFRESH = 2.0   # s — relecture de la fréquence de scan
PERIODS = 2          # nombre de périodes affichées


def main():
    rp_host = sys.argv[1] if len(sys.argv) > 1 else RP_HOST
    laser_host = sys.argv[2] if len(sys.argv) > 2 else LASER_HOST

    plt.ion()
    fig, ax = plt.subplots()

    with RedPitaya(rp_host) as rp, Laser(host=laser_host) as laser:
        freq = 10.0            # valeur par défaut avant la première lecture
        last_read = -1e9       # force la lecture immédiate

        while True:
            # relire la fréquence de scan régulièrement
            if time.monotonic() - last_read > FREQ_REFRESH:
                try:
                    freq = float(laser.get('laser1:scan:frequency'))
                    last_read = time.monotonic()
                except Exception:
                    pass

            # décimation (puissance de 2) pour ~2 périodes
            target = PERIODS * rp.ADC_RATE / (rp.BUFFER * freq)
            dec = max(1, min(65536, 2 ** int(round(math.log2(target)))))

            # acquisition one-shot (fiable : reset + flush à chaque fois)
            v = rp.acquire(dec=dec)
            t = rp.time_axis(dec) * 1e3

            ax.clear()
            ax.plot(t, v)
            ax.set_xlabel("time (ms)")
            ax.set_ylabel("intensity (V)")
            ax.set_title(f"scan {freq:.1f} Hz — ~{PERIODS} periods (dec {dec})")
            ax.grid(True)
            plt.pause(0.05)


if __name__ == "__main__":
    main()
