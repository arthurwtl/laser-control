"""Ready-to-use class to drive the Red Pitaya (SCPI acquisition).

Wraps the `redpitaya_scpi` library and hides raw SCPI commands.
"""
import time

import numpy as np
import redpitaya_scpi as scpi


class RedPitaya:
    """Red Pitaya STEMlab 125-14 acquisition board.

    Usage:
        rp = RedPitaya('169.254.140.238')
        with rp:
            print(rp.info)
            v = rp.acquire(dec=65536)
    """

    ADC_RATE = 125e6    # STEMlab 125-14: 125 MS/s
    BUFFER = 16384      # acquisition buffer size (samples)

    def __init__(self, host, port=5000):
        self._host = host
        self._port = port
        self._rp = None

    # ------------------------------------------------------------------ connection
    def __enter__(self):
        self._rp = scpi.scpi(self._host, port=self._port)
        return self

    def __exit__(self, *exc):
        if self._rp:
            self._rp.close()

    # --------------------------------------------------------------------- info
    @property
    def info(self):
        """Board identification (*IDN?)."""
        return self._rp.txrx_txt('*IDN?')

    # -------------------------------------------------------------- acquisition
    def arm(self, dec):
        """Arm the acquisition and discard the stale buffer (once per decimation)."""
        rp = self._rp
        rp.tx_txt('ACQ:RST')
        rp.tx_txt(f'ACQ:DEC {dec}')
        rp.tx_txt('ACQ:START')
        time.sleep(self.BUFFER / self.sample_rate(dec))

    def read(self, channel=1):
        """Trigger and read one acquisition (without re-discarding the buffer)."""
        rp = self._rp
        rp.tx_txt('ACQ:TRIG NOW')
        while True:
            rp.tx_txt('ACQ:TRIG:STAT?')
            if rp.rx_txt() == 'TD':
                break
        while True:
            rp.tx_txt('ACQ:TRIG:FILL?')
            if rp.rx_txt() == '1':
                break
        rp.tx_txt(f'ACQ:SOUR{channel}:DATA?')
        s = rp.rx_txt()
        return np.array([float(x) for x in s.strip('{}\n\r').split(',')])

    def acquire(self, channel=1, dec=1):
        """One-shot acquisition (arm then read)."""
        self.arm(dec)
        return self.read(channel)

    def intensity(self, channel=1, dec=65536, n=10):
        """Mean intensity (V) over n acquisitions -> (mean, std)."""
        self.arm(dec)
        vals = [self.read(channel).mean() for _ in range(n)]
        return float(np.mean(vals)), float(np.std(vals))

    # ------------------------------------------------------------------ helpers
    def sample_rate(self, dec):
        """Sample rate (samples/s) for a given decimation."""
        return self.ADC_RATE / dec

    def time_axis(self, dec):
        """Time axis (s) of the acquired samples."""
        return np.arange(self.BUFFER) / self.sample_rate(dec)

    # ------------------------------------------------------------ generic access
    def send(self, cmd):
        """Send a raw SCPI command (no reply)."""
        self._rp.tx_txt(cmd)

    def query(self, cmd):
        """Send a SCPI command and return the text reply."""
        return self._rp.txrx_txt(cmd)

    def close(self):
        """Close the connection."""
        if self._rp:
            self._rp.close()
