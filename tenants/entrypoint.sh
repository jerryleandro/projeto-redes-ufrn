#!/bin/sh
set -eu

mkdir -p /run/dbus
dbus-daemon --system --fork
avahi-daemon --daemonize --no-chroot

exec /docker-entrypoint.sh "$@"
