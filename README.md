# Projeto Redes 2

Projeto academico da disciplina Redes 2 demonstrando uma arquitetura local com Docker Compose, service discovery dinamico, reverse proxy e dois tenants.

## Estrutura

```text
.
├── gateway/
│   └── traefik.yml
├── discovery/
│   └── registrator/
│       ├── Dockerfile
│       └── registrator.py
├── tenants/
│   ├── Dockerfile
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
| `discovery` | `projeto-redes2-discovery` | Consul: catalogo dinamico de servicos |
| `registrator` | `projeto-redes2-registrator` | Observa a API do Docker e registra containers no Consul |
| `gateway` | `projeto-redes2-gateway` | Traefik: reverse proxy dinamico |
| `tenant1` | `projeto-redes2-tenant1` | Aplicacao do tenant 1 |
| `tenant2` | `projeto-redes2-tenant2` | Aplicacao do tenant 2 |

## Fluxo

1. O container `tenant1` ou `tenant2` sobe.
2. O `registrator` observa o evento do Docker e registra o servico no Consul.
3. O Traefik consulta o catalogo do Consul e cria as rotas HTTP dinamicamente.
4. O navegador acessa `tenant1.localhost` ou `tenant2.localhost`.
5. A requisicao chega ao gateway Traefik na porta `80`.
6. O Traefik le o cabecalho `Host` e encaminha para o tenant registrado no Consul.

Esta arquitetura usa service discovery, que e a alternativa mais adequada para Docker em ambiente local. Em vez de manter um arquivo DNS estatico, os containers sao registrados quando iniciam e removidos quando param.

O dominio `*.localhost` e usado para teste no navegador porque resolve para `127.0.0.1` sem alterar o arquivo `hosts` do Windows. As regras tambem aceitam `tenant1.redes2.local` e `tenant2.redes2.local`, mas esses nomes ainda exigiriam que o sistema operacional soubesse resolver o dominio ate o gateway.

## Como subir

```bash
docker compose up -d --build
```

Verifique os containers:

```bash
docker compose ps
```

## Como configurar o DNS local

Nao e necessario alterar o arquivo `hosts` para testar no navegador. Use:

```text
http://tenant1.localhost
http://tenant2.localhost
```

O Consul tambem expoe DNS interno para laboratorio na porta `8600/udp`. Exemplo:

```bash
dig @127.0.0.1 -p 8600 tenant1.service.consul
dig @127.0.0.1 -p 8600 tenant2.service.consul
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

Interface do Consul:

```text
http://localhost:8500
```

Dashboard do Traefik:

```text
http://localhost:8080
```

## Encerrar ambiente

```bash
docker compose down
```
