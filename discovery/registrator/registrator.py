import http.client
import json
import os
import socket
import time
import urllib.parse
import urllib.request


DOCKER_SOCKET = os.getenv("DOCKER_SOCKET", "/var/run/docker.sock")
CONSUL_HTTP_ADDR = os.getenv("CONSUL_HTTP_ADDR", "http://discovery:8500")
DOCKER_NETWORK = os.getenv("DOCKER_NETWORK", "projeto-redes2-net")
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "5"))


class UnixHTTPConnection(http.client.HTTPConnection):
    def __init__(self, socket_path):
        super().__init__("docker")
        self.socket_path = socket_path

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.socket_path)


def docker_get(path):
    conn = UnixHTTPConnection(DOCKER_SOCKET)
    conn.request("GET", path)
    response = conn.getresponse()
    body = response.read()
    conn.close()

    if response.status >= 400:
        raise RuntimeError(f"Docker API error {response.status}: {body.decode()}")

    return json.loads(body.decode())


def consul_put(path, payload):
    url = urllib.parse.urljoin(CONSUL_HTTP_ADDR, path)
    data = json.dumps(payload).encode()
    request = urllib.request.Request(
        url,
        data=data,
        method="PUT",
        headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(request, timeout=5) as response:
        response.read()


def parse_env(env_list):
    env = {}
    for item in env_list or []:
        key, _, value = item.partition("=")
        env[key] = value
    return env


def service_tags(raw_tags):
    if not raw_tags:
        return []
    return [tag.strip() for tag in raw_tags.split(",") if tag.strip()]


def discover_services():
    services = {}
    containers = docker_get("/containers/json")

    for container in containers:
        container_id = container["Id"]
        details = docker_get(f"/containers/{container_id}/json")
        env = parse_env(details.get("Config", {}).get("Env", []))

        if env.get("SERVICE_IGNORE", "").lower() == "true":
            continue

        service_name = env.get("SERVICE_NAME")
        if not service_name:
            continue

        networks = details.get("NetworkSettings", {}).get("Networks", {})
        network = networks.get(DOCKER_NETWORK)
        if not network:
            continue

        ip_address = network.get("IPAddress")
        if not ip_address:
            continue

        exposed_ports = details.get("Config", {}).get("ExposedPorts", {})
        port = int(env.get("SERVICE_PORT", "80"))
        if not env.get("SERVICE_PORT") and exposed_ports:
            first_port = next(iter(exposed_ports.keys()))
            port = int(first_port.split("/")[0])

        container_name = details.get("Name", "").lstrip("/")
        service_id = f"{service_name}-{container_id[:12]}"
        services[service_id] = {
            "ID": service_id,
            "Name": service_name,
            "Address": ip_address,
            "Port": port,
            "Tags": service_tags(env.get("SERVICE_TAGS")),
            "Meta": {
                "container": container_name,
                "project": "projeto-redes2",
            },
        }

    return services


def sync_loop():
    registered = set()

    while True:
        try:
            services = discover_services()

            for service_id, service in services.items():
                consul_put("/v1/agent/service/register", service)
                registered.add(service_id)
                print(
                    f"registered {service['Name']} at {service['Address']}:{service['Port']}",
                    flush=True,
                )

            stale_services = registered - set(services.keys())
            for service_id in stale_services:
                consul_put(f"/v1/agent/service/deregister/{service_id}", {})
                registered.remove(service_id)
                print(f"deregistered {service_id}", flush=True)

        except Exception as exc:
            print(f"registrator error: {exc}", flush=True)

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    sync_loop()
