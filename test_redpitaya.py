import math
import sys

import matplotlib.pyplot as plt

from redpitaya import RedPitaya

HOST = "169.254.140.238"


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else HOST
    freq = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0   # Hz

    # décimation (puissance de 2) la plus proche de ~3 périodes
    target = 3 * RedPitaya.ADC_RATE / (RedPitaya.BUFFER * freq)
    dec = max(1, min(65536, 2 ** int(round(math.log2(target)))))

    with RedPitaya(host) as rp:
        print("Connected:", rp.info)
        v = rp.acquire(dec=dec)
        t = rp.time_axis(dec) * 1e3   # ms
        n = t[-1] * freq / 1e3         # nombre de périodes affichées

        print(f"frequency : {freq} Hz")
        print(f"decimation: {dec}")
        print(f"window    : {t[-1]:.0f} ms ≈ {n:.1f} periods")

        plt.plot(t, v)
        plt.xlabel("time (ms)")
        plt.ylabel("intensity (V)")
        plt.title(f"{freq} Hz — ~3 periods")
        plt.grid(True)
        plt.show()


if __name__ == "__main__":
    main()
