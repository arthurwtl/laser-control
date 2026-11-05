"""Interactive CLI to control the DLC pro laser.

Usage:
    uv run python cli.py
    uv run python cli.py 192.168.55.1
"""
import sys
import readline  # flèches haut/bas pour naviguer dans l'historique (Linux/macOS)

from laser import Laser

HOST = "192.168.55.1"

COMMANDS = {}


def command(*names):
    """Decorator: registers a function under one or more names."""
    def decorator(fn):
        for name in names:
            COMMANDS[name] = fn
        return fn
    return decorator


# ---------------------------------------------------------------- commands

@command("on")
def _on(laser, args):
    "on : turns on laser emission"
    laser.on()
    print("emission ON")


@command("off")
def _off(laser, args):
    "off : turns off laser emission"
    laser.off()
    print("emission OFF")


def _s(laser, param):
    """Safe read: returns the value, or 'n/a' if unavailable."""
    try:
        return laser.get(param)
    except Exception:
        return "n/a"


@command("status", "st")
def _status(laser, args):
    "status : states (emission/lock/scan) + setpoints and values"
    print("emission :", "ON" if laser.is_on else "OFF")
    print("lock     :", "ON" if _s(laser, 'laser1:dl:lock:lock-enabled') is True else "OFF")
    print("temperature: setpoint", laser.get('laser1:dl:tc:temp-set'), "°C | actual", laser.get_temperature(), "°C")
    print()
    print("current    : setpoint", laser.get('laser1:dl:cc:current-set'), "mA | actual", laser.get_current(), "mA")
    print()
    print("scan:")
    print("  state    :", "ON" if laser.get('laser1:scan:enabled') else "OFF")
    print("  amplitude:", laser.get('laser1:scan:amplitude'), "V")
    print("  offset   :", laser.get('laser1:scan:offset'), "V")
    print("  actual   :", laser.get_offset(), "V")


@command("info")
def _info(laser, args):
    "info : software/hardware info and technical parameters"
    print("serial        :", laser.serial)
    print("firmware      :", laser.firmware)
    print("label         :", laser.label)
    print("type          :", _s(laser, 'laser1:type'))
    print("health        :", laser.health)
    print("interlock     :", "OPEN" if laser.interlock_open else "closed")
    print("emission time :", _s(laser, 'laser1:dl:ontime-txt'))
    print()
    print("current:")
    print("  limit (clip):", _s(laser, 'laser1:dl:cc:current-clip'), "mA")
    print("  max limit   :", _s(laser, 'laser1:dl:cc:current-clip-limit'), "mA")
    print("  max rate    :", _s(laser, 'laser1:dl:cc:output-filter:slew-rate'), "mA/s")
    print("piezo:")
    print("  range       :", _s(laser, 'laser1:dl:pc:voltage-min'), "to", _s(laser, 'laser1:dl:pc:voltage-max'), "V")
    print("  max rate    :", _s(laser, 'laser1:dl:pc:output-filter:slew-rate'), "V/s")
    print("temperature:")
    print("  max rate    :", _s(laser, 'laser1:dl:tc:temp-roc-limit'), "°C/s")


SETTERS = {
    "current": ("mA", lambda laser, v: laser.set_current(v)),
    "temp":    ("°C", lambda laser, v: laser.set_temperature(v)),
    "offset":  ("V",  lambda laser, v: laser.set_offset(v)),
    "amp":     ("V",  lambda laser, v: laser.set('laser1:scan:amplitude', v)),
    "freq":    ("Hz", lambda laser, v: laser.set('laser1:scan:frequency', v)),
}


@command("set")
def _set(laser, args):
    "set current|temp|offset|amp|freq <value>"
    if len(args) < 2:
        print("usage: set", "/".join(SETTERS), "<value>")
        return
    what, value = args[0], float(args[1])
    if what not in SETTERS:
        print("unknown:", what, "— choices:", ", ".join(SETTERS))
        return
    unit, setter = SETTERS[what]
    setter(laser, value)
    print(f"set {what} = {value} {unit}")


@command("scan")
def _scan(laser, args):
    "scan on|off : starts/stops the scan"
    if not args or args[0] not in ("on", "off"):
        print("usage: scan on|off")
        return
    if args[0] == "on":
        laser.set('laser1:scan:enabled', True)
        print("scan ON")
    else:
        laser.scan_off()
        print("scan OFF")


@command("lock")
def _lock(laser, args):
    "lock on|off : frequency lock (license required)"
    if not args or args[0] not in ("on", "off"):
        print("usage: lock on|off")
        return
    if args[0] == "on":
        laser.lock_on()
        print("lock ON")
    else:
        laser.lock_off()
        print("lock OFF")


@command("save")
def _save(laser, args):
    "save : saves the configuration"
    laser.save()
    print("configuration saved")


@command("shutdown")
def _shutdown(laser, args):
    "shutdown : turns off emission and sets current to 0"
    laser.shutdown()
    print("laser turned off")


@command("get")
def _get(laser, args):
    "get <param> : reads a parameter (e.g. get laser1:dl:cc:current-set)"
    if not args:
        print("usage: get <param>")
        return
    print(laser.get(args[0]))


@command("exec")
def _exec(laser, args):
    "exec <command> : executes a command (e.g. exec laser1:save)"
    if not args:
        print("usage: exec <command>")
        return
    print(laser.exec(" ".join(args)))


@command("help", "?")
def _help(laser, args):
    "help : lists commands"
    seen = set()
    for name in sorted(COMMANDS):
        fn = COMMANDS[name]
        if fn in seen:
            continue
        seen.add(fn)
        print("  " + fn.__doc__)


# ------------------------------------------------------------------ loop

def repl(laser):
    while True:
        try:
            line = input("==== LASER ===> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        name, *args = line.split()
        if name in ("quit", "exit", "q"):
            break
        handler = COMMANDS.get(name)
        if handler is None:
            print(f"unknown command: {name} — type 'help'")
            continue
        try:
            handler(laser, args)
        except Exception as exc:
            print(f"Error: {exc}")


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else HOST
    with Laser(host=host) as laser:
        print(f"Connected to {host} — serial {laser.serial}.")
        print("Type 'help' for the list of commands.")
        repl(laser)


if __name__ == "__main__":
    main()
