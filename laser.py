"""Ready-to-use class to control the TOPTICA DLC pro laser.

Wraps the low-level `Client` API of the `toptica-lasersdk` SDK
with simple, readable methods.
"""
import time

from toptica.lasersdk.client import Client, NetworkConnection, SerialConnection


class Laser:
    """TOPTICA DLC pro controller.

    Usage:
        laser = Laser(host='192.168.1.100')   # Ethernet
        with laser:
            print(laser.serial)
    """

    def __init__(self, host=None, port=None):
        """host : IP / DNS / serial number (Ethernet). port : 'COM3' or '/dev/ttyACM0' (USB)."""
        if host is not None:
            self._conn = NetworkConnection(host)
        elif port is not None:
            self._conn = SerialConnection(port)
        else:
            raise ValueError("Provide host= (Ethernet) or port= (USB)")
        self._c = None

    # ------------------------------------------------------------------ connection
    def __enter__(self):
        """Open the connection (called by the `with` block)."""
        self._c = Client(self._conn)
        self._c.open()
        return self

    def __exit__(self, *exc):
        """Close the connection (called automatically on `with` exit)."""
        self._c.close()

    # --------------------------------------------------------------------- info
    @property
    def serial(self):
        """Controller serial number."""
        return self._c.get('serial-number')

    @property
    def firmware(self):
        """Controller firmware version."""
        return self._c.get('fw-ver')

    @property
    def label(self):
        """Laser label/name."""
        return self._c.get('laser1:label')

    @property
    def health(self):
        """Global health status (text)."""
        return self._c.get('system-health-txt')

    @property
    def interlock_open(self):
        """True = interlock OPEN = laser is blocked and cannot turn on."""
        return self._c.get('interlock-open')

    # ------------------------------------------------------------------ emission
    def on(self):
        """Turn on laser emission (the current setpoint flows into the diode).

        Note: light is emitted only if the interlock is closed, the key is ON,
        and the front-panel Emission button is pressed.
        """
        self.set('laser1:dl:cc:enabled', True)

    def off(self):
        """Turn off laser emission."""
        self.set('laser1:dl:cc:enabled', False)

    @property
    def is_on(self):
        """True if emission is active (read-only status)."""
        return self._c.get('laser1:emission')

    # ------------------------------------------------------------------- current
    def set_current(self, mA):
        """Set the diode current setpoint (mA)."""
        self.set('laser1:dl:cc:current-set', float(mA))  # mA

    def get_current(self):
        """Measured diode current (mA)."""
        return self._c.get('laser1:dl:cc:current-act')  # mA

    def set_current_limit(self, mA):
        """Set the current safety limit (clip), in mA."""
        self.set('laser1:dl:cc:current-clip', float(mA))  # mA

    # -------------------------------------------------------------- temperature
    def set_temperature(self, degC):
        """Set the temperature setpoint (°C)."""
        self.set('laser1:dl:tc:temp-set', float(degC))  # °C

    def get_temperature(self):
        """Measured temperature (°C)."""
        return self._c.get('laser1:dl:tc:temp-act')  # °C

    def wait_temperature(self, timeout=120):
        """Block until temperature is stable (True) or timeout (False).

        timeout : seconds.
        """
        t0 = time.time()
        while time.time() - t0 < timeout:
            if self._c.get('laser1:dl:tc:ready'):
                return True
            time.sleep(1)
        return False

    # --------------------------------------------------------------------- piezo
    def set_offset(self, volts):
        """Set the piezo voltage (V)."""
        self.set('laser1:dl:pc:voltage-set', float(volts))  # V

    def get_offset(self):
        """Measured piezo voltage (V)."""
        return self._c.get('laser1:dl:pc:voltage-act')  # V

    # ---------------------------------------------------------------------- scan
    def scan(self, frequency=10, amplitude=10, offset=0, enable=True):
        """Configure and start/stop a scan.

        frequency : Hz. amplitude/offset : in the output channel unit
        (V for piezo, mA for current — see laser1:scan:output-channel).
        """
        self.set('laser1:scan:frequency', float(frequency))
        self.set('laser1:scan:amplitude', float(amplitude))
        self.set('laser1:scan:offset', float(offset))
        self.set('laser1:scan:enabled', enable)

    def scan_off(self):
        """Stop the scan."""
        self.set('laser1:scan:enabled', False)

    def set_scan_output(self, channel):
        """Route the scan to an output channel.
        50 = piezo, 51 = current, 20 = Out A, 21 = Out B.
        """
        self.set('laser1:scan:output-channel', int(channel))

    # --------------------------------------------------------------------- lock
    def lock_on(self):
        """Enable the frequency lock (Lock license required)."""
        self.set('laser1:dl:lock:lock-enabled', True)

    def lock_off(self):
        """Disable the lock."""
        self.set('laser1:dl:lock:lock-enabled', False)

    @property
    def lock_state(self):
        """Textual lock state."""
        return self._c.get('laser1:dl:lock:state-txt')

    # --------------------------------------------------------------- persistence
    def save(self):
        """Save current parameters (survive reboot)."""
        self._c.exec('laser1:save')

    def load(self):
        """Reload saved parameters."""
        self._c.exec('laser1:load')

    # ------------------------------------------------------------------- safety
    def shutdown(self):
        """Turn off emission, then set the current to 0."""
        self.off()
        self.set_current(0)

    # ------------------------------------------------------------ generic access
    def get(self, name):
        """Read any parameter from the Command Reference."""
        return self._c.get(name)

    def set(self, name, value):
        """Writes a parameter; prints a short explanation on error."""
        try:
            code = self._c.set(name, value)
            if code == 2:
                print(f"⚠️  {name} : value clipped (out of range, clamped to min/max).")
            return code
        except Exception as exc:
            print(f"❌  {name} : {self._expliquer(exc)}")
            return None

    def _expliquer(self, exc):
        """Translates a controller error into a short explanation."""
        msg = str(exc)
        if '-11' in msg:
            return "read-only parameter (not settable). See Command Reference §2.3."
        if '-3' in msg:
            return "no such parameter (wrong name or not on this model). See Command Reference §2.3."
        if '-1' in msg:
            return "invalid argument (wrong type or value). See Command Reference §2.3."
        return msg

    def exec(self, name, **kwargs):
        """Execute any command from the Command Reference."""
        return self._c.exec(name, **kwargs)
