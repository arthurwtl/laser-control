"""Classe prête à l'emploi pour contrôler le laser TOPTICA DLC pro.

Elle enveloppe l'API bas niveau (`Client`) du SDK `toptica-lasersdk`
et expose des méthodes simples et lisibles.
"""
import time

from toptica.lasersdk.client import Client, NetworkConnection, SerialConnection


class Laser:
    """Contrôleur TOPTICA DLC pro.

    Utilisation :
        laser = Laser(host='192.168.1.100')   # Ethernet
        with laser:
            print(laser.serial)
    """

    def __init__(self, host=None, port=None):
        """host : IP / nom DNS / n° de série (Ethernet). port : 'COM3' ou '/dev/ttyACM0' (USB)."""
        if host is not None:
            self._conn = NetworkConnection(host)
        elif port is not None:
            self._conn = SerialConnection(port)
        else:
            raise ValueError("Fournir host= (Ethernet) ou port= (USB)")
        self._c = None

    # ------------------------------------------------------------------ connexion
    def __enter__(self):
        """Ouvre la connexion au laser (appelé par le bloc `with`)."""
        self._c = Client(self._conn)
        self._c.open()
        return self

    def __exit__(self, *exc):
        """Ferme la connexion (appelé automatiquement à la sortie du `with`)."""
        self._c.close()

    # ------------------------------------------------------------- informations
    @property
    def serial(self):
        """N° de série du contrôleur."""
        return self._c.get('serial-number')

    @property
    def firmware(self):
        """Version du firmware du contrôleur."""
        return self._c.get('fw-ver')

    @property
    def label(self):
        """Nom/label du laser."""
        return self._c.get('laser1:label')

    @property
    def health(self):
        """État de santé global (texte)."""
        return self._c.get('system-health-txt')

    @property
    def interlock_open(self):
        """True = interlock OUVERT = le laser est bloqué et ne s'allumera pas."""
        return self._c.get('interlock-open')

    # ----------------------------------------------------------------- émission
    def on(self):
        """Active l'émission laser (le courant de consigne circule dans la diode).

        NB : la lumière ne sort que si interlock fermé, clé sur ON et bouton
        Émission de la façade enfoncé.
        """
        self.set('laser1:dl:cc:enabled', True)

    def off(self):
        """Coupe l'émission laser (la diode ne reçoit plus de courant)."""
        self.set('laser1:dl:cc:enabled', False)

    @property
    def is_on(self):
        """True si l'émission est active (statut réel, lecture seule)."""
        return self._c.get('laser1:emission')

    # ------------------------------------------------------------------- courant
    def set_current(self, mA):
        """Fixe la consigne de courant diode (mA)."""
        self.set('laser1:dl:cc:current-set', float(mA))  # mA

    def get_current(self):
        """Courant réellement mesuré dans la diode (mA)."""
        return self._c.get('laser1:dl:cc:current-act')  # mA

    def set_current_limit(self, mA):
        """Fixe la limite de sécurité (clip) du courant (mA)."""
        self.set('laser1:dl:cc:current-clip', float(mA))  # mA

    # -------------------------------------------------------------- température
    def set_temperature(self, degC):
        """Fixe la consigne de température (°C)."""
        self.set('laser1:dl:tc:temp-set', float(degC))  # °C

    def get_temperature(self):
        """Température réelle (°C)."""
        return self._c.get('laser1:dl:tc:temp-act')  # °C

    def wait_temperature(self, timeout=120):
        """Bloque jusqu'à stabilisation de la température (True) ou timeout (False).

        timeout : secondes.
        """
        t0 = time.time()
        while time.time() - t0 < timeout:
            if self._c.get('laser1:dl:tc:ready'):
                return True
            time.sleep(1)
        return False

    # --------------------------------------------------------------------- piezo
    def set_piezo(self, volts):
        """Fixe la tension piezo (V)."""
        self.set('laser1:dl:pc:voltage-set', float(volts))  # V

    def get_piezo(self):
        """Tension piezo réelle (V)."""
        return self._c.get('laser1:dl:pc:voltage-act')  # V

    # ---------------------------------------------------------------------- scan
    def scan(self, frequency=10, amplitude=10, offset=0, enable=True):
        """Configure et démarre/arrête un scan.

        frequency : Hz. amplitude/offset : dans l'unité de la voie de sortie
        (V si piezo, mA si courant — selon laser1:scan:output-channel).
        """
        self.set('laser1:scan:frequency', float(frequency))
        self.set('laser1:scan:amplitude', float(amplitude))
        self.set('laser1:scan:offset', float(offset))
        self.set('laser1:scan:enabled', enable)

    def scan_off(self):
        """Arrête le scan."""
        self.set('laser1:scan:enabled', False)

    # ------------------------------------------------------- verrouillage (lock)
    def lock_on(self):
        """Active la boucle de verrouillage de fréquence (licence Lock requise)."""
        self.set('laser1:dl:lock:lock-enabled', True)

    def lock_off(self):
        """Désactive le verrouillage."""
        self.set('laser1:dl:lock:lock-enabled', False)

    @property
    def lock_state(self):
        """État textuel du verrouillage."""
        return self._c.get('laser1:dl:lock:state-txt')

    # --------------------------------------------------------------- persistance
    def save(self):
        """Sauvegarde les paramètres courants (survivent au redémarrage)."""
        self._c.exec('laser1:save')

    def load(self):
        """Recharge les paramètres sauvegardés."""
        self._c.exec('laser1:load')

    # ------------------------------------------------------------------- sécurité
    def shutdown(self):
        """Coupe l'émission, puis ramène la consigne de courant à 0."""
        self.off()
        self.set_current(0)

    # ------------------------------------------------------------ accès générique
    def get(self, name):
        """Lit n'importe quel paramètre de la Command Reference."""
        return self._c.get(name)

    def set(self, name, value):
        """Écrit un paramètre ; en cas d'erreur, affiche une explication courte."""
        try:
            code = self._c.set(name, value)
            if code == 2:
                print(f"⚠️  {name} : valeur écrêtée (hors limites, ramenée au min/max).")
            return code
        except Exception as exc:
            print(f"❌  {name} : {self._expliquer(exc)}")
            return None

    def _expliquer(self, exc):
        """Traduit une erreur du contrôleur en explication courte."""
        msg = str(exc)
        if '-11' in msg:
            return "paramètre en lecture seule (non modifiable). Cf. Command Reference §2.3."
        if '-3' in msg:
            return "paramètre inexistant (nom incorrect ou absent de ce modèle). Cf. Command Reference §2.3."
        if '-1' in msg:
            return "argument invalide (type ou valeur incorrect). Cf. Command Reference §2.3."
        return msg

    def exec(self, name, **kwargs):
        """Exécute n'importe quelle commande de la Command Reference."""
        return self._c.exec(name, **kwargs)
