"""Classe prête à l'emploi pour piloter la carte Red Pitaya (acquisition SCPI).

Elle enveloppe la bibliothèque `redpitaya_scpi` et masque les commandes SCPI brutes.
"""
import time

import numpy as np
import redpitaya_scpi as scpi


class RedPitaya:
    """Carte d'acquisition Red Pitaya STEMlab 125-14.

    Utilisation :
        rp = RedPitaya('169.254.140.238')
        with rp:
            print(rp.info)
            v = rp.acquire(dec=65536)
    """

    ADC_RATE = 125e6    # STEMlab 125-14 : 125 MS/s
    BUFFER = 16384      # taille du buffer d'acquisition (échantillons)

    def __init__(self, host, port=5000):
        self._host = host
        self._port = port
        self._rp = None

    # ------------------------------------------------------------------ connexion
    def __enter__(self):
        self._rp = scpi.scpi(self._host, port=self._port)
        return self

    def __exit__(self, *exc):
        if self._rp:
            self._rp.close()

    # -------------------------------------------------------------------- infos
    @property
    def info(self):
        """Identification de la carte (*IDN?)."""
        return self._rp.txrx_txt('*IDN?')

    # -------------------------------------------------------------- acquisition
    def acquire(self, channel=1, dec=1):
        """Acquiert les 16384 échantillons du canal (1 ou 2) → np.ndarray en volts.

        dec : décimation (puissances de 2 : 1, 2, 4, ..., 65536).
              taux = ADC_RATE / dec, durée = BUFFER / taux.
        """
        rp = self._rp
        rp.tx_txt('ACQ:RST')
        rp.tx_txt(f'ACQ:DEC {dec}')
        rp.tx_txt('ACQ:START')
        # attendre un buffer complet de données fraîches avant de déclencher,
        # sinon les premières valeurs peuvent être périmées (cf. doc Red Pitaya)
        time.sleep(self.BUFFER / self.sample_rate(dec))
        rp.tx_txt('ACQ:TRIG NOW')
        while True:
            rp.tx_txt('ACQ:TRIG:FILL?')
            if rp.rx_txt() == '1':
                break
        rp.tx_txt(f'ACQ:SOUR{channel}:DATA?')
        s = rp.rx_txt()
        return np.array([float(x) for x in s.strip('{}\n\r').split(',')])

    def intensity(self, channel=1, dec=65536, n=10):
        """Intensité moyenne (V) sur n acquisitions → (moyenne, écart-type)."""
        vals = [self.acquire(channel, dec).mean() for _ in range(n)]
        return float(np.mean(vals)), float(np.std(vals))

    # ------------------------------------------------------------------ helpers
    def sample_rate(self, dec):
        """Taux d'échantillonnage (éch./s) pour une décimation donnée."""
        return self.ADC_RATE / dec

    def time_axis(self, dec):
        """Axe des temps (s) correspondant aux échantillons acquis."""
        return np.arange(self.BUFFER) / self.sample_rate(dec)

    # ------------------------------------------------------------ accès générique
    def send(self, cmd):
        """Envoie une commande SCPI brute (pas de réponse)."""
        self._rp.tx_txt(cmd)

    def query(self, cmd):
        """Envoie une commande SCPI et renvoie la réponse texte."""
        return self._rp.txrx_txt(cmd)

    def close(self):
        """Ferme la connexion."""
        if self._rp:
            self._rp.close()
