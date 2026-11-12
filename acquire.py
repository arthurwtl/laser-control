"""acquire.py — real-time acquisition on the Red Pitaya.

Run it, then freely adjust the laser (scan frequency, etc.).
The script re-reads the scan frequency every ~2 s and adapts the
window to display ~2 periods, in real time.

Usage:
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
FREQ_REFRESH = 2.0   # s — scan frequency re-read
PERIODS = 2          # periods displayed


def main():
    rp_host = sys.argv[1] if len(sys.argv) > 1 else RP_HOST
    laser_host = sys.argv[2] if len(sys.argv) > 2 else LASER_HOST

    plt.ion()
    fig, ax = plt.subplots()

    with RedPitaya(rp_host) as rp, Laser(host=laser_host) as laser:
        freq = 10.0            # default before first read
        last_read = -1e9       # force immediate read

        while True:
            # re-read the scan frequency periodically
            if time.monotonic() - last_read > FREQ_REFRESH:
                try:
                    freq = float(laser.get('laser1:scan:frequency'))
                    last_read = time.monotonic()
                except Exception:
                    pass

            # decimation (power of 2) for ~2 periods
            target = PERIODS * rp.ADC_RATE / (rp.BUFFER * freq)
            dec = max(1, min(65536, 2 ** int(round(math.log2(target)))))

            # one-shot acquisition (reset + flush each time)
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
