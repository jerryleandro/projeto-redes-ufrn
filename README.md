# Projeto Redes 2 - etapa mDNS

Projeto academico da disciplina Redes 2 demonstrando resolucao de nomes via mDNS entre containers Docker, reverse proxy Nginx e dois tenants.

## Estrutura

```text
.
├── gateway/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── nginx.conf
│   └── traefik.yml (legado, nao utilizado nesta etapa)
├── discovery/
│   └── registrator/
│       ├── Dockerfile
│       └── registrator.py
├── tenants/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── nginx/
│   │   └── default.conf
│   ├── tenant1/
│   │   └── index.html
│   └── tenant2/
│       └── index.html
└── docker-compose.yml
```

## Servicos

| Servico | Container | Funcao |
| --- | --- | --- |
| `gateway` | `projeto-redes2-gateway` | Nginx: resolve os nomes mDNS e encaminha requisicoes |
| `tenant1` | `projeto-redes2-tenant1` | Nginx que anuncia `tenant1.local` via Avahi |
| `tenant2` | `projeto-redes2-tenant2` | Nginx que anuncia `tenant2.local` via Avahi |

Os servicos `discovery` (Consul) e `registrator` pertencem a uma implementacao anterior e foram mantidos no perfil opcional `consul-legado`. Eles nao participam da etapa mDNS nem sobem no comando padrao.

## Fluxo

1. Cada tenant inicia D-Bus e `avahi-daemon` com seu hostname definido no Compose.
2. Avahi anuncia `tenant1.local` ou `tenant2.local` e o IP privado na rede bridge.
3. O gateway inicia Avahi e usa `libnss-mdns` para resolver os nomes `.local`.
4. Depois da resolucao, o Nginx do gateway inicia seus upstreams usando `tenant1.local:80` e `tenant2.local:80`.
5. O cliente envia a requisicao para a porta `80` do host usando `tenant1.localhost` ou `tenant2.localhost`.

O dominio `*.localhost` serve apenas para chegar ao gateway pelo host. Os nomes mDNS `.local` sao usados internamente pelo gateway para chegar aos tenants.

## Como subir

```bash
docker compose up -d --build
```

Verifique os containers:

```bash
docker compose ps
```

## Como observar o mDNS

O host nao precisa resolver os nomes mDNS para testar o proxy. Para consultar os anuncios a partir do gateway:

```bash
docker compose exec gateway avahi-resolve-host-name -4 tenant1.local
docker compose exec gateway avahi-resolve-host-name -4 tenant2.local
docker compose exec gateway getent ahostsv4 tenant1.local tenant2.local
```

Para comparar o IP anunciado com o IP privado de cada tenant:

```bash
docker compose exec tenant1 hostname -i
docker compose exec tenant2 hostname -i
```

## Como testar

Acesse:

```text
http://tenant1.localhost
http://tenant2.localhost
```

Tambem e possivel testar o gateway por cabecalho:

```bash
curl -H "Host: tenant1.localhost" http://127.0.0.1
curl -H "Host: tenant2.localhost" http://127.0.0.1
```

O Nginx resolve os upstreams quando inicia. Se um tenant for recriado e receber outro IP, reinicie o gateway para que ele resolva novamente: `docker compose restart gateway`.

## Limitacoes

mDNS funciona bem como demonstracao local em uma unica rede bridge com multicast disponivel. Ele nao fornece um catalogo central, nao e adequado para descoberta entre hosts Docker diferentes e o Nginx aberto nao atualiza automaticamente IPs mDNS de upstreams ja carregados. Para registro dinamico e resolucao DNS mais controlada, a proxima etapa deve avaliar um servidor DNS dedicado.

## Encerrar ambiente

```bash
docker compose down
```
