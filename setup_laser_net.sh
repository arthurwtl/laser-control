#!/usr/bin/env bash
# Assign IP 192.168.55.2 to the laser interface (laser is at 192.168.55.1).
set -e

IFACE="enp3s0f4u1"
IP="192.168.55.2/24"

sudo ip link set "$IFACE" up
sudo ip addr flush dev "$IFACE"
sudo ip addr add "$IP" dev "$IFACE"

echo "OK : $IFACE -> $IP"
ip addr show "$IFACE" | grep -E 'inet |state'
