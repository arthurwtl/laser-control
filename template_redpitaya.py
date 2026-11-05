import sys

import redpitaya_scpi as scpi

HOST = "169.254.140.238"
PORT = 5000


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else HOST

    with scpi.scpi(host, port=PORT) as rp:
        rp.tx_txt('*IDN?')
        print("Connected:", rp.rx_txt())

        # coder ici


if __name__ == "__main__":
    main()
