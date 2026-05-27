#!/bin/sh
set -eu

mkdir -p /run/dbus
dbus-daemon --system --fork
avahi-daemon --daemonize --no-chroot

for backend in tenant1.local tenant2.local; do
    attempts=0
    until getent ahostsv4 "$backend" >/dev/null 2>&1; do
        attempts=$((attempts + 1))
        if [ "$attempts" -ge 30 ]; then
            echo "Nao foi possivel resolver $backend via mDNS." >&2
            exit 1
        fi
        sleep 1
    done
done

exec /docker-entrypoint.sh "$@"
