FROM nginx:1.27-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends avahi-daemon avahi-utils dbus libnss-mdns \
    && rm -rf /var/lib/apt/lists/*

COPY nginx.conf /etc/nginx/nginx.conf
COPY entrypoint.sh /usr/local/bin/mdns-entrypoint.sh

RUN chmod +x /usr/local/bin/mdns-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/mdns-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
